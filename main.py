import tkinter as tk
import random
import time


def generate_sudoku(n=9):
    g = int(n**0.5)
    grid = [[0 for _ in range(n)] for _ in range(n)]

    def shuffle(arr):
        for i in range(len(arr) - 1, 0, -1):
            j = random.randint(0, i)
            arr[i], arr[j] = arr[j], arr[i]
        return arr

    def safe(r, c, val):
        for x in range(n):
            if grid[r][x] == val or grid[x][c] == val:
                return False
        br, bc = (r // g) * g, (c // g) * g
        for rr in range(g):
            for cc in range(g):
                if grid[br + rr][bc + cc] == val:
                    return False
        return True

    def solve(k=0):
        if k >= n * n:
            return True
        r, c = divmod(k, n)
        nums = shuffle([v for v in range(1, n + 1)])
        for v in nums:
            if safe(r, c, v):
                grid[r][c] = v
                if solve(k + 1):
                    return True
                grid[r][c] = 0
        return False

    solve()
    return grid


class SudokuApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sudoku Trainer")
        self.root.configure(bg="#1e1e1e")
        self.root.geometry("500x550")

        self.grid = None
        self.solution = None
        self.selected = None
        self.mistakes = 0
        self.start_time = None
        self.timer_label = None
        self.mistake_label = None
        self.canvas = None
        self.cells = {}

        self.start_game(0.9)

    def start_game(self, hide_ratio):
        for widget in self.root.winfo_children():
            widget.destroy()

        self.grid = generate_sudoku(9)
        self.solution = [row[:] for row in self.grid]

        total = 81
        to_hide = int(total * hide_ratio)
        hidden = 0
        while hidden < to_hide:
            r, c = random.randint(0, 8), random.randint(0, 8)
            if self.grid[r][c] != 0:
                self.grid[r][c] = 0
                hidden += 1

        top_frame = tk.Frame(self.root, bg="#1e1e1e")
        top_frame.pack(fill="x", pady=10)

        self.timer_label = tk.Label(
            top_frame, text="Time: 0s", font=("Consolas", 14), fg="white", bg="#1e1e1e"
        )
        self.timer_label.pack(side="left", padx=20)

        self.mistake_label = tk.Label(
            top_frame,
            text="Mistakes: 0",
            font=("Consolas", 14),
            fg="white",
            bg="#1e1e1e",
        )
        self.mistake_label.pack(side="right", padx=20)

        self.canvas = tk.Canvas(
            self.root, width=9 * 50, height=9 * 50, bg="#1e1e1e", highlightthickness=0
        )
        self.canvas.pack(padx=20, pady=20)

        self.cells = {}
        for r in range(9):
            for c in range(9):
                x1, y1 = c * 50, r * 50
                x2, y2 = x1 + 50, y1 + 50
                rect = self.canvas.create_rectangle(
                    x1, y1, x2, y2, fill="#2e2e2e", outline="#555", width=1
                )
                val = self.grid[r][c]
                text = self.canvas.create_text(
                    x1 + 25,
                    y1 + 25,
                    text=str(val) if val != 0 else "",
                    fill="#00ff88" if val != 0 else "#ddd",
                    font=("Consolas", 16, "bold"),
                )
                self.cells[(r, c)] = {
                    "rect": rect,
                    "text": text,
                    "value": self.solution[r][c],
                    "locked": val != 0,
                }

        for i in range(10):
            w = 2 if i % 3 == 0 else 1
            self.canvas.create_line(0, i * 50, 9 * 50, i * 50, fill="#888", width=w)
            self.canvas.create_line(i * 50, 0, i * 50, 9 * 50, fill="#888", width=w)

        self.canvas.bind("<Button-1>", self.on_click)
        self.root.bind("<Key>", self.on_key)

        self.start_time = time.time()
        self.mistakes = 0
        self.update_timer()

    def on_click(self, event):
        c = event.x // 50
        r = event.y // 50
        if (r, c) in self.cells:
            if self.selected:
                prev = self.cells[self.selected]
                self.canvas.itemconfig(
                    prev["rect"], fill="#2e2e2e" if not prev["locked"] else "#333"
                )
            self.selected = (r, c)
            if not self.cells[(r, c)]["locked"]:
                self.canvas.itemconfig(self.cells[(r, c)]["rect"], fill="#00bfff")

    def on_key(self, event):
        if not self.selected or not event.char.isdigit():
            return
        val = int(event.char)
        r, c = self.selected
        cell = self.cells[(r, c)]
        if cell["locked"]:
            return
        if val == cell["value"]:
            self.canvas.itemconfig(cell["text"], text=str(val), fill="#00ff88")
            cell["locked"] = True
            self.canvas.itemconfig(cell["rect"], fill="#333")
            if all(c["locked"] for c in self.cells.values()):
                self.end_game()
        else:
            self.canvas.itemconfig(cell["text"], text=str(val), fill="#ff5555")
            self.mistakes += 1
            self.mistake_label.config(text=f"Mistakes: {self.mistakes}")

    def update_timer(self):
        if self.start_time:
            elapsed = int(time.time() - self.start_time)
            self.timer_label.config(text=f"Time: {elapsed}s")
            self.root.after(1000, self.update_timer)

    def end_game(self):
        elapsed = int(time.time() - self.start_time)
        with open("sudoku_stats.txt", "a") as f:
            f.write(f"Time: {elapsed}s, Mistakes: {self.mistakes}\n")
        self.root.after(2000, lambda: self.start_game(0.9))


if __name__ == "__main__":
    root = tk.Tk()
    app = SudokuApp(root)
    root.mainloop()
