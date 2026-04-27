import tkinter as tk
from constants import COLORS


class ClockMixin:
    """Mixin för Around the Clock-spel"""

    def start_clock_game(self):
        """Starta Around the Clock-spel"""
        self.clock_position = {name: 1 for name in self.player_names}
        self.clock_include_bull = True
        self.current_player_index = 0
        self.history = []
        self.show_clock_game()

    def show_clock_game(self):
        """Visa Around the Clock-spelskärmen"""
        self.clear()
        self.current_dart = 1
        self.dart_details = []
        self.multiplier = 1

        # Top: player progress
        top = tk.Frame(self.root, bg=COLORS['panel'])
        top.place(x=0, y=0, width=self.W, height=self.sy(60))

        for i, name in enumerate(self.player_names):
            x = self.sx(5) + i * (self.sx(470) // self.num_players)
            width = (self.sx(470) // self.num_players) - self.sx(5)
            
            frame = tk.Frame(top, bg=COLORS['panel'])
            frame.place(x=x, y=self.sy(5), width=width, height=self.sy(50))
            
            is_current = i == self.current_player_index
            fg = COLORS['gold'] if is_current else COLORS['text']
            
            tk.Label(frame, text=name[:8], font=("Arial", 10, "bold"),
                    fg=fg, bg=COLORS['panel']).pack()
            
            pos = self.clock_position[name]
            target_text = "Bull" if pos == 21 else f"Siktar: {pos}"
            if pos > 21:
                target_text = "KLAR!"
            tk.Label(frame, text=target_text, font=("Arial", 14, "bold"),
                    fg=COLORS['accent'] if is_current else COLORS['text'],
                    bg=COLORS['panel']).pack()

        # Current target highlight
        current_player = self.player_names[self.current_player_index]
        target = self.clock_position[current_player]
        if target <= 20:
            target_text = f"Träffa {target}!"
        elif target == 21:
            target_text = "Träffa Bull!"
        else:
            target_text = "Du är klar!"
        
        info = tk.Frame(self.root, bg=COLORS['bg'])
        info.place(x=0, y=self.sy(60), width=self.W, height=self.sy(35))
        tk.Label(info, text=target_text, font=("Arial", 16, "bold"),
                fg=COLORS['gold'], bg=COLORS['bg']).pack()
        
        self.dart_label = tk.Label(info, text=f"Pil {self.current_dart}", font=("Arial", 10),
                                   fg=COLORS['green'], bg=COLORS['bg'])
        self.dart_label.place(x=self.sx(5), y=self.sy(5))

        # Number grid (highlight current target)
        grid = tk.Frame(self.root, bg=COLORS['bg'])
        grid.place(x=self.sx(5), y=self.sy(100), width=self.sx(470), height=self.sy(160))

        num = 1
        for r in range(4):
            for c in range(5):
                if num <= 20:
                    is_target = num == target
                    bg = COLORS['accent'] if is_target else COLORS['button']
                    btn = tk.Button(grid, text=str(num), font=("Arial", 12, "bold"),
                                   bg=bg, fg=COLORS['text'], relief="flat",
                                   command=lambda v=num: self.clock_hit(v))
                    btn.grid(row=r, column=c, sticky="nsew", padx=1, pady=1)
                    num += 1
            grid.rowconfigure(r, weight=1)
        for c in range(5):
            grid.columnconfigure(c, weight=1)

        # Special buttons
        special = tk.Frame(self.root, bg=COLORS['bg'])
        special.place(x=self.sx(5), y=self.sy(265), width=self.sx(470), height=self.sy(50))

        is_bull_target = target == 21
        bull_bg = COLORS['accent'] if is_bull_target else COLORS['button']
        
        btns = [
            ("Miss", lambda: self.clock_hit(0), COLORS['button']),
            ("Bull", lambda: self.clock_hit(25), bull_bg),
            ("Ångra", self.clock_undo, COLORS['accent2']),
            ("Klar", self.clock_finish_round, COLORS['green']),
            ("?", lambda: self.show_help('around_the_clock', self.show_clock_game), COLORS['accent2']),
            ("✕", self.show_game_select, COLORS['accent2'])
        ]
        for i, (txt, cmd, bg) in enumerate(btns):
            btn = tk.Button(special, text=txt, font=("Arial", 12, "bold"),
                           bg=bg, fg=COLORS['text'], relief="flat", command=cmd)
            btn.grid(row=0, column=i, sticky="nsew", padx=2, pady=2)
            special.columnconfigure(i, weight=1)

    def clock_hit(self, value):
        """Registrera en Around the Clock-träff"""
        if self.current_dart > 3:
            return
        
        self.dart_details.append(value)
        self.current_dart += 1
        
        if self.current_dart > 3:
            self.clock_finish_round()
        else:
            self.dart_label.config(text=f"Pil {self.current_dart}")

    def clock_undo(self):
        """Ångra senaste Around the Clock-pilen"""
        if self.dart_details:
            self.dart_details.pop()
            self.current_dart -= 1
            self.dart_label.config(text=f"Pil {self.current_dart}")

    def clock_finish_round(self):
        """Avsluta Around the Clock-rundan"""
        player = self.player_names[self.current_player_index]
        target = self.clock_position[player]
        
        for val in self.dart_details:
            if target > 21:
                break
            
            if target <= 20 and val == target:
                self.clock_position[player] += 1
                target = self.clock_position[player]
            elif target == 21 and val == 25:
                self.clock_position[player] = 22

        if self.clock_position[player] > 21:
            self.show_winner(player)
            return

        self.current_player_index = (self.current_player_index + 1) % self.num_players
        self.show_clock_game()
