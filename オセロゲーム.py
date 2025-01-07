import tkinter as tk
from tkinter import messagebox
import random
import json

class OthelloGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Othello Game")
        self.board_size = 6
        self.cell_size = 95
        self.current_player = None
        self.board = [[None] * self.board_size for _ in range(self.board_size)]
        self.canvas = None
        self.history_of_moves = []
        self.pass_button = None
        self.ai_skill_level = 1
        self.corners = [(0, 0), (0, self.board_size - 1), (self.board_size - 1, 0), (self.board_size - 1, self.board_size - 1)]
        self.learning_data_file = "ai_learning.json"
        self.bad_moves = self.load_learning_data()
        self.start_screen()

    def load_learning_data(self):
        try:
            with open(self.learning_data_file, "r") as f:
                return list({tuple(move) for move in json.load(f)})  
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def save_learning_data(self):
        with open(self.learning_data_file, "w") as f:
            json.dump([list(move) for move in self.bad_moves], f)

    def reset_learning_data(self):
        delete_count_history = len(self.history_of_moves)  # 最低1個は削除
        self.history_of_moves = self.history_of_moves[delete_count_history:]  # 前方から削除
        self.bad_moves = []
        self.save_learning_data()
        messagebox.showinfo("学習データリセット", "学習記録をリセットしました。")

    def start_screen(self):
        self.clear_screen()
        self.root.geometry("1000x1000")
        label = tk.Label(self.root, text="Othello Game", font=("Arial", 24))
        label.pack(pady=50)

        rule_text = "○ ルール:\n1. 石を挟むと相手の石が反転します。\n2. 合法手がない場合はパスボタンを押してください。\n3. あなたは、黒色の石を使います。\n4. ゲーム終了時に石が多い方が勝利します。"
        rules = tk.Label(self.root, text=rule_text, font=("Arial", 14), justify="left")
        rules.pack(pady=10)

        start_button = tk.Button(self.root, text="スタート", command=self.start_game, font=("Arial", 14))
        start_button.pack(pady=10)

        learning_button = tk.Button(self.root, text="学習記録を表示", command=self.show_learning_data, font=("Arial", 14))
        learning_button.pack(pady=10)

        reset_button = tk.Button(self.root, text="学習記録をリセット", command=self.reset_learning_data, font=("Arial", 14), bg="red", fg="white")
        reset_button.pack(pady=10)

    def start_game(self):
        self.clear_screen()
        self.board = [[None] * self.board_size for _ in range(self.board_size)]
        mid = self.board_size // 2
        self.board[mid - 1][mid - 1] = "White"
        self.board[mid - 1][mid] = "Black"
        self.board[mid][mid - 1] = "Black"
        self.board[mid][mid] = "White"

        self.canvas = tk.Canvas(self.root, width=self.board_size * self.cell_size,
                                height=self.board_size * self.cell_size, bg="green")
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.handle_click)

        self.pass_button = tk.Button(self.root, text="パス", command=self.pass_turn, font=("Arial", 14), bg="lightgrey")
        self.pass_button.pack(pady=10)

        self.current_player = random.choice(["Player", "AI"])
        turn_text = "先行は自分からです" if self.current_player == "Player" else "先行は相手からです"
        messagebox.showinfo("先行決定", turn_text)
        self.draw_board()

        if self.current_player == "AI":
            self.root.after(500, self.ai_turn)

    def pass_turn(self):
        if self.current_player == "Player":
            self.current_player = "AI"
            messagebox.showinfo("パス", "自分が置けないため、順番を渡します。")
            self.root.after(500, self.ai_turn)

    def draw_board(self):
        self.canvas.delete("all")
        for i in range(self.board_size):
            for j in range(self.board_size):
                x1, y1 = j * self.cell_size, i * self.cell_size
                x2, y2 = x1 + self.cell_size, y1 + self.cell_size
                self.canvas.create_rectangle(x1, y1, x2, y2, outline="black", fill="green")
                if self.board[i][j] == "Black":
                    self.canvas.create_oval(x1 + 5, y1 + 5, x2 - 5, y2 - 5, fill="black")
                elif self.board[i][j] == "White":
                    self.canvas.create_oval(x1 + 5, y1 + 5, x2 - 5, y2 - 5, fill="white")

    def handle_click(self, event):
        if self.current_player != "Player":
            return

        col = event.x // self.cell_size
        row = event.y // self.cell_size

        if 0 <= row < self.board_size and 0 <= col < self.board_size:
            if self.board[row][col] is None and self.is_valid_move(row, col, "Black"):
                self.place_stone(row, col, "Black")
                if self.check_game_over():
                    self.show_result()
                    return
                self.current_player = "AI"
                self.root.after(500, self.ai_turn)
            else:
                messagebox.showerror("無効な場所", "ここには黒い石を置けません。")

    def is_valid_move(self, row, col, color):
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (-1, 1), (1, -1)]
        for dx, dy in directions:
            if self.can_flip(row, col, dx, dy, color):
                return True
        return False

    def can_flip(self, row, col, dx, dy, color):
        x, y = row + dx, col + dy
        opponent = "White" if color == "Black" else "Black"
        has_opponent = False
        while 0 <= x < self.board_size and 0 <= y < self.board_size:
            if self.board[x][y] == opponent:
                has_opponent = True
            elif self.board[x][y] == color:
                return has_opponent
            else:
                break
            x += dx
            y += dy
        return False

    def place_stone(self, row, col, color):
        self.board[row][col] = color
        self.flip_stones(row, col, color)
        self.history_of_moves.append((row, col, color))
        self.draw_board()

    def flip_stones(self, row, col, color):
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (-1, 1), (1, -1)]
        for dx, dy in directions:
            if self.can_flip(row, col, dx, dy, color):
                self.flip_direction(row, col, dx, dy, color)

    def flip_direction(self, row, col, dx, dy, color):
        x, y = row + dx, col + dy
        opponent = "White" if color == "Black" else "Black"
        while 0 <= x < self.board_size and 0 <= y < self.board_size and self.board[x][y] == opponent:
            self.board[x][y] = color
            x += dx
            y += dy

    def ai_turn(self):
        best_move = self.get_corner_move()

        if not best_move:
            best_move = self.get_safe_move()

        if not best_move and self.current_player == "AI" and self.history_of_moves:
            best_move = self.get_second_turn_move()

        if not best_move:
            best_move = self.get_low_open_move()

        if best_move:
            row, col = best_move
            if (row, col) in self.bad_moves:
                self.ai_turn()  # 再帰的に次の手を選択
                return
            self.place_stone(row, col, "White")
        else:
            messagebox.showinfo("情報", "相手はおける場所がない。あなたの番です")
            self.current_player = "Player"
            return

        if self.check_game_over():
            self.show_result()
            return

        self.current_player = "Player"
 

    def get_corner_move(self):
        for corner in self.corners:
            row, col = corner
            if self.board[row][col] is None and self.is_valid_move(row, col, "White"):
                return (row, col)
        return None

    def get_safe_move(self):
        # 隅の隣接マスを避ける
        unsafe_moves = set()
        for corner in self.corners:
            row, col = corner
            for dx in [-1, 1]:
                for dy in [-1, 1]:
                    nx, ny = row + dx, col + dy
                    if 0 <= nx < self.board_size and 0 <= ny < self.board_size and self.board[nx][ny] is None:
                        unsafe_moves.add((nx, ny))
        
        safe_moves = [(r, c) for r in range(self.board_size) for c in range(self.board_size)
                      if self.board[r][c] is None and self.is_valid_move(r, c, "White") and (r, c) not in unsafe_moves]

        if safe_moves:
            return random.choice(safe_moves)
        return None

    def get_second_turn_move(self):
        # AIの2番目の手：平行にならないように
        best_move = None
        for row in range(self.board_size):
            for col in range(self.board_size):
                if self.board[row][col] is None and self.is_valid_move(row, col, "White"):
                    best_move = (row, col)
                    break
        return best_move

    def get_low_open_move(self):
        # 開放度が少ない場所を選ぶ
        best_move = None
        best_open = float('inf')

        for row in range(self.board_size):
            for col in range(self.board_size):
                if self.board[row][col] is None and self.is_valid_move(row, col, "White"):
                    open_count = self.count_open_spaces(row, col)
                    if open_count < best_open:
                        best_open = open_count
                        best_move = (row, col)

        return best_move

    def count_open_spaces(self, row, col):
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, 1), (-1, 1), (1, -1)]
        open_count = 0

        for dx, dy in directions:
            x, y = row + dx, col + dy
            while 0 <= x < self.board_size and 0 <= y < self.board_size:
                if self.board[x][y] is None:
                    open_count += 1
                    break
                x += dx
                y += dy

        return open_count

    def check_game_over(self):
        for row in range(self.board_size):
            for col in range(self.board_size):
                if self.board[row][col] is None and (
                        self.is_valid_move(row, col, "Black") or self.is_valid_move(row, col, "White")):
                    return False
        return True

    def show_result(self):
        black_count = sum(row.count("Black") for row in self.board)
        white_count = sum(row.count("White") for row in self.board)

        if black_count > white_count:
            winner = "黒"
            self.bad_moves = [tuple(move) for move in self.history_of_moves if move[2] == "White"]
            
             
                        
        elif white_count > black_count:
            winner = "白"
            if self.bad_moves:
                delete_count = max(1, len(self.bad_moves) //2)  # 最低1個は削除
                self.bad_moves = self.bad_moves[delete_count:]  # 前方から削除
                
                delete_count_history = len(self.history_of_moves)  # 最低1個は削除
                self.history_of_moves = self.history_of_moves[delete_count_history:]  # 前方から削除

        else:
            winner = "引き分け"

        
   

        # ゲーム結果を記録として保存
        self.save_learning_data()

        messagebox.showinfo("結果", f"ゲーム終了！\n黒: {black_count} 白: {white_count}\n勝者: {winner}")
        self.start_screen()

    def show_learning_data(self):
        self.clear_screen()
        label = tk.Label(self.root, text="学習記録", font=("Arial", 24))
        label.pack(pady=20)

        if self.bad_moves:
            # 学習記録を10行ごとに改行して表示
            display_text = ""
            for i, move in enumerate(self.bad_moves):
                if i % 10 == 0 and i > 0:
                    display_text += "\n"
                display_text += f"座標: {move[:2]} "
            move_label = tk.Label(self.root, text=display_text, font=("Arial", 10), justify="left")
            move_label.pack()
        else:
            empty_label = tk.Label(self.root, text="学習記録はまだありません。", font=("Arial", 14))
            empty_label.pack()

        back_button = tk.Button(self.root, text="戻る", command=self.start_screen, font=("Arial", 14))
        back_button.pack(pady=10)

    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

root = tk.Tk()
game = OthelloGame(root)
root.mainloop()














