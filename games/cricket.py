import tkinter as tk
from constants import COLORS


class CricketMixin:
    """Mixin för Cricket-spel"""

    def start_cricket_game(self):
        """Starta Cricket-spel"""
        self.cricket_targets = [20, 19, 18, 17, 16, 15, 25]
        self.cricket_marks = {name: {t: 0 for t in self.cricket_targets} for name in self.player_names}
        self.cricket_scores = {name: 0 for name in self.player_names}
        self.current_player_index = 0
        self.history = []
        self.show_cricket_game()

    def show_cricket_game(self):
        """Visa Cricket-spelskärmen"""
        self.clear()
        self.current_dart = 1
        self.dart_details = []
        self.multiplier = 1

        # Scoreboard top (kompakt layout)
        top = tk.Frame(self.root, bg=COLORS['panel'])
        top.place(x=0, y=0, width=self.W, height=self.sy(105))

        # Headers - använd mindre font och packa tätare
        tk.Label(top, text="", bg=COLORS['panel'], width=5, font=("Arial", 8)).grid(row=0, column=0, pady=0)
        for i, name in enumerate(self.player_names):
            is_current = i == self.current_player_index
            fg = COLORS['gold'] if is_current else COLORS['text']
            tk.Label(top, text=name[:5], font=("Arial", 8, "bold"),
                    fg=fg, bg=COLORS['panel'], width=6).grid(row=0, column=i+1, pady=0)

        # Target rows (kompakt)
        for row, target in enumerate(self.cricket_targets):
            label = "Bull" if target == 25 else str(target)
            tk.Label(top, text=label, font=("Arial", 8, "bold"),
                    fg=COLORS['accent'], bg=COLORS['panel'], width=5).grid(row=row+1, column=0, pady=0, ipady=0)
            
            for i, name in enumerate(self.player_names):
                marks = self.cricket_marks[name][target]
                mark_text = self._get_cricket_mark_text(marks)
                is_closed = self._is_cricket_target_closed(target)
                fg = COLORS['green'] if marks >= 3 else COLORS['text']
                if is_closed:
                    fg = COLORS['accent2']
                tk.Label(top, text=mark_text, font=("Arial", 8),
                        fg=fg, bg=COLORS['panel'], width=6).grid(row=row+1, column=i+1, pady=0, ipady=0)

        # Scores row
        tk.Label(top, text="Poäng", font=("Arial", 8, "bold"),
                fg=COLORS['gold'], bg=COLORS['panel'], width=5).grid(row=8, column=0, pady=0)
        for i, name in enumerate(self.player_names):
            is_current = i == self.current_player_index
            fg = COLORS['gold'] if is_current else COLORS['text']
            tk.Label(top, text=str(self.cricket_scores[name]), font=("Arial", 9, "bold"),
                    fg=fg, bg=COLORS['panel'], width=6).grid(row=8, column=i+1, pady=0)

        # Dart info
        info = tk.Frame(self.root, bg=COLORS['bg'])
        info.place(x=0, y=self.sy(105), width=self.W, height=self.sy(20))
        self.dart_label = tk.Label(info, text="Pil 1", font=("Arial", 18, "bold"),
                                   fg=COLORS['green'], bg=COLORS['bg'])
        self.dart_label.place(x=self.sx(5), y=0)
        self.thrown_label = tk.Label(info, text="", font=("Arial", 9),
                                     fg=COLORS['text'], bg=COLORS['bg'])
        self.thrown_label.place(x=self.sx(55), y=0)

        # Multiplier
        multi = tk.Frame(self.root, bg=COLORS['bg'])
        multi.place(x=self.sx(5), y=self.sy(125), width=self.sx(470), height=self.sy(28))
        self.multi_buttons = []
        for i, (txt, m) in enumerate([("Single", 1), ("Double", 2), ("Triple", 3)]):
            btn = tk.Button(multi, text=txt, font=("Arial", 10, "bold"),
                           bg=COLORS['accent'] if m == 1 else COLORS['button'],
                           fg=COLORS['text'], relief="flat",
                           command=lambda mm=m: self.set_multiplier(mm))
            btn.grid(row=0, column=i, sticky="nsew", padx=2)
            multi.columnconfigure(i, weight=1)
            self.multi_buttons.append(btn)

        # Target buttons (only cricket numbers)
        grid = tk.Frame(self.root, bg=COLORS['bg'])
        grid.place(x=self.sx(5), y=self.sy(155), width=self.sx(470), height=self.sy(105))
        
        targets_row1 = [20, 19, 18, 17]
        targets_row2 = [16, 15]
        
        for c, t in enumerate(targets_row1):
            btn = tk.Button(grid, text=str(t), font=("Arial", 14, "bold"),
                           bg=COLORS['button'], fg=COLORS['text'], relief="flat",
                           command=lambda v=t: self.cricket_hit(v))
            btn.grid(row=0, column=c, sticky="nsew", padx=2, pady=2)
            grid.columnconfigure(c, weight=1)
        
        for c, t in enumerate(targets_row2):
            btn = tk.Button(grid, text=str(t), font=("Arial", 14, "bold"),
                           bg=COLORS['button'], fg=COLORS['text'], relief="flat",
                           command=lambda v=t: self.cricket_hit(v))
            btn.grid(row=1, column=c, sticky="nsew", padx=2, pady=2)
        
        # Bull button
        btn = tk.Button(grid, text="Bull", font=("Arial", 14, "bold"),
                       bg=COLORS['button'], fg=COLORS['text'], relief="flat",
                       command=lambda: self.cricket_hit(25))
        btn.grid(row=1, column=2, columnspan=2, sticky="nsew", padx=2, pady=2)
        
        grid.rowconfigure(0, weight=1)
        grid.rowconfigure(1, weight=1)

        # Special buttons
        special = tk.Frame(self.root, bg=COLORS['bg'])
        special.place(x=self.sx(5), y=self.sy(265), width=self.sx(470), height=self.sy(50))
        
        btns = [("Miss", 0), ("Ångra", -1), ("Klar", -2), ("?", -3), ("✕", -4)]
        for i, (txt, val) in enumerate(btns):
            if val == -1:
                cmd = self.cricket_undo
                bg = COLORS['accent2']
            elif val == -2:
                cmd = self.cricket_finish_round
                bg = COLORS['green']
            elif val == -3:
                cmd = lambda: self.show_help('cricket', self.show_cricket_game)
                bg = COLORS['accent2']
            elif val == -4:
                cmd = self.show_game_select
                bg = COLORS['accent2']
            else:
                cmd = lambda: self.cricket_hit(0)
                bg = COLORS['button']
            btn = tk.Button(special, text=txt, font=("Arial", 12, "bold"),
                           bg=bg, fg=COLORS['text'], relief="flat", command=cmd)
            btn.grid(row=0, column=i, sticky="nsew", padx=2, pady=2)
            special.columnconfigure(i, weight=1)

    def _get_cricket_mark_text(self, marks):
        """Hämta text för antal markeringar"""
        if marks == 0:
            return ""
        elif marks == 1:
            return "/"
        elif marks == 2:
            return "X"
        else:
            return "Ⓧ"

    def _is_cricket_target_closed(self, target):
        """Kolla om alla spelare stängt ett mål"""
        return all(self.cricket_marks[name][target] >= 3 for name in self.player_names)

    def cricket_hit(self, value):
        """Registrera en Cricket-träff"""
        if self.current_dart > 3:
            return
        
        if value == 0:
            self.dart_details.append((0, 1))
        elif value in self.cricket_targets:
            mult = min(self.multiplier, 2) if value == 25 else self.multiplier
            self.dart_details.append((value, mult))
        else:
            self.dart_details.append((0, 1))

        self.current_dart += 1
        self._update_cricket_thrown()
        
        if self.current_dart > 3:
            self.cricket_finish_round()
        else:
            self.dart_label.config(text=f"Pil {self.current_dart}")
            self.set_multiplier(1)

    def _update_cricket_thrown(self):
        """Uppdatera visning av kastade pilar"""
        parts = []
        for val, mult in self.dart_details:
            if val == 0:
                parts.append("Miss")
            elif val == 25:
                parts.append("D-Bull" if mult == 2 else "Bull")
            elif mult == 3:
                parts.append(f"T{val}")
            elif mult == 2:
                parts.append(f"D{val}")
            else:
                parts.append(str(val))
        self.thrown_label.config(text=" ".join(parts))

    def cricket_undo(self):
        """Ångra senaste Cricket-pilen"""
        if self.dart_details:
            self.dart_details.pop()
            self.current_dart -= 1
            self.dart_label.config(text=f"Pil {self.current_dart}")
            self._update_cricket_thrown()

    def cricket_finish_round(self):
        """Avsluta Cricket-rundan"""
        player = self.player_names[self.current_player_index]
        
        for val, mult in self.dart_details:
            if val == 0 or val not in self.cricket_targets:
                continue
                
            marks_to_add = mult
            current_marks = self.cricket_marks[player][val]
            
            new_marks = min(current_marks + marks_to_add, 3)
            self.cricket_marks[player][val] = new_marks
            
            if current_marks >= 3 and not self._is_cricket_target_closed(val):
                points = val * mult if val != 25 else (25 if mult == 1 else 50)
                self.cricket_scores[player] += points
            elif current_marks < 3:
                marks_used = new_marks - current_marks
                marks_for_points = marks_to_add - marks_used
                if marks_for_points > 0 and not self._is_cricket_target_closed(val):
                    points = val * marks_for_points if val != 25 else (25 if marks_for_points == 1 else 50 * marks_for_points // 2)
                    self.cricket_scores[player] += points

        if self._check_cricket_winner():
            return

        self.current_player_index = (self.current_player_index + 1) % self.num_players
        self.show_cricket_game()

    def _check_cricket_winner(self):
        """Kolla om någon vunnit Cricket"""
        for name in self.player_names:
            all_closed = all(self.cricket_marks[name][t] >= 3 for t in self.cricket_targets)
            if all_closed:
                player_score = self.cricket_scores[name]
                is_highest = all(player_score >= self.cricket_scores[other] 
                               for other in self.player_names)
                if is_highest:
                    self.show_winner(name)
                    return True
        return False
