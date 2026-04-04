import tkinter as tk

class DartApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Dart")
        self.root.geometry("480x320")
        self.root.attributes('-fullscreen', True)

        self.num_players = 0
        self.start_score = 501
        self.players = {}
        self.current_player_index = 0

        self.show_player_select()

    def clear(self):
        for w in self.root.winfo_children():
            w.destroy()

    # --- Screen 1 ---
    def show_player_select(self):
        self.clear()
        tk.Label(self.root, text="Antal spelare", font=("Arial", 18)).pack(pady=10)

        for i in range(1, 5):
            tk.Button(self.root, text=f"{i}", font=("Arial", 18),
                      command=lambda n=i: self.set_players(n)).pack(fill="x", padx=20, pady=5)

    def set_players(self, n):
        self.num_players = n
        self.show_game_select()

    # --- Screen 2 ---
    def show_game_select(self):
        self.clear()
        tk.Label(self.root, text="Välj spel", font=("Arial", 18)).pack(pady=10)

        for g in [301, 501, 701]:
            tk.Button(self.root, text=str(g), font=("Arial", 18),
                      command=lambda s=g: self.start_game(s)).pack(fill="x", padx=20, pady=5)

    def start_game(self, score):
        self.start_score = score
        self.players = {f"Spelare {i+1}": score for i in range(self.num_players)}
        self.current_player_index = 0
        self.show_game()

    # --- Game ---
    def show_game(self):
        self.clear()

        self.current_dart = 1
        self.darts = [0,0,0]
        self.multiplier = 1

        self.score_label = tk.Label(self.root, font=("Arial", 12), justify="left")
        self.score_label.place(x=5, y=5, width=470, height=60)

        self.dart_label = tk.Label(self.root, text="Pil 1", font=("Arial", 16))
        self.dart_label.place(x=5, y=65, width=150, height=40)

        multi = tk.Frame(self.root)
        multi.place(x=160, y=65, width=310, height=40)

        for i,m in enumerate([1,2,3]):
            tk.Button(multi, text=f"x{m}", command=lambda mm=m: self.set_multiplier(mm))                .grid(row=0, column=i, sticky="nsew")
            multi.columnconfigure(i, weight=1)

        grid = tk.Frame(self.root)
        grid.place(x=5, y=110, width=470, height=150)

        num=1
        for r in range(4):
            for c in range(5):
                if num<=20:
                    tk.Button(grid, text=str(num), command=lambda v=num: self.hit(v))                        .grid(row=r, column=c, sticky="nsew")
                    num+=1

        for i in range(4): grid.rowconfigure(i, weight=1)
        for i in range(5): grid.columnconfigure(i, weight=1)

        special = tk.Frame(self.root)
        special.place(x=5, y=265, width=470, height=50)

        tk.Button(special, text="Miss", command=lambda: self.hit(0)).pack(side="left", expand=True, fill="both")
        tk.Button(special, text="25", command=lambda: self.hit(25)).pack(side="left", expand=True, fill="both")
        tk.Button(special, text="50", command=lambda: self.hit(50)).pack(side="left", expand=True, fill="both")

        self.update_score()

    def set_multiplier(self, m):
        self.multiplier = m

    def hit(self, value):
        score = value if value in [25,50] else value*self.multiplier
        self.darts[self.current_dart-1] = score
        self.current_dart +=1

        if self.current_dart>3:
            self.finish_round()
        else:
            self.dart_label.config(text=f"Pil {self.current_dart}")

    def finish_round(self):
        total = sum(self.darts)
        player = list(self.players.keys())[self.current_player_index]

        new_score = self.players[player] - total
        if new_score>=0:
            self.players[player]=new_score

        if new_score==0:
            self.show_winner(player)
            return

        self.darts=[0,0,0]
        self.current_dart=1
        self.dart_label.config(text="Pil 1")

        self.current_player_index=(self.current_player_index+1)%self.num_players
        self.update_score()

    def update_score(self):
        text="\n".join([f"{p}: {s}" for p,s in self.players.items()])
        current=list(self.players.keys())[self.current_player_index]
        text+=f"\nTur: {current}"
        self.score_label.config(text=text)

    def show_winner(self, player):
        self.clear()
        tk.Label(self.root, text=f"{player} vann!", font=("Arial", 24)).pack(expand=True)


root=tk.Tk()
app=DartApp(root)
root.mainloop()
