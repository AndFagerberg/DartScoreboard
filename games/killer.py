import tkinter as tk
import random
from constants import COLORS


class KillerMixin:
    """Mixin för Killer-spel"""

    def start_killer_game(self, triple_mode=False, hits_mode=False):
        """Starta Killer-spel"""
        self.killer_triple_mode = triple_mode
        self.killer_hits_mode = hits_mode
        if hits_mode:
            self.killer_required_mult = None  # alla träffar räknas
            self.killer_prefix = ""
        elif triple_mode:
            self.killer_required_mult = 3
            self.killer_prefix = "T"
        else:
            self.killer_required_mult = 2
            self.killer_prefix = "D"
        # Varje spelare behöver ett nummer (1-20)
        available = list(range(1, 21))
        random.shuffle(available)
        
        self.killer_numbers = {name: available[i] for i, name in enumerate(self.player_names)}
        self.killer_lives = {name: 3 for name in self.player_names}
        self.killer_status = {name: False for name in self.player_names}  # True = är killer
        if hits_mode:
            self.killer_progress = {name: 0 for name in self.player_names}  # 0-3 träffar mot killer
        self.current_player_index = 0
        self.eliminated_players = []
        self.show_killer_game()

    def show_killer_game(self):
        """Visa Killer-spelskärmen"""
        self.clear()
        self.current_dart = 1
        self.dart_details = []
        self.multiplier = 1

        # Top: spelarinfo
        top = tk.Frame(self.root, bg=COLORS['panel'])
        top.place(x=0, y=0, width=self.W, height=self.sy(70))

        # Visa alla spelare med status
        for i, name in enumerate(self.player_names):
            x = self.sx(5) + i * (self.sx(470) // self.num_players)
            width = (self.sx(470) // self.num_players) - self.sx(5)
            
            frame = tk.Frame(top, bg=COLORS['panel'])
            frame.place(x=x, y=self.sy(2), width=width, height=self.sy(65))
            
            is_current = i == self.current_player_index
            is_eliminated = name in self.eliminated_players
            is_killer = self.killer_status[name]
            
            # Namn
            fg = COLORS['accent2'] if is_eliminated else (COLORS['gold'] if is_current else COLORS['text'])
            tk.Label(frame, text=name[:6], font=("Arial", 9, "bold"),
                    fg=fg, bg=COLORS['panel']).pack()
            
            # Nummer och status
            num = self.killer_numbers[name]
            status = "☠" if is_killer else "○"
            if is_eliminated:
                status = "✗"
            prefix = self.killer_prefix
            if self.killer_hits_mode and not is_killer and not is_eliminated:
                progress = self.killer_progress[name]
                status = f"{'●' * progress}{'○' * (3 - progress)}"
            tk.Label(frame, text=f"{prefix}{num} {status}", font=("Arial", 10, "bold"),
                    fg=COLORS['red'] if is_killer else COLORS['text'],
                    bg=COLORS['panel']).pack()
            
            # Liv
            lives = self.killer_lives[name]
            lives_text = "♥" * lives + "♡" * (3 - lives)
            tk.Label(frame, text=lives_text, font=("Arial", 10),
                    fg=COLORS['red'], bg=COLORS['panel']).pack()

        # Info
        current_player = self.player_names[self.current_player_index]
        is_killer = self.killer_status[current_player]
        
        info = tk.Frame(self.root, bg=COLORS['bg'])
        info.place(x=0, y=self.sy(70), width=self.W, height=self.sy(30))
        
        mult_name = "tripplar" if self.killer_triple_mode else "doubles"
        if self.killer_hits_mode:
            if is_killer:
                info_text = "Du är KILLER! Träffa andras nummer!"
            else:
                num = self.killer_numbers[current_player]
                progress = self.killer_progress[current_player]
                info_text = f"Träffa {num} ({progress}/3) - RÖR EJ andras!"
        elif is_killer:
            info_text = f"Du är KILLER! Träffa andras {mult_name}!"
        else:
            num = self.killer_numbers[current_player]
            info_text = f"Träffa {self.killer_prefix}{num} för att bli killer!"
        
        tk.Label(info, text=info_text, font=("Arial", 11, "bold"),
                fg=COLORS['gold'], bg=COLORS['bg']).pack()

        self.dart_label = tk.Label(info, text=f"Pil {self.current_dart}", font=("Arial", 18, "bold"),
                                   fg=COLORS['green'], bg=COLORS['bg'])
        self.dart_label.place(x=self.sx(5), y=self.sy(5))

        # Number grid
        grid = tk.Frame(self.root, bg=COLORS['bg'])
        grid.place(x=self.sx(5), y=self.sy(105), width=self.sx(470), height=self.sy(155))

        num = 1
        for r in range(4):
            for c in range(5):
                if num <= 20:
                    # Markera eget och andras nummer
                    bg = COLORS['button']
                    if num == self.killer_numbers[current_player]:
                        bg = COLORS['accent'] if not is_killer else COLORS['button']
                    elif is_killer:
                        # Visa andras nummer som mål
                        for other in self.player_names:
                            if other != current_player and other not in self.eliminated_players:
                                if num == self.killer_numbers[other]:
                                    bg = COLORS['red']
                    
                    btn = tk.Button(grid, text=str(num), font=("Arial", 12, "bold"),
                                   bg=bg, fg=COLORS['text'], relief="flat",
                                   command=lambda v=num: self.killer_hit(v))
                    btn.grid(row=r, column=c, sticky="nsew", padx=1, pady=1)
                    num += 1
            grid.rowconfigure(r, weight=1)
        for c in range(5):
            grid.columnconfigure(c, weight=1)

        # Multiplier (endast double spelar roll i Killer)
        multi = tk.Frame(self.root, bg=COLORS['bg'])
        multi.place(x=self.sx(5), y=self.sy(262), width=self.sx(230), height=self.sy(30))
        
        self.multi_buttons = []
        for i, (txt, m) in enumerate([("Single", 1), ("Double", 2), ("Triple", 3)]):
            btn = tk.Button(multi, text=txt, font=("Arial", 9, "bold"),
                           bg=COLORS['accent'] if m == 1 else COLORS['button'],
                           fg=COLORS['text'], relief="flat",
                           command=lambda mm=m: self.set_multiplier(mm))
            btn.grid(row=0, column=i, sticky="nsew", padx=1)
            multi.columnconfigure(i, weight=1)
            self.multi_buttons.append(btn)

        # Special buttons
        special = tk.Frame(self.root, bg=COLORS['bg'])
        special.place(x=self.sx(240), y=self.sy(262), width=self.sx(235), height=self.sy(55))
        
        btns = [
            ("Miss", lambda: self.killer_hit(0), COLORS['button']),
            ("Ångra", self.killer_undo, COLORS['accent2']),
            ("Klar", self.killer_finish_round, COLORS['green']),
            ("?", lambda: self.show_help('hits_killer' if self.killer_hits_mode else ('triple_killer' if self.killer_triple_mode else 'killer'), self.show_killer_game), COLORS['accent2']),
            ("✕", self.show_game_select, COLORS['accent2'])
        ]
        for i, (txt, cmd, bg) in enumerate(btns):
            btn = tk.Button(special, text=txt, font=("Arial", 10, "bold"),
                           bg=bg, fg=COLORS['text'], relief="flat", command=cmd)
            btn.grid(row=0, column=i, sticky="nsew", padx=1, pady=1)
            special.columnconfigure(i, weight=1)

    def killer_hit(self, value):
        """Registrera en Killer-träff"""
        if self.current_dart > 3:
            return
        
        self.dart_details.append((value, self.multiplier))
        self.current_dart += 1
        
        if self.current_dart > 3:
            self.killer_finish_round()
        else:
            self.dart_label.config(text=f"Pil {self.current_dart}")
            self.set_multiplier(1)

    def killer_undo(self):
        """Ångra senaste Killer-pilen"""
        if self.dart_details:
            self.dart_details.pop()
            self.current_dart -= 1
            self.dart_label.config(text=f"Pil {self.current_dart}")

    def killer_finish_round(self):
        """Avsluta Killer-rundan"""
        player = self.player_names[self.current_player_index]
        my_number = self.killer_numbers[player]
        is_killer = self.killer_status[player]
        
        if self.killer_hits_mode:
            self._killer_finish_hits_mode(player, my_number, is_killer)
        else:
            self._killer_finish_standard(player, my_number, is_killer)

        # Kolla om spelaren blev eliminerad (hits mode)
        if player in self.eliminated_players:
            active_players = [p for p in self.player_names if p not in self.eliminated_players]
            if len(active_players) == 1:
                self.show_winner(active_players[0])
                return

        # Kolla vinnare
        active_players = [p for p in self.player_names if p not in self.eliminated_players]
        if len(active_players) == 1:
            self.show_winner(active_players[0])
            return

        # Nästa spelare (hoppa över eliminerade)
        self.current_player_index = (self.current_player_index + 1) % self.num_players
        while self.player_names[self.current_player_index] in self.eliminated_players:
            self.current_player_index = (self.current_player_index + 1) % self.num_players
        
        self.show_killer_game()

    def _killer_finish_standard(self, player, my_number, is_killer):
        """Standard Killer (double/triple mode)"""
        for val, mult in self.dart_details:
            if val == 0:
                continue
            
            # Endast rätt multiplier räknas
            if mult != self.killer_required_mult:
                continue
            
            if not is_killer:
                if val == my_number:
                    self.killer_status[player] = True
                    is_killer = True
            else:
                for other in self.player_names:
                    if other != player and other not in self.eliminated_players:
                        if val == self.killer_numbers[other]:
                            self.killer_lives[other] -= 1
                            if self.killer_lives[other] <= 0:
                                self.eliminated_players.append(other)

    def _killer_finish_hits_mode(self, player, my_number, is_killer):
        """Hits Killer — alla träffar räknas, multiplier = antal hits"""
        for val, mult in self.dart_details:
            if val == 0:
                continue
            
            if not is_killer:
                if val == my_number:
                    # Träffar sitt eget nummer — bygger progress
                    self.killer_progress[player] = min(3, self.killer_progress[player] + mult)
                    if self.killer_progress[player] >= 3:
                        self.killer_status[player] = True
                        is_killer = True
                else:
                    # Kolla om man träffade någon annans nummer
                    for other in self.player_names:
                        if other != player and other not in self.eliminated_players:
                            if val == self.killer_numbers[other]:
                                # Inte killer ännu — du är ute!
                                self.eliminated_players.append(player)
                                return
            else:
                # Är killer — attackera andra
                for other in self.player_names:
                    if other != player and other not in self.eliminated_players:
                        if val == self.killer_numbers[other]:
                            self.killer_lives[other] -= mult
                            if self.killer_lives[other] <= 0:
                                self.eliminated_players.append(other)
