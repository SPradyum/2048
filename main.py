"""
enhanced_2048.py

Enhanced 2048 game (single-file). Layout fixes so controls and arrow buttons
sit correctly beneath the board. All features retained:
- Score + Best score (persisted to best_score.json)
- Move counter
- Undo (single-step)
- New Game / Restart
- On-screen arrow buttons (click to move)
- Target tile selector (2048 / 4096)
- Reset best score button
- Simple tile flash animation on merge
"""

import tkinter as tk
from tkinter import messagebox, simpledialog
import random
import json
import os
import time

BEST_SCORE_FILE = "best_score.json"


class Board:
    bg_color = {
        '2': '#eee4da', '4': '#ede0c8', '8': '#edc850', '16': '#edc53f',
        '32': '#f67c5f', '64': '#f65e3b', '128': '#edcf72', '256': '#edcc61',
        '512': '#f2b179', '1024': '#f59563', '2048': '#edc22e', '4096': '#eecb2f',
    }
    fg_color = {
        '2': '#776e65', '4': '#776e65', '8': '#f9f6f2', '16': '#f9f6f2',
        '32': '#f9f6f2', '64': '#f9f6f2', '128': '#f9f6f2', '256': '#f9f6f2',
        '512': '#776e65', '1024': '#f9f6f2', '2048': '#f9f6f2', '4096': '#f9f6f2',
    }

    def __init__(self, master, size=4):
        self.master = master
        self.size = size
        self.game_area_frame = tk.Frame(self.master, bg='#bbada0', padx=8, pady=8)
        self.board = []
        self.gridCell = [[0] * size for _ in range(size)]

        self.compress = False
        self.merge = False
        self.moved = False
        self.score = 0

        # UI labels (matrix of Labels)
        for i in range(size):
            rows = []
            for j in range(size):
                l = tk.Label(self.game_area_frame, text='', bg='#cdc1b4',
                             font=('Helvetica', 24, 'bold'), width=4, height=2, relief='ridge', bd=4)
                l.grid(row=i, column=j, padx=6, pady=6)
                rows.append(l)
            self.board.append(rows)

    def place(self, row, column, pady=(6, 6)):
        self.game_area_frame.grid(row=row, column=column, pady=pady)

    # basic transforms
    def reverse(self):
        for ind in range(self.size):
            i = 0
            j = self.size - 1
            while i < j:
                self.gridCell[ind][i], self.gridCell[ind][j] = self.gridCell[ind][j], self.gridCell[ind][i]
                i += 1
                j -= 1

    def transpose(self):
        self.gridCell = [list(t) for t in zip(*self.gridCell)]

    # compress left
    def compressGrid(self):
        self.compress = False
        temp = [[0] * self.size for _ in range(self.size)]
        for i in range(self.size):
            cnt = 0
            for j in range(self.size):
                if self.gridCell[i][j] != 0:
                    temp[i][cnt] = self.gridCell[i][j]
                    if cnt != j:
                        self.compress = True
                    cnt += 1
        self.gridCell = temp

    def mergeGrid(self):
        self.merge = False
        for i in range(self.size):
            for j in range(self.size - 1):
                if self.gridCell[i][j] == self.gridCell[i][j + 1] and self.gridCell[i][j] != 0:
                    self.gridCell[i][j] *= 2
                    self.gridCell[i][j + 1] = 0
                    self.score += self.gridCell[i][j]
                    self.merge = True

    def random_cell(self):
        cells = []
        for i in range(self.size):
            for j in range(self.size):
                if self.gridCell[i][j] == 0:
                    cells.append((i, j))
        if not cells:
            return False
        curr = random.choice(cells)
        i, j = curr
        # 90% spawn 2, 10% spawn 4
        self.gridCell[i][j] = 4 if random.random() < 0.1 else 2
        return True

    def can_merge(self):
        for i in range(self.size):
            for j in range(self.size - 1):
                if self.gridCell[i][j] == self.gridCell[i][j + 1]:
                    return True
        for i in range(self.size - 1):
            for j in range(self.size):
                if self.gridCell[i + 1][j] == self.gridCell[i][j]:
                    return True
        return False

    def paintGrid(self, highlight_cells=None):
        if highlight_cells is None:
            highlight_cells = []
        for i in range(self.size):
            for j in range(self.size):
                val = self.gridCell[i][j]
                if val == 0:
                    self.board[i][j].config(text='', bg='#cdc1b4', fg='black')
                else:
                    s = str(val)
                    bg = self.bg_color.get(s, '#3c3a32')
                    fg = self.fg_color.get(s, '#f9f6f2')
                    self.board[i][j].config(text=s, bg=bg, fg=fg)
        # apply highlight flash
        for (i, j) in highlight_cells:
            self._flash_cell(i, j)

    def _flash_cell(self, i, j, times=2, interval=80):
        original = self.board[i][j].cget('bg')
        def do_flash(count):
            if count == 0:
                self.board[i][j].config(bg=original)
                return
            self.board[i][j].config(bg='white')
            self.master.after(interval, lambda: self.board[i][j].config(bg=original))
            self.master.after(interval*2, lambda: do_flash(count-1))
        do_flash(times)


