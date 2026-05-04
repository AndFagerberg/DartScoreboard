import tkinter as tk
from constants import COLORS


class HalveItMixin:
    """Mixin för Halve It-spel"""

    def start_halveit_game(self):
        """Starta Halve It-spel"""
        # Standardrundor: 20, 19, 18, Doubles, 17, 16, 15, Triples, Bull
        self.halveit_targets = [
            ('20', 20, None),
            ('19', 19, None),
            ('18', 18, None),
            ('Doubles', None, 2),  # Valfri double
            ('17', 17, None),
            ('16', 16, None),
            ('15', 15, None),
            ('Triples', None, 3),  # Valfri triple
            ('Bull', 25, None),
        ]
        self.halveit_round = 0
        self.halveit_scores = {name: 40 for name in self.player_names}  # Startpoäng
        self.halveit_round_details = {name: [] for name in self.player_names}
        self.current_player_index = 0
        self.show_halveit_game()

    def show_halveit_game(self):
        """Visa Halve It-spelskärmen"""
        self.clear()
        self.current_dart = 1
        self.dart_details = []
        self.multiplier = 1
        self.round_score = 0

        target_name, target_num, target_mult = self.halveit_targets[self.halveit_round]

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
            tk.Label(frame, text=str(self.halveit_scores[name]), font=("Arial", 16, "bold"),
                    fg=fg, bg=COLORS['panel']).pack()

        # Info
        info = tk.Frame(self.root, bg=COLORS['bg'])
        info.place(x=0, y=self.sy(55), width=self.W, height=self.sy(40))
        
        round_text = f"Runda {self.halveit_round + 1}/9: {target_name}"
        tk.Label(info, text=round_text, font=("Arial", 14, "bold"),
                fg=COLORS['gold'], bg=COLORS['bg']).pack()
        
        self.dart_label = tk.Label(info, text=f"Pil {self.current_dart}", font=("Arial", 18, "bold"),
                                   fg=COLORS['green'], bg=COLORS['bg'])
        self.dart_label.place(x=self.sx(5), y=self.sy(5))
        
        self.thrown_label = tk.Label(info, text="", font=("Arial", 10),
                                    fg=COLORS['text'], bg=COLORS['bg'])
        self.thrown_label.place(x=self.sx(60), y=self.sy(22))

        # Multiplier (om inte specifik multiplikator krävs)
        multi = tk.Frame(self.root, bg=COLORS['bg'])
        multi.place(x=self.sx(5), y=self.sy(95), width=self.sx(470), height=self.sy(30))
        
        self.multi_buttons = []
        for i, (txt, m) in enumerate([("Single", 1), ("Double", 2), ("Triple", 3)]):
            active = target_mult is None or target_mult == m
            btn = tk.Button(multi, text=txt, font=("Arial", 10, "bold"),
                           bg=COLORS['accent'] if m == 1 else COLORS['button'],
                           fg=COLORS['text'] if active else COLORS['accent2'],
                           relief="flat",
                           state="normal" if active else "disabled",
                           command=lambda mm=m: self.set_multiplier(mm))
            btn.grid(row=0, column=i, sticky="nsew", padx=2)
            multi.columnconfigure(i, weight=1)
            self.multi_buttons.append(btn)

        # Knappar - beror på vad målet är
        grid = tk.Frame(self.root, bg=COLORS['bg'])
        grid.place(x=self.sx(5), y=self.sy(130), width=self.sx(470), height=self.sy(130))

        if target_num is not None:
            # Specifikt nummer
            target_btn = tk.Button(grid, text=str(target_num), font=("Arial", 36, "bold"),
                                  bg=COLORS['accent'], fg=COLORS['text'], relief="flat",
                                  command=lambda: self.halveit_hit(target_num))
            target_btn.place(x=self.sx(50), y=self.sy(10), width=self.sx(180), height=self.sy(110))
            
            miss_btn = tk.Button(grid, text="Miss", font=("Arial", 18, "bold"),
                                bg=COLORS['button'], fg=COLORS['text'], relief="flat",
                                command=lambda: self.halveit_hit(0))
            miss_btn.place(x=self.sx(250), y=self.sy(10), width=self.sx(180), height=self.sy(110))
        else:
            # Valfritt nummer (doubles eller triples)
            num = 1
            for r in range(4):
                for c in range(5):
                    if num <= 20:
                        btn = tk.Button(grid, text=str(num), font=("Arial", 11, "bold"),
                                       bg=COLORS['button'], fg=COLORS['text'], relief="flat",
                                       command=lambda v=num: self.halveit_hit(v))
                        btn.grid(row=r, column=c, sticky="nsew", padx=1, pady=1)
                        num += 1
                grid.rowconfigure(r, weight=1)
            for c in range(5):
                grid.columnconfigure(c, weight=1)

        # Special buttons
        special = tk.Frame(self.root, bg=COLORS['bg'])
        special.place(x=self.sx(5), y=self.sy(265), width=self.sx(470), height=self.sy(50))
        
        btns = [("Miss", lambda: self.halveit_hit(0), COLORS['button'])]
        if target_num is None:
            btns.insert(0, ("Bull", lambda: self.halveit_hit(25), COLORS['button']))
        btns.extend([
            ("Ångra", self.halveit_undo, COLORS['accent2']),
            ("Klar", self.halveit_finish_round, COLORS['green']),
            ("?", lambda: self.show_help('halveit', self.show_halveit_game), COLORS['accent2']),
            ("✕", self.show_game_select, COLORS['accent2'])
        ])
        
        for i, (txt, cmd, bg) in enumerate(btns):
            btn = tk.Button(special, text=txt, font=("Arial", 11, "bold"),
                           bg=bg, fg=COLORS['text'], relief="flat", command=cmd)
            btn.grid(row=0, column=i, sticky="nsew", padx=2, pady=2)
            special.columnconfigure(i, weight=1)

    def halveit_hit(self, value):
        """Registrera en Halve It-träff"""
        if self.current_dart > 3:
            return
        
        target_name, target_num, target_mult = self.halveit_targets[self.halveit_round]
        
        # Kolla om träffen är giltig för målet
        valid = False
        score = 0
        
        if value == 0:
            valid = False
            score = 0
        elif target_num is not None:
            # Specifikt nummer
            if value == target_num:
                valid = True
                score = value * self.multiplier
        else:
            # Valfritt nummer med specifik multiplikator
            if self.multiplier == target_mult:
                valid = True
                score = value * self.multiplier
        
        self.dart_details.append((value, self.multiplier, valid, score))
        self.round_score += score
        self.current_dart += 1
        self._update_halveit_display()
        
        if self.current_dart > 3:
            self.halveit_finish_round()
        else:
            self.dart_label.config(text=f"Pil {self.current_dart}")
            self.set_multiplier(1)

    def _update_halveit_display(self):
        """Uppdatera visning"""
        parts = []
        for val, mult, valid, score in self.dart_details:
            if val == 0:
                parts.append("Miss")
            elif valid:
                if mult == 3:
                    parts.append(f"T{val}✓")
                elif mult == 2:
                    parts.append(f"D{val}✓")
                else:
                    parts.append(f"{val}✓")
            else:
                parts.append(f"({val})")
        
        self.thrown_label.config(text=" ".join(parts) + f" = {self.round_score}" if parts else "")

    def halveit_undo(self):
        """Ångra senaste Halve It-pilen"""
        if self.dart_details:
            _, _, _, score = self.dart_details.pop()
            self.round_score -= score
            self.current_dart -= 1
            self.dart_label.config(text=f"Pil {self.current_dart}")
            self._update_halveit_display()

    def halveit_finish_round(self):
        """Avsluta Halve It-rundan"""
        player = self.player_names[self.current_player_index]
        
        # Kolla om någon giltig träff
        any_valid = any(valid for _, _, valid, _ in self.dart_details)
        
        target_name = self.halveit_targets[self.halveit_round][0]
        if any_valid:
            self.halveit_scores[player] += self.round_score
            self.halveit_round_details[player].append((target_name, self.round_score, self.halveit_scores[player]))
        else:
            # Halvera poängen!
            old = self.halveit_scores[player]
            self.halveit_scores[player] //= 2
            self.halveit_round_details[player].append((target_name, -(old - self.halveit_scores[player]), self.halveit_scores[player]))

        # Nästa spelare
        self.current_player_index = (self.current_player_index + 1) % self.num_players
        
        # Om alla spelat, nästa runda
        if self.current_player_index == 0:
            self.halveit_round += 1
            
            if self.halveit_round >= len(self.halveit_targets):
                # Högst poäng vinner
                winner = max(self.player_names, key=lambda p: self.halveit_scores[p])
                self.show_winner(winner)
                return
        
        self.show_halveit_game()
