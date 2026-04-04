import tkinter as tk
from constants import COLORS


class GolfMixin:
    """Mixin för Golf-spel"""

    def start_golf_game(self):
        """Starta Golf-spel"""
        self.golf_holes = 9  # 9 eller 18 hål
        self.golf_current_hole = 1
        self.golf_scores = {name: 0 for name in self.player_names}  # Lägre är bättre
        self.golf_hole_scores = {name: [] for name in self.player_names}
        self.current_player_index = 0
        self.show_golf_game()

    def show_golf_game(self):
        """Visa Golf-spelskärmen"""
        self.clear()
        self.current_dart = 1
        self.dart_details = []
        self.multiplier = 1
        self.hole_total = 0

        target = self.golf_current_hole  # Hål = nummer att sikta på

        # Top: poängtavla
        top = tk.Frame(self.root, bg=COLORS['panel'])
        top.place(x=0, y=0, width=480, height=55)

        for i, name in enumerate(self.player_names):
            x = 5 + i * (470 // self.num_players)
            width = (470 // self.num_players) - 5
            
            frame = tk.Frame(top, bg=COLORS['panel'])
            frame.place(x=x, y=2, width=width, height=50)
            
            is_current = i == self.current_player_index
            fg = COLORS['gold'] if is_current else COLORS['text']
            
            tk.Label(frame, text=name[:8], font=("Arial", 10, "bold"),
                    fg=fg, bg=COLORS['panel']).pack()
            # I golf är lägre bättre
            tk.Label(frame, text=str(self.golf_scores[name]), font=("Arial", 16, "bold"),
                    fg=fg, bg=COLORS['panel']).pack()

        # Info
        info = tk.Frame(self.root, bg=COLORS['bg'])
        info.place(x=0, y=55, width=480, height=40)
        
        tk.Label(info, text=f"Hål {target}/{self.golf_holes} - Sikta på {target}", 
                font=("Arial", 14, "bold"), fg=COLORS['gold'], bg=COLORS['bg']).pack()
        
        self.dart_label = tk.Label(info, text=f"Pil {self.current_dart}", font=("Arial", 10),
                                   fg=COLORS['green'], bg=COLORS['bg'])
        self.dart_label.place(x=5, y=5)
        
        self.thrown_label = tk.Label(info, text="", font=("Arial", 10),
                                    fg=COLORS['text'], bg=COLORS['bg'])
        self.thrown_label.place(x=60, y=22)

        # Poängsystem info
        scoring = tk.Label(info, text="T=1  D=2  S=3  Miss=5", font=("Arial", 8),
                          fg=COLORS['accent2'], bg=COLORS['bg'])
        scoring.place(x=350, y=5)

        # Multiplier
        multi = tk.Frame(self.root, bg=COLORS['bg'])
        multi.place(x=5, y=95, width=470, height=30)
        
        self.multi_buttons = []
        for i, (txt, m) in enumerate([("Single", 1), ("Double", 2), ("Triple", 3)]):
            btn = tk.Button(multi, text=txt, font=("Arial", 10, "bold"),
                           bg=COLORS['accent'] if m == 1 else COLORS['button'],
                           fg=COLORS['text'], relief="flat",
                           command=lambda mm=m: self.set_multiplier(mm))
            btn.grid(row=0, column=i, sticky="nsew", padx=2)
            multi.columnconfigure(i, weight=1)
            self.multi_buttons.append(btn)

        # Stor knapp för aktuellt hål + miss
        grid = tk.Frame(self.root, bg=COLORS['bg'])
        grid.place(x=5, y=130, width=470, height=130)
        
        target_btn = tk.Button(grid, text=str(target), font=("Arial", 36, "bold"),
                              bg=COLORS['accent'], fg=COLORS['text'], relief="flat",
                              command=lambda: self.golf_hit(target))
        target_btn.place(x=50, y=10, width=180, height=110)
        
        miss_btn = tk.Button(grid, text="Miss", font=("Arial", 18, "bold"),
                            bg=COLORS['button'], fg=COLORS['text'], relief="flat",
                            command=lambda: self.golf_hit(0))
        miss_btn.place(x=250, y=10, width=180, height=110)

        # Special buttons
        special = tk.Frame(self.root, bg=COLORS['bg'])
        special.place(x=5, y=265, width=470, height=50)
        
        btns = [
            ("Ångra", self.golf_undo, COLORS['accent2']),
            ("Klar", self.golf_finish_hole, COLORS['green']),
            ("?", lambda: self.show_help('golf', self.show_golf_game), COLORS['accent2']),
            ("✕", self.show_game_select, COLORS['accent2'])
        ]
        for i, (txt, cmd, bg) in enumerate(btns):
            btn = tk.Button(special, text=txt, font=("Arial", 12, "bold"),
                           bg=bg, fg=COLORS['text'], relief="flat", command=cmd)
            btn.grid(row=0, column=i, sticky="nsew", padx=2, pady=2)
            special.columnconfigure(i, weight=1)

    def _golf_dart_score(self, value, mult):
        """Räkna ut golfpoäng för en pil"""
        target = self.golf_current_hole
        
        if value == 0:
            return 5  # Miss
        elif value == target:
            if mult == 3:
                return 1  # Triple = hole in one!
            elif mult == 2:
                return 2  # Double
            else:
                return 3  # Single
        else:
            return 5  # Fel nummer

    def golf_hit(self, value):
        """Registrera en Golf-träff"""
        if self.current_dart > 3:
            return
        
        score = self._golf_dart_score(value, self.multiplier)
        self.dart_details.append((value, self.multiplier, score))
        self.hole_total += score
        
        self.current_dart += 1
        self._update_golf_display()
        
        if self.current_dart > 3:
            self.golf_finish_hole()
        else:
            self.dart_label.config(text=f"Pil {self.current_dart}")
            self.set_multiplier(1)

    def _update_golf_display(self):
        """Uppdatera visning"""
        parts = []
        for val, mult, score in self.dart_details:
            if val == 0:
                parts.append(f"Miss({score})")
            elif mult == 3:
                parts.append(f"T{val}({score})")
            elif mult == 2:
                parts.append(f"D{val}({score})")
            else:
                parts.append(f"{val}({score})")
        
        # Bästa poängen räknas
        best = min(d[2] for d in self.dart_details) if self.dart_details else 0
        self.thrown_label.config(text=" ".join(parts) + f" → Bäst: {best}" if parts else "")

    def golf_undo(self):
        """Ångra senaste Golf-pilen"""
        if self.dart_details:
            _, _, score = self.dart_details.pop()
            self.hole_total -= score
            self.current_dart -= 1
            self.dart_label.config(text=f"Pil {self.current_dart}")
            self._update_golf_display()

    def golf_finish_hole(self):
        """Avsluta Golf-hålet"""
        player = self.player_names[self.current_player_index]
        
        # Bästa av 3 pilar räknas
        if self.dart_details:
            best_score = min(d[2] for d in self.dart_details)
        else:
            best_score = 5  # Miss om inga pilar
        
        self.golf_scores[player] += best_score
        self.golf_hole_scores[player].append(best_score)

        # Nästa spelare
        self.current_player_index = (self.current_player_index + 1) % self.num_players
        
        # Om alla spelat, nästa hål
        if self.current_player_index == 0:
            self.golf_current_hole += 1
            
            if self.golf_current_hole > self.golf_holes:
                # Lägst poäng vinner
                winner = min(self.player_names, key=lambda p: self.golf_scores[p])
                self.show_winner(winner)
                return
        
        self.show_golf_game()