class Game:
    def __init__(self, board: Board, target=2048):
        self.board = board
        self.end = False
        self.won = False
        self.move_count = 0
        self.prev_grid = None
        self.prev_score = 0
        self.best_score = self._load_best_score()
        self.target = target

    def _load_best_score(self):
        if os.path.exists(BEST_SCORE_FILE):
            try:
                with open(BEST_SCORE_FILE, "r") as f:
                    data = json.load(f)
                return data.get("best", 0)
            except Exception:
                return 0
        return 0

    def _save_best_score(self):
        data = {"best": self.best_score}
        try:
            with open(BEST_SCORE_FILE, "w") as f:
                json.dump(data, f)
        except Exception:
            pass

    def start(self):
        self.board.random_cell()
        self.board.random_cell()
        self.board.paintGrid()
        # Key binding is handled by the application class

    def reset(self):
        self.board.gridCell = [[0] * self.board.size for _ in range(self.board.size)]
        self.board.score = 0
        self.move_count = 0
        self.end = False
        self.won = False
        self.prev_grid = None
        self.prev_score = 0
        self.board.random_cell()
        self.board.random_cell()
        self.board.paintGrid()

    def set_target(self, t):
        self.target = t

    def can_move(self):
        # check if any zero or can_merge
        for i in range(self.board.size):
            for j in range(self.board.size):
                if self.board.gridCell[i][j] == 0:
                    return True
        return self.board.can_merge()

    def save_undo(self):
        # deep copy current grid and score
        self.prev_grid = [row[:] for row in self.board.gridCell]
        self.prev_score = self.board.score

    def undo(self):
        if self.prev_grid is not None:
            self.board.gridCell = [row[:] for row in self.prev_grid]
            self.board.score = self.prev_score
            self.prev_grid = None
            self.prev_score = 0
            self.board.paintGrid()

    def move_left(self):
        if self.end or self.won:
            return False
        self.save_undo()
        self.board.compressGrid()
        self.board.mergeGrid()
        moved = self.board.compress or self.board.merge
        self.board.compressGrid()
        if moved:
            self.move_count += 1
            self.board.random_cell()
            self.board.paintGrid()
        return moved

    def move_right(self):
        if self.end or self.won:
            return False
        self.save_undo()
        self.board.reverse()
        self.board.compressGrid()
        self.board.mergeGrid()
        moved = self.board.compress or self.board.merge
        self.board.compressGrid()
        self.board.reverse()
        if moved:
            self.move_count += 1
            self.board.random_cell()
            self.board.paintGrid()
        return moved

    def move_up(self):
        if self.end or self.won:
            return False
        self.save_undo()
        self.board.transpose()
        self.board.compressGrid()
        self.board.mergeGrid()
        moved = self.board.compress or self.board.merge
        self.board.compressGrid()
        self.board.transpose()
        if moved:
            self.move_count += 1
            self.board.random_cell()
            self.board.paintGrid()
        return moved

    def move_down(self):
        if self.end or self.won:
            return False
        self.save_undo()
        self.board.transpose()
        self.board.reverse()
        self.board.compressGrid()
        self.board.mergeGrid()
        moved = self.board.compress or self.board.merge
        self.board.compressGrid()
        self.board.reverse()
        self.board.transpose()
        if moved:
            self.move_count += 1
            self.board.random_cell()
            self.board.paintGrid()
        return moved

    def after_move_updates(self):
        # update best score if needed, check win/lose
        if self.board.score > self.best_score:
            self.best_score = self.board.score
            self._save_best_score()

        # check win
        for row in self.board.gridCell:
            for val in row:
                if val == self.target:
                    self.won = True
                    messagebox.showinfo("2048", f"Congratulations! You reached {self.target}!\nScore: {self.board.score}")
                    return

        # check gameover
        if not self.can_move():
            self.end = True
            messagebox.showinfo("Game Over", f"No more moves!\nScore: {self.board.score}")


