import tkinter as tk
from constants import COLORS, CHECKOUTS


class X01Mixin:
    """Mixin för X01-spel (301, 501, 701)"""

    def start_game(self):
        """Starta X01-spel"""
        self.players = {name: self.start_score for name in self.player_names}
        self.player_stats = {name: {'darts': 0, 'total': 0, 'rounds': 0} 
                            for name in self.player_names}
        self.current_player_index = 0
        self.history = []
        self.show_game()

    def show_game(self):
        """Visa X01-spelskärmen"""
        self.clear()

        self.current_dart = 1
        self.darts = [None, None, None]
        self.dart_details = []
        self.multiplier = 1
        self.round_score = 0

        # Top panel: scores
        top = tk.Frame(self.root, bg=COLORS['panel'])
        top.place(x=0, y=0, width=480, height=55)

        self.score_labels = {}
        for i, name in enumerate(self.player_names):
            x = 5 + i * (470 // self.num_players)
            width = (470 // self.num_players) - 5

            frame = tk.Frame(top, bg=COLORS['panel'])
            frame.place(x=x, y=2, width=width, height=50)

            is_current = i == self.current_player_index
            name_color = COLORS['accent'] if is_current else COLORS['text']
            
            name_lbl = tk.Label(frame, text=name[:8], font=("Arial", 10, "bold"),
                               fg=name_color, bg=COLORS['panel'])
            name_lbl.pack()
            
            score_lbl = tk.Label(frame, text=str(self.players[name]),
                                font=("Arial", 16, "bold"),
                                fg=COLORS['gold'] if is_current else COLORS['text'],
                                bg=COLORS['panel'])
            score_lbl.pack()
            self.score_labels[name] = (name_lbl, score_lbl)

        # Info row: dart number + darts thrown + checkout
        info = tk.Frame(self.root, bg=COLORS['bg'])
        info.place(x=0, y=55, width=480, height=35)

        self.dart_label = tk.Label(info, text="Pil 1", font=("Arial", 12, "bold"),
                                  fg=COLORS['green'], bg=COLORS['bg'])
        self.dart_label.place(x=5, y=5)

        self.thrown_label = tk.Label(info, text="", font=("Arial", 11),
                                    fg=COLORS['text'], bg=COLORS['bg'])
        self.thrown_label.place(x=60, y=5)

        self.checkout_label = tk.Label(info, text="", font=("Arial", 10),
                                       fg=COLORS['gold'], bg=COLORS['bg'])
        self.checkout_label.place(x=250, y=5)

        # Multiplier buttons
        multi = tk.Frame(self.root, bg=COLORS['bg'])
        multi.place(x=5, y=90, width=470, height=35)

        self.multi_buttons = []
        labels = [("Single", 1), ("Double", 2), ("Triple", 3)]
        for i, (txt, m) in enumerate(labels):
            btn = tk.Button(multi, text=txt, font=("Arial", 11, "bold"),
                           bg=COLORS['button'] if m != 1 else COLORS['accent'],
                           fg=COLORS['text'],
                           activebackground=COLORS['button_active'],
                           relief="flat",
                           command=lambda mm=m: self.set_multiplier(mm))
            btn.grid(row=0, column=i, sticky="nsew", padx=2)
            multi.columnconfigure(i, weight=1)
            self.multi_buttons.append(btn)

        # Number grid
        grid = tk.Frame(self.root, bg=COLORS['bg'])
        grid.place(x=5, y=130, width=470, height=130)

        num = 1
        for r in range(4):
            for c in range(5):
                if num <= 20:
                    btn = tk.Button(grid, text=str(num), font=("Arial", 12, "bold"),
                                   bg=COLORS['button'], fg=COLORS['text'],
                                   activebackground=COLORS['button_active'],
                                   relief="flat",
                                   command=lambda v=num: self.hit(v))
                    btn.grid(row=r, column=c, sticky="nsew", padx=1, pady=1)
                    num += 1
            grid.rowconfigure(r, weight=1)
        for c in range(5):
            grid.columnconfigure(c, weight=1)

        # Special buttons row
        special = tk.Frame(self.root, bg=COLORS['bg'])
        special.place(x=5, y=265, width=470, height=50)

        btns = [("Miss", 0), ("25", 25), ("Bull", 50), ("Ångra", -1), ("Klar", -2), ("?", -3)]
        for i, (txt, val) in enumerate(btns):
            if val == -1:
                cmd = self.undo_dart
                bg = COLORS['accent2']
            elif val == -2:
                cmd = self.finish_round
                bg = COLORS['green']
            elif val == -3:
                cmd = lambda: self.show_help('x01', self.show_game)
                bg = COLORS['accent2']
            else:
                cmd = lambda v=val: self.hit(v)
                bg = COLORS['button']
            
            btn = tk.Button(special, text=txt, font=("Arial", 12, "bold"),
                           bg=bg, fg=COLORS['text'],
                           activebackground=COLORS['button_active'],
                           relief="flat", command=cmd)
            btn.grid(row=0, column=i, sticky="nsew", padx=2, pady=2)
            special.columnconfigure(i, weight=1)

        self.update_checkout()

    def set_multiplier(self, m):
        """Sätt multiplikator (single/double/triple)"""
        self.multiplier = m
        for i, btn in enumerate(self.multi_buttons):
            btn.config(bg=COLORS['accent'] if i + 1 == m else COLORS['button'])

    def hit(self, value):
        """Registrera en träff"""
        if self.current_dart > 3:
            return

        if value == 0:
            score = 0
            self.dart_details.append((0, 1))
        elif value == 25:
            score = 25 * self.multiplier if self.multiplier <= 2 else 25
            self.dart_details.append((25, min(self.multiplier, 2)))
        elif value == 50:
            score = 50
            self.dart_details.append((25, 2))
        else:
            score = value * self.multiplier
            self.dart_details.append((value, self.multiplier))

        self.darts[self.current_dart - 1] = score
        self.round_score = sum(d for d in self.darts if d is not None)
        self.update_thrown_display()

        self.current_dart += 1
        if self.current_dart > 3:
            self.finish_round()
        else:
            self.dart_label.config(text=f"Pil {self.current_dart}")
            self.set_multiplier(1)
            self.update_checkout()

    def undo_dart(self):
        """Ångra senaste pilen"""
        if self.current_dart > 1 and self.dart_details:
            self.current_dart -= 1
            self.darts[self.current_dart - 1] = None
            self.dart_details.pop()
            self.round_score = sum(d for d in self.darts if d is not None)
            self.dart_label.config(text=f"Pil {self.current_dart}")
            self.update_thrown_display()
            self.update_checkout()

    def update_thrown_display(self):
        """Uppdatera visning av kastade pilar"""
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

    def update_checkout(self):
        """Visa checkout-förslag"""
        player = self.player_names[self.current_player_index]
        remaining = self.players[player] - self.round_score
        
        if remaining in CHECKOUTS:
            self.checkout_label.config(text=f"Checkout: {CHECKOUTS[remaining]}")
        else:
            self.checkout_label.config(text="")

    def finish_round(self):
        """Avsluta rundan"""
        total = sum(d for d in self.darts if d is not None)
        player = self.player_names[self.current_player_index]
        old_score = self.players[player]
        new_score = old_score - total

        # Spara historik
        self.history.append({
            'player': player,
            'darts': self.dart_details.copy(),
            'total': total,
            'old_score': old_score
        })

        # Uppdatera statistik
        darts_thrown = len([d for d in self.darts if d is not None])
        self.player_stats[player]['darts'] += darts_thrown
        self.player_stats[player]['total'] += total
        self.player_stats[player]['rounds'] += 1

        # Kontrollera giltigt avslut
        valid = True
        if new_score < 0:
            valid = False
        elif new_score == 1 and self.double_out:
            valid = False
        elif new_score == 0 and self.double_out:
            if self.dart_details:
                last_val, last_mult = self.dart_details[-1]
                if last_mult != 2:
                    valid = False

        if valid and new_score >= 0:
            self.players[player] = new_score

        if new_score == 0 and valid:
            self.show_winner(player)
            return

        # Nästa spelare
        self.current_player_index = (self.current_player_index + 1) % self.num_players
        self.show_game()

    def update_scores_display(self):
        """Uppdatera poängvisning"""
        for i, name in enumerate(self.player_names):
            is_current = i == self.current_player_index
            name_lbl, score_lbl = self.score_labels[name]
            name_lbl.config(fg=COLORS['accent'] if is_current else COLORS['text'])
            score_lbl.config(text=str(self.players[name]),
                           fg=COLORS['gold'] if is_current else COLORS['text'])
