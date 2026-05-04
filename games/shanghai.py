import tkinter as tk
from constants import COLORS


class ShanghaiMixin:
    """Mixin för Shanghai-spel"""

    def start_shanghai_game(self):
        """Starta Shanghai-spel"""
        self.shanghai_round = 1  # Runda 1-20
        self.shanghai_scores = {name: 0 for name in self.player_names}
        self.shanghai_round_scores = {name: [] for name in self.player_names}
        self.current_player_index = 0
        self.show_shanghai_game()

    def show_shanghai_game(self):
        """Visa Shanghai-spelskärmen"""
        self.clear()
        self.current_dart = 1
        self.dart_details = []
        self.multiplier = 1
        self.round_hits = {'single': False, 'double': False, 'triple': False}

        target = self.shanghai_round

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
            tk.Label(frame, text=str(self.shanghai_scores[name]), font=("Arial", 16, "bold"),
                    fg=fg, bg=COLORS['panel']).pack()

        # Info
        info = tk.Frame(self.root, bg=COLORS['bg'])
        info.place(x=0, y=self.sy(55), width=self.W, height=self.sy(40))
        
        tk.Label(info, text=f"Runda {target} av 20 - Sikta på {target}!", font=("Arial", 14, "bold"),
                fg=COLORS['gold'], bg=COLORS['bg']).pack()
        
        self.dart_label = tk.Label(info, text=f"Pil {self.current_dart}", font=("Arial", 18, "bold"),
                                   fg=COLORS['green'], bg=COLORS['bg'])
        self.dart_label.place(x=self.sx(5), y=self.sy(5))
        
        self.thrown_label = tk.Label(info, text="", font=("Arial", 10),
                                    fg=COLORS['text'], bg=COLORS['bg'])
        self.thrown_label.place(x=self.sx(60), y=self.sy(22))

        # Shanghai-indikator
        self.shanghai_label = tk.Label(info, text="", font=("Arial", 10, "bold"),
                                       fg=COLORS['accent'], bg=COLORS['bg'])
        self.shanghai_label.place(x=self.sx(350), y=self.sy(5))

        # Multiplier
        multi = tk.Frame(self.root, bg=COLORS['bg'])
        multi.place(x=self.sx(5), y=self.sy(95), width=self.sx(470), height=self.sy(30))
        
        self.multi_buttons = []
        for i, (txt, m) in enumerate([("Single", 1), ("Double", 2), ("Triple", 3)]):
            btn = tk.Button(multi, text=txt, font=("Arial", 10, "bold"),
                           bg=COLORS['accent'] if m == 1 else COLORS['button'],
                           fg=COLORS['text'], relief="flat",
                           command=lambda mm=m: self.set_multiplier(mm))
            btn.grid(row=0, column=i, sticky="nsew", padx=2)
            multi.columnconfigure(i, weight=1)
            self.multi_buttons.append(btn)

        # Stora knappar för nuvarande mål + miss
        grid = tk.Frame(self.root, bg=COLORS['bg'])
        grid.place(x=self.sx(5), y=self.sy(130), width=self.sx(470), height=self.sy(130))
        
        # Huvudknapp för målet
        target_btn = tk.Button(grid, text=str(target), font=("Arial", 36, "bold"),
                              bg=COLORS['accent'], fg=COLORS['text'], relief="flat",
                              command=lambda: self.shanghai_hit(target))
        target_btn.place(x=self.sx(50), y=self.sy(10), width=self.sx(180), height=self.sy(110))
        
        # Miss-knapp
        miss_btn = tk.Button(grid, text="Miss", font=("Arial", 18, "bold"),
                            bg=COLORS['button'], fg=COLORS['text'], relief="flat",
                            command=lambda: self.shanghai_hit(0))
        miss_btn.place(x=self.sx(250), y=self.sy(10), width=self.sx(180), height=self.sy(110))

        # Special buttons
        special = tk.Frame(self.root, bg=COLORS['bg'])
        special.place(x=self.sx(5), y=self.sy(265), width=self.sx(470), height=self.sy(50))
        
        btns = [
            ("Ångra", self.shanghai_undo, COLORS['accent2']),
            ("Klar", self.shanghai_finish_round, COLORS['green']),
            ("?", lambda: self.show_help('shanghai', self.show_shanghai_game), COLORS['accent2']),
            ("✕", self.show_game_select, COLORS['accent2'])
        ]
        for i, (txt, cmd, bg) in enumerate(btns):
            btn = tk.Button(special, text=txt, font=("Arial", 12, "bold"),
                           bg=bg, fg=COLORS['text'], relief="flat", command=cmd)
            btn.grid(row=0, column=i, sticky="nsew", padx=2, pady=2)
            special.columnconfigure(i, weight=1)

    def shanghai_hit(self, value):
        """Registrera en Shanghai-träff"""
        if self.current_dart > 3:
            return
        
        target = self.shanghai_round
        
        if value == target:
            self.dart_details.append((value, self.multiplier))
            # Spåra för Shanghai
            if self.multiplier == 1:
                self.round_hits['single'] = True
            elif self.multiplier == 2:
                self.round_hits['double'] = True
            elif self.multiplier == 3:
                self.round_hits['triple'] = True
        else:
            self.dart_details.append((0, 1))  # Miss
        
        self.current_dart += 1
        self._update_shanghai_display()
        
        if self.current_dart > 3:
            self.shanghai_finish_round()
        else:
            self.dart_label.config(text=f"Pil {self.current_dart}")
            self.set_multiplier(1)

    def _update_shanghai_display(self):
        """Uppdatera visning"""
        parts = []
        score = 0
        for val, mult in self.dart_details:
            if val == 0:
                parts.append("Miss")
            else:
                score += val * mult
                if mult == 3:
                    parts.append(f"T{val}")
                elif mult == 2:
                    parts.append(f"D{val}")
                else:
                    parts.append(str(val))
        
        self.thrown_label.config(text=" + ".join(parts) + f" = {score}" if parts else "")
        
        # Shanghai-check
        if self.round_hits['single'] and self.round_hits['double'] and self.round_hits['triple']:
            self.shanghai_label.config(text="SHANGHAI!")
        else:
            hits = []
            if self.round_hits['single']:
                hits.append("S")
            if self.round_hits['double']:
                hits.append("D")
            if self.round_hits['triple']:
                hits.append("T")
            self.shanghai_label.config(text=" ".join(hits))

    def shanghai_undo(self):
        """Ångra senaste Shanghai-pilen"""
        if self.dart_details:
            val, mult = self.dart_details.pop()
            self.current_dart -= 1
            
            # Uppdatera hits
            if val != 0:
                if mult == 1:
                    self.round_hits['single'] = False
                elif mult == 2:
                    self.round_hits['double'] = False
                elif mult == 3:
                    self.round_hits['triple'] = False
            
            self.dart_label.config(text=f"Pil {self.current_dart}")
            self._update_shanghai_display()

    def shanghai_finish_round(self):
        """Avsluta Shanghai-rundan"""
        player = self.player_names[self.current_player_index]
        
        # Räkna poäng
        round_score = sum(val * mult for val, mult in self.dart_details)
        self.shanghai_scores[player] += round_score
        self.shanghai_round_scores[player].append(round_score)
        
        # Kolla Shanghai (instant win)
        if self.round_hits['single'] and self.round_hits['double'] and self.round_hits['triple']:
            self.show_winner(player)
            return

        # Nästa spelare
        self.current_player_index = (self.current_player_index + 1) % self.num_players
        
        # Om alla spelat, nästa runda
        if self.current_player_index == 0:
            self.shanghai_round += 1
            
            # Kolla om spelet är slut (20 rundor)
            if self.shanghai_round > 20:
                # Högst poäng vinner
                winner = max(self.player_names, key=lambda p: self.shanghai_scores[p])
                self.show_winner(winner)
                return
        
        self.show_shanghai_game()