class Enhanced2048App:
    def __init__(self, root):
        self.root = root
        self.root.title("2048")
        self.root.resizable(False, False)
        self.size = 4

        # create board and game
        self.board = Board(self.root, size=self.size)
        self.game = Game(self.board, target=2048)

        # layout: top controls, board, control buttons, arrow keypad, status
        self._build_ui()
        self.game.start()

        # bind keyboard to app-level handler
        self.root.bind("<Key>", self._key_handler)

    def _build_ui(self):
        # Top frame: title and stats
        top_frame = tk.Frame(self.root)
        top_frame.grid(row=0, column=0, pady=(8, 0), padx=8)

        title = tk.Label(top_frame, text="2048", font=("Helvetica", 18, "bold"))
        title.grid(row=0, column=0, sticky="w", padx=(0, 12))

        stats_frame = tk.Frame(top_frame)
        stats_frame.grid(row=0, column=1, sticky="w")

        self.score_var = tk.IntVar(value=self.board.score)
        self.best_var = tk.IntVar(value=self.game.best_score)
        self.move_var = tk.IntVar(value=self.game.move_count)

        tk.Label(stats_frame, text="Score:", font=("Helvetica", 10, "bold")).grid(row=0, column=0, padx=(0, 2))
        tk.Label(stats_frame, textvariable=self.score_var, font=("Helvetica", 10)).grid(row=0, column=1, padx=(0, 10))
        tk.Label(stats_frame, text="Best:", font=("Helvetica", 10, "bold")).grid(row=0, column=2, padx=(0, 2))
        tk.Label(stats_frame, textvariable=self.best_var, font=("Helvetica", 10)).grid(row=0, column=3, padx=(0, 10))
        tk.Label(stats_frame, text="Moves:", font=("Helvetica", 10, "bold")).grid(row=0, column=4, padx=(0, 2))
        tk.Label(stats_frame, textvariable=self.move_var, font=("Helvetica", 10)).grid(row=0, column=5, padx=(0, 10))

        # Board placement (centered)
        board_frame = tk.Frame(self.root)
        board_frame.grid(row=1, column=0, pady=(6, 6))
        self.board.place(row=1, column=0)

        # Control buttons under the board
        control_frame = tk.Frame(self.root)
        control_frame.grid(row=2, column=0, pady=(4, 8))

        btn_new = tk.Button(control_frame, text="New Game", width=10, command=self.new_game)
        btn_new.grid(row=0, column=0, padx=6)

        btn_undo = tk.Button(control_frame, text="Undo", width=10, command=self.undo)
        btn_undo.grid(row=0, column=1, padx=6)

        btn_reset_best = tk.Button(control_frame, text="Reset Best", width=10, command=self.reset_best)
        btn_reset_best.grid(row=0, column=2, padx=6)

        btn_target = tk.Button(control_frame, text="Set Target", width=10, command=self.set_target)
        btn_target.grid(row=0, column=3, padx=6)

        # Arrow keypad centered below controls
        arrows_frame = tk.Frame(self.root)
        arrows_frame.grid(row=3, column=0, pady=(10, 6))

        up_btn = tk.Button(arrows_frame, text="↑", width=4, height=2, command=self.move_up)
        up_btn.grid(row=0, column=1, padx=3, pady=3)

        left_btn = tk.Button(arrows_frame, text="←", width=4, height=2, command=self.move_left)
        left_btn.grid(row=1, column=0, padx=3, pady=3)

        right_btn = tk.Button(arrows_frame, text="→", width=4, height=2, command=self.move_right)
        right_btn.grid(row=1, column=2, padx=3, pady=3)

        down_btn = tk.Button(arrows_frame, text="↓", width=4, height=2, command=self.move_down)
        down_btn.grid(row=2, column=1, padx=3, pady=3)

        # Status label
        self.status_label = tk.Label(self.root, text="Use arrow keys or buttons to play.", fg="gray")
        self.status_label.grid(row=4, column=0, pady=(6, 12))

        # periodic UI refresh
        self._refresh_ui()

    # UI action handlers
    def new_game(self):
        if messagebox.askyesno("New Game", "Start a new game? Current progress will be lost."):
            self.game.reset()
            self._refresh_ui()

    def undo(self):
        self.game.undo()
        self._refresh_ui()

    def reset_best(self):
        if messagebox.askyesno("Reset Best", "Reset best score to 0?"):
            self.game.best_score = 0
            self.game._save_best_score()
            self.best_var.set(0)

    def set_target(self):
        t = simpledialog.askinteger("Set target", "Enter target tile (e.g. 2048 or 4096):", parent=self.root, minvalue=128, maxvalue=65536)
        if t:
            self.game.set_target(t)
            messagebox.showinfo("Target Set", f"New target set to {t}")

    # moves call wrappers
    def move_left(self):
        moved = self.game.move_left()
        if moved:
            self.game.after_move_updates()
        self._post_move_updates()

    def move_right(self):
        moved = self.game.move_right()
        if moved:
            self.game.after_move_updates()
        self._post_move_updates()

    def move_up(self):
        moved = self.game.move_up()
        if moved:
            self.game.after_move_updates()
        self._post_move_updates()

    def move_down(self):
        moved = self.game.move_down()
        if moved:
            self.game.after_move_updates()
        self._post_move_updates()

    def _key_handler(self, event):
        key = event.keysym
        if key == 'Left':
            self.move_left()
        elif key == 'Right':
            self.move_right()
        elif key == 'Up':
            self.move_up()
        elif key == 'Down':
            self.move_down()

    def _post_move_updates(self):
        # update UI and store stats
        self.score_var.set(self.board.score)
        self.move_var.set(self.game.move_count)
        if self.board.score > self.game.best_score:
            self.game.best_score = self.board.score
            self.best_var.set(self.game.best_score)
            self.game._save_best_score()

        self.board.paintGrid()
        if self.game.won:
            self.status_label.config(text=f"Reached target {self.game.target}!")
        elif self.game.end:
            self.status_label.config(text="No more moves. Game Over.")
        else:
            self.status_label.config(text="Playing...")

    def _refresh_ui(self):
        # periodic UI refresh to show current values
        self.score_var.set(self.board.score)
        self.best_var.set(self.game.best_score)
        self.move_var.set(self.game.move_count)
        self.board.paintGrid()
        self.root.after(200, self._refresh_ui)


if __name__ == "__main__":
    root = tk.Tk()
    app = Enhanced2048App(root)
    root.mainloop()
