import tkinter as tk
from constants import COLORS


class HighScoreMixin:
    """Mixin för High Score-spel"""

    def start_highscore_game(self):
        """Starta High Score-spel"""
        self.highscore_rounds = 10  # Antal rundor
        self.highscore_current_round = 1
        self.highscore_scores = {name: 0 for name in self.player_names}
        self.highscore_round_scores = {name: [] for name in self.player_names}
        self.current_player_index = 0
        self.show_highscore_game()

    def show_highscore_game(self):
        """Visa High Score-spelskärmen"""
        self.clear()
        self.current_dart = 1
        self.darts = [None, None, None]
        self.dart_details = []
        self.multiplier = 1
        self.round_score = 0

        # Top: poängtavla
        top = tk.Frame(self.root, bg=COLORS['panel'])
        top.place(x=0, y=0, width=self.W, height=self.sy(55))

        for i, name in enumerate(self.player_names):
            x = self.sx(5) + i * (self.sx(470) // self.num_players)
            width = (self.sx(470) // self.num_players) - self.sx(5)
            
            frame = tk.Frame(top, bg=COLORS['panel'])
            frame.place(x=x, y=self.sy(2), width=width, height=self.sy(50))
            
            is_current = i == self.current_player_index
            fg = COLORS['gold'] if is_current else COLORS['text']
            
            tk.Label(frame, text=name[:8], font=("Arial", 10, "bold"),
                    fg=fg, bg=COLORS['panel']).pack()
            tk.Label(frame, text=str(self.highscore_scores[name]), font=("Arial", 16, "bold"),
                    fg=fg, bg=COLORS['panel']).pack()

        # Info
        info = tk.Frame(self.root, bg=COLORS['bg'])
        info.place(x=0, y=self.sy(55), width=self.W, height=self.sy(35))
        
        tk.Label(info, text=f"Runda {self.highscore_current_round}/{self.highscore_rounds}", 
                font=("Arial", 14, "bold"), fg=COLORS['gold'], bg=COLORS['bg']).pack()
        
        self.dart_label = tk.Label(info, text=f"Pil {self.current_dart}", font=("Arial", 18, "bold"),
                                   fg=COLORS['green'], bg=COLORS['bg'])
        self.dart_label.place(x=self.sx(5), y=self.sy(5))
        
        self.thrown_label = tk.Label(info, text="", font=("Arial", 10),
                                    fg=COLORS['text'], bg=COLORS['bg'])
        self.thrown_label.place(x=self.sx(60), y=self.sy(5))

        # Multiplier
        multi = tk.Frame(self.root, bg=COLORS['bg'])
        multi.place(x=self.sx(5), y=self.sy(90), width=self.sx(470), height=self.sy(35))
        
        self.multi_buttons = []
        for i, (txt, m) in enumerate([("Single", 1), ("Double", 2), ("Triple", 3)]):
            btn = tk.Button(multi, text=txt, font=("Arial", 11, "bold"),
                           bg=COLORS['accent'] if m == 1 else COLORS['button'],
                           fg=COLORS['text'], relief="flat",
                           command=lambda mm=m: self.set_multiplier(mm))
            btn.grid(row=0, column=i, sticky="nsew", padx=2)
            multi.columnconfigure(i, weight=1)
            self.multi_buttons.append(btn)

        # Number grid
        grid = tk.Frame(self.root, bg=COLORS['bg'])
        grid.place(x=self.sx(5), y=self.sy(130), width=self.sx(470), height=self.sy(130))

        num = 1
        for r in range(4):
            for c in range(5):
                if num <= 20:
                    btn = tk.Button(grid, text=str(num), font=("Arial", 12, "bold"),
                                   bg=COLORS['button'], fg=COLORS['text'], relief="flat",
                                   command=lambda v=num: self.highscore_hit(v))
                    btn.grid(row=r, column=c, sticky="nsew", padx=1, pady=1)
                    num += 1
            grid.rowconfigure(r, weight=1)
        for c in range(5):
            grid.columnconfigure(c, weight=1)

        # Special buttons
        special = tk.Frame(self.root, bg=COLORS['bg'])
        special.place(x=self.sx(5), y=self.sy(265), width=self.sx(470), height=self.sy(50))
        
        btns = [
            ("Miss", lambda: self.highscore_hit(0), COLORS['button']),
            ("25", lambda: self.highscore_hit(25), COLORS['button']),
            ("Bull", lambda: self.highscore_hit(50), COLORS['button']),
            ("Ångra", self.highscore_undo, COLORS['accent2']),
            ("Klar", self.highscore_finish_round, COLORS['green']),
            ("?", lambda: self.show_help('highscore', self.show_highscore_game), COLORS['accent2']),
            ("✕", self.show_game_select, COLORS['accent2'])
        ]
        for i, (txt, cmd, bg) in enumerate(btns):
            btn = tk.Button(special, text=txt, font=("Arial", 10, "bold"),
                           bg=bg, fg=COLORS['text'], relief="flat", command=cmd)
            btn.grid(row=0, column=i, sticky="nsew", padx=1, pady=2)
            special.columnconfigure(i, weight=1)

    def highscore_hit(self, value):
        """Registrera en High Score-träff"""
        if self.current_dart > 3:
            return
        
        if value == 0:
            score = 0
            self.dart_details.append((0, 1))
        elif value == 25:
            score = 25 * min(self.multiplier, 2)
            self.dart_details.append((25, min(self.multiplier, 2)))
        elif value == 50:
            score = 50
            self.dart_details.append((25, 2))
        else:
            score = value * self.multiplier
            self.dart_details.append((value, self.multiplier))

        self.darts[self.current_dart - 1] = score
        self.round_score = sum(d for d in self.darts if d is not None)
        self._update_highscore_display()

        self.current_dart += 1
        if self.current_dart > 3:
            self.highscore_finish_round()
        else:
            self.dart_label.config(text=f"Pil {self.current_dart}")
            self.set_multiplier(1)

    def _update_highscore_display(self):
        """Uppdatera visning"""
        parts = []
        for val, mult in self.dart_details:
            if val == 0:
                parts.append("Miss")
            elif mult == 3:
                parts.append(f"T{val}")
            elif mult == 2:
                parts.append(f"D{val}")
            else:
                parts.append(str(val))
        self.thrown_label.config(text=" + ".join(parts) + f" = {self.round_score}" if parts else "")

    def highscore_undo(self):
        """Ångra senaste High Score-pilen"""
        if self.current_dart > 1 and self.dart_details:
            self.current_dart -= 1
            self.darts[self.current_dart - 1] = None
            self.dart_details.pop()
            self.round_score = sum(d for d in self.darts if d is not None)
            self.dart_label.config(text=f"Pil {self.current_dart}")
            self._update_highscore_display()

    def highscore_finish_round(self):
        """Avsluta High Score-rundan"""
        player = self.player_names[self.current_player_index]
        
        # Lägg till runda-poäng
        total = sum(d for d in self.darts if d is not None)
        self.highscore_scores[player] += total
        self.highscore_round_scores[player].append(total)

        # Nästa spelare
        self.current_player_index = (self.current_player_index + 1) % self.num_players
        
        # Om alla spelat, nästa runda
        if self.current_player_index == 0:
            self.highscore_current_round += 1
            
            if self.highscore_current_round > self.highscore_rounds:
                # Högst poäng vinner
                winner = max(self.player_names, key=lambda p: self.highscore_scores[p])
                self.show_winner(winner)
                return
        
        self.show_highscore_game()
