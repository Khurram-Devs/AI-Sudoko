import tkinter as tk
import random
import time
import json
import os

LEADERBOARD_FILE = "leaderboard.json"


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


def load_leaderboard():
    if not os.path.exists(LEADERBOARD_FILE):
        return []
    with open(LEADERBOARD_FILE, "r") as f:
        return json.load(f)


def save_leaderboard(data):
    with open(LEADERBOARD_FILE, "w") as f:
        json.dump(data, f, indent=2)


class SudokuApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sudoku Trainer")
        self.root.configure(bg="#1e1e1e")

        self.mode = None
        self.grid = None
        self.solution = None
        self.selected = None
        self.mistakes = 0
        self.start_time = None
        self.timer_label = None
        self.mistake_label = None
        self.canvas = None
        self.cells = {}

        self.show_start_screen()

    def show_start_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        frame = tk.Frame(self.root, bg="#1e1e1e")
        frame.pack(expand=True, fill="both")

        title = tk.Label(
            frame,
            text="Sudoku Trainer",
            font=("Consolas", 24, "bold"),
            fg="white",
            bg="#1e1e1e",
        )
        title.pack(pady=30)

        modes = [("Easy", 0.4), ("Medium", 0.6), ("Hard", 0.8)]
        for name, hide_ratio in modes:
            btn = tk.Button(
                frame,
                text=name,
                font=("Consolas", 16),
                bg="#2e2e2e",
                fg="white",
                activebackground="#444",
                activeforeground="white",
                width=10,
                command=lambda h=hide_ratio: self.start_game(h),
            )
            btn.pack(pady=10)

        leaderboard_btn = tk.Button(
            frame,
            text="Leaderboard",
            font=("Consolas", 16),
            bg="#444444",
            fg="white",
            width=12,
            command=self.show_leaderboard,
        )
        leaderboard_btn.pack(pady=20)

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
            self.root, width=9 * 40, height=9 * 40, bg="#1e1e1e", highlightthickness=0
        )
        self.canvas.pack(padx=20, pady=20)

        self.cells = {}
        for r in range(9):
            for c in range(9):
                x1, y1 = c * 40, r * 40
                x2, y2 = x1 + 40, y1 + 40
                rect = self.canvas.create_rectangle(
                    x1, y1, x2, y2, fill="#2e2e2e", outline="#555", width=1
                )
                val = self.grid[r][c]
                text = self.canvas.create_text(
                    x1 + 20,
                    y1 + 20,
                    text=str(val) if val != 0 else "",
                    fill="#00ff88" if val != 0 else "#ddd",
                    font=("Consolas", 14, "bold"),
                )
                self.cells[(r, c)] = {
                    "rect": rect,
                    "text": text,
                    "value": self.solution[r][c],
                    "locked": val != 0,
                }

        for i in range(10):
            w = 2 if i % 3 == 0 else 1
            self.canvas.create_line(0, i * 40, 9 * 40, i * 40, fill="#888", width=w)
            self.canvas.create_line(i * 40, 0, i * 40, 9 * 40, fill="#888", width=w)

        self.canvas.bind("<Button-1>", self.on_click)
        self.root.bind("<Key>", self.on_key)

        self.start_time = time.time()
        self.update_timer()

    def on_click(self, event):
        c = event.x // 40
        r = event.y // 40
        if (r, c) in self.cells:
            if self.selected:
                self.canvas.itemconfig(
                    self.cells[self.selected]["rect"], outline="#555"
                )
            self.selected = (r, c)
            if not self.cells[(r, c)]["locked"]:
                self.canvas.itemconfig(self.cells[(r, c)]["rect"], outline="#00bfff")

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
            self.canvas.itemconfig(cell["rect"], outline="#555")
            if all(c["locked"] for c in self.cells.values()):
                self.game_finished()
        else:
            self.canvas.itemconfig(cell["text"], text=str(val), fill="#ff5555")
            self.mistakes += 1
            self.mistake_label.config(text=f"Mistakes: {self.mistakes}")

    def update_timer(self):
        if self.start_time:
            elapsed = int(time.time() - self.start_time)
            self.timer_label.config(text=f"Time: {elapsed}s")
            self.root.after(1000, self.update_timer)

    def game_finished(self):
        elapsed = int(time.time() - self.start_time)

        popup = tk.Toplevel(self.root)
        popup.title("You Won!")
        popup.configure(bg="#1e1e1e")

        msg = tk.Label(
            popup,
            text=f"Completed!\nTime: {elapsed}s | Mistakes: {self.mistakes}",
            font=("Consolas", 14),
            fg="white",
            bg="#1e1e1e",
        )
        msg.pack(pady=10)

        entry_label = tk.Label(popup, text="Enter your name:", fg="white", bg="#1e1e1e")
        entry_label.pack()
        name_entry = tk.Entry(popup)
        name_entry.pack(pady=5)

        def save_score():
            name = name_entry.get().strip() or "Player"
            leaderboard = load_leaderboard()
            leaderboard.append(
                {"name": name, "time": elapsed, "mistakes": self.mistakes}
            )
            leaderboard.sort(key=lambda x: (x["time"], x["mistakes"]))
            save_leaderboard(leaderboard)
            popup.destroy()
            self.show_leaderboard()

        save_btn = tk.Button(
            popup,
            text="Save",
            font=("Consolas", 12),
            bg="#2e2e2e",
            fg="white",
            command=save_score,
        )
        save_btn.pack(pady=10)

    def show_leaderboard(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        frame = tk.Frame(self.root, bg="#1e1e1e")
        frame.pack(expand=True, fill="both")

        title = tk.Label(
            frame,
            text="Leaderboard",
            font=("Consolas", 20, "bold"),
            fg="white",
            bg="#1e1e1e",
        )
        title.pack(pady=20)

        leaderboard = load_leaderboard()
        for idx, entry in enumerate(leaderboard[:10], start=1):
            lbl = tk.Label(
                frame,
                text=f"{idx}. {entry['name']} - {entry['time']}s - {entry['mistakes']} mistakes",
                font=("Consolas", 14),
                fg="#00ff88",
                bg="#1e1e1e",
            )
            lbl.pack(anchor="w", padx=30)

        back_btn = tk.Button(
            frame,
            text="Back",
            font=("Consolas", 14),
            bg="#2e2e2e",
            fg="white",
            command=self.show_start_screen,
        )
        back_btn.pack(pady=20)


if __name__ == "__main__":
    root = tk.Tk()
    app = SudokuApp(root)
    root.mainloop()
