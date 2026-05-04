import tkinter as tk
from constants import COLORS, PRESET_NAMES, GAME_HELP
from games import X01Mixin, CricketMixin, ClockMixin, KillerMixin, ShanghaiMixin, HalveItMixin, HighScoreMixin, GolfMixin
from results_store import save_result, get_leaderboard, get_player_stats, get_all_results, get_head_to_head, get_form_data


class DartApp(X01Mixin, CricketMixin, ClockMixin, KillerMixin, ShanghaiMixin, HalveItMixin, HighScoreMixin, GolfMixin):
    """Huvudapplikation för Dart Scoreboard"""

    def __init__(self, root, fullscreen=False, resolution=None):
        self.root = root
        self.root.title("Dart Scoreboard")
        self.root.configure(bg=COLORS['bg'])
        if fullscreen:
            if resolution:
                self.W, self.H = resolution
            else:
                self.root.update()
                self.W = self.root.winfo_screenwidth()
                self.H = self.root.winfo_screenheight()
            self.root.geometry(f"{self.W}x{self.H}+0+0")
            self.root.overrideredirect(True)
            self.root.attributes('-fullscreen', True)
        else:
            self.W = resolution[0] if resolution else 480
            self.H = resolution[1] if resolution else 320
            self.root.geometry(f"{self.W}x{self.H}")
            self.root.resizable(False, False)

        self.num_players = 0
        self.start_score = 501
        self.double_out = True
        self.game_mode = 'x01'
        self.players = {}
        self.player_names = []
        self.player_stats = {}
        self.current_player_index = 0
        self.history = []

        self.show_player_select()

    def clear(self):
        """Rensa skärmen"""
        for w in self.root.winfo_children():
            w.destroy()

    def sx(self, v):
        """Skala x-värde från 480-bas till aktuell bredd"""
        return int(v * self.W / 480)

    def sy(self, v):
        """Skala y-värde från 320-bas till aktuell höjd"""
        return int(v * self.H / 320)

    def styled_button(self, parent, text, command, width=None, bg=None, fg=None):
        """Skapa en stilad knapp"""
        btn = tk.Button(parent, text=text, command=command,
                       font=("Arial", 14, "bold"),
                       bg=bg or COLORS['button'],
                       fg=fg or COLORS['text'],
                       activebackground=COLORS['button_active'],
                       activeforeground=COLORS['text'],
                       relief="flat", bd=0)
        if width:
            btn.config(width=width)
        return btn

    def styled_label(self, parent, text, font_size=14, fg=None, bg=None):
        """Skapa en stilad label"""
        return tk.Label(parent, text=text,
                       font=("Arial", font_size, "bold"),
                       fg=fg or COLORS['text'],
                       bg=bg or COLORS['bg'])

    def show_help(self, game_type, return_callback):
        """Visa hjälp-popup för ett spel"""
        self.clear()
        
        help_data = GAME_HELP.get(game_type, GAME_HELP['all'])
        
        # Titel (fast position)
        self.styled_label(self.root, help_data['title'], 14, COLORS['gold']).place(x=self.sx(10), y=self.sy(5))
        
        # Stäng-knapp (fast position längst upp till höger)
        close_btn = self.styled_button(self.root, "✕ Stäng", return_callback, bg=COLORS['accent'])
        close_btn.config(font=("Arial", 11, "bold"))
        close_btn.place(x=self.sx(380), y=self.sy(5), width=self.sx(90), height=self.sy(30))
        
        # Scrollbar hjälptext med Canvas
        canvas_frame = tk.Frame(self.root, bg=COLORS['panel'])
        canvas_frame.place(x=self.sx(10), y=self.sy(40), width=self.sx(460), height=self.sy(270))
        
        canvas = tk.Canvas(canvas_frame, bg=COLORS['panel'], highlightthickness=0)
        scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=COLORS['panel'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=self.sx(440))
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Hjälptext
        help_label = tk.Label(scrollable_frame, text=help_data['text'],
                             font=("Arial", 10),
                             fg=COLORS['text'], bg=COLORS['panel'],
                             justify="left", anchor="nw",
                             wraplength=self.sx(420))
        help_label.pack(fill="both", expand=True, padx=10, pady=10)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Touch-scroll (swipe up/down)
        def on_touch_scroll(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", on_touch_scroll)

    # ============================================
    # MENYER
    # ============================================

    def show_player_select(self):
        """Visa val av antal spelare"""
        self.clear()
        self.styled_label(self.root, "Dart Scoreboard", 28, COLORS['accent']).pack(pady=5)
        self.styled_label(self.root, "Antal spelare", 16).pack(pady=5)

        frame = tk.Frame(self.root, bg=COLORS['bg'])
        frame.pack(pady=10)
        for i in range(1, 5):
            btn = self.styled_button(frame, str(i), lambda n=i: self.set_players(n))
            btn.config(width=5, height=2)
            btn.grid(row=0, column=i-1, padx=5)

        stats_btn = self.styled_button(self.root, "📊 Statistik", self.show_stats_menu,
                                        bg=COLORS['accent2'])
        stats_btn.config(font=("Arial", 12, "bold"))
        stats_btn.pack(pady=15)

    def set_players(self, n):
        """Sätt antal spelare"""
        self.num_players = n
        self.show_name_entry()

    def show_name_entry(self):
        """Starta namnval"""
        self.clear()
        # Default namn: Albin för spelare 1, Andreas för spelare 2
        default_names = ["Albin", "Andreas", "Spelare 1", "Spelare 2"]
        self.player_names = [default_names[i] for i in range(self.num_players)]
        self.current_name_index = 0
        self.name_scroll_index = 0
        self.show_name_picker()

    def show_name_picker(self):
        """Visa namnväljare"""
        self.clear()
        idx = self.current_name_index
        self.styled_label(self.root, f"Välj namn för spelare {idx + 1}", 16).pack(pady=5)

        current_name = self.player_names[idx]
        self.name_display = tk.Label(self.root, text=current_name,
                                     font=("Arial", 20, "bold"),
                                     fg=COLORS['gold'], bg=COLORS['panel'],
                                     width=15, height=1)
        self.name_display.pack(pady=5)

        nav_frame = tk.Frame(self.root, bg=COLORS['bg'])
        nav_frame.pack(pady=5)
        
        self.styled_button(nav_frame, "◀", self.scroll_names_left).grid(row=0, column=0, padx=5)
        self.styled_button(nav_frame, "▶", self.scroll_names_right).grid(row=0, column=1, padx=5)

        self.name_grid = tk.Frame(self.root, bg=COLORS['bg'])
        self.name_grid.pack(pady=5)
        self.update_name_grid()

        btn_frame = tk.Frame(self.root, bg=COLORS['bg'])
        btn_frame.pack(pady=10)

        if idx > 0:
            self.styled_button(btn_frame, "← Tillbaka", self.prev_player_name).grid(row=0, column=0, padx=10)
        
        if idx < self.num_players - 1:
            self.styled_button(btn_frame, "Nästa →", self.next_player_name).grid(row=0, column=1, padx=10)
        else:
            btn = self.styled_button(btn_frame, "Starta!", self.show_game_select, bg=COLORS['green'])
            btn.grid(row=0, column=1, padx=10)

    def update_name_grid(self):
        """Uppdatera namnrutnätet"""
        for w in self.name_grid.winfo_children():
            w.destroy()

        start = self.name_scroll_index
        names_to_show = PRESET_NAMES[start:start + 6]

        for i, name in enumerate(names_to_show):
            row, col = i // 3, i % 3
            is_selected = name == self.player_names[self.current_name_index]
            bg = COLORS['accent'] if is_selected else COLORS['button']
            
            btn = tk.Button(self.name_grid, text=name, font=("Arial", 11, "bold"),
                           bg=bg, fg=COLORS['text'],
                           activebackground=COLORS['button_active'],
                           relief="flat", width=10,
                           command=lambda n=name: self.select_name(n))
            btn.grid(row=row, column=col, padx=3, pady=3)

    def scroll_names_left(self):
        """Scrolla namn vänster"""
        if self.name_scroll_index > 0:
            self.name_scroll_index -= 3
            self.update_name_grid()

    def scroll_names_right(self):
        """Scrolla namn höger"""
        if self.name_scroll_index + 6 < len(PRESET_NAMES):
            self.name_scroll_index += 3
            self.update_name_grid()

    def select_name(self, name):
        """Välj ett namn"""
        self.player_names[self.current_name_index] = name
        self.name_display.config(text=name)
        self.update_name_grid()

    def prev_player_name(self):
        """Gå till föregående spelare"""
        self.current_name_index -= 1
        self.name_scroll_index = 0
        self.show_name_picker()

    def next_player_name(self):
        """Gå till nästa spelare"""
        self.current_name_index += 1
        self.name_scroll_index = 0
        self.show_name_picker()

    def show_game_select(self):
        """Visa spelval"""
        self.clear()
        
        # Titel med tillbaka- och hjälp-knapp
        title_frame = tk.Frame(self.root, bg=COLORS['bg'])
        title_frame.pack(pady=5, fill="x")
        back_btn = self.styled_button(title_frame, "← Tillbaka", self.show_player_select,
                                      bg=COLORS['accent2'])
        back_btn.config(font=("Arial", 10, "bold"))
        back_btn.pack(side="left", padx=10)
        self.styled_label(title_frame, "Välj spel", 18).pack(side="left", expand=True)
        help_btn = self.styled_button(title_frame, "?", 
                                      lambda: self.show_help('all', self.show_game_select),
                                      bg=COLORS['accent2'])
        help_btn.config(width=2, height=1, font=("Arial", 12, "bold"))
        help_btn.pack(side="right", padx=10)

        # X01 games
        x01_frame = tk.Frame(self.root, bg=COLORS['bg'])
        x01_frame.pack(pady=5)
        
        x01_header = tk.Frame(x01_frame, bg=COLORS['bg'])
        x01_header.grid(row=0, column=0, columnspan=4)
        self.styled_label(x01_header, "X01", 12, COLORS['accent']).pack(side="left")
        x01_help = self.styled_button(x01_header, "?",
                                      lambda: self.show_help('x01', self.show_game_select),
                                      bg=COLORS['accent2'])
        x01_help.config(width=2, font=("Arial", 9))
        x01_help.pack(side="left", padx=5)
        
        for i, g in enumerate([301, 501, 701]):
            btn = self.styled_button(x01_frame, str(g), lambda s=g: self.set_x01_game(s))
            btn.config(width=6, height=1, font=("Arial", 12, "bold"))
            btn.grid(row=1, column=i, padx=5, pady=2)

        self.double_out_var = tk.BooleanVar(value=True)
        tk.Checkbutton(x01_frame, text="Double Out",
                      variable=self.double_out_var,
                      font=("Arial", 10),
                      fg=COLORS['text'], bg=COLORS['bg'],
                      selectcolor=COLORS['panel'],
                      activebackground=COLORS['bg'],
                      activeforeground=COLORS['text']).grid(row=2, column=0, columnspan=4)

        # Other games
        other_frame = tk.Frame(self.root, bg=COLORS['bg'])
        other_frame.pack(pady=5)
        
        self.styled_label(other_frame, "Andra spel", 12, COLORS['accent']).pack()
        
        # Game buttons in centered rows (3 per rad)
        games = [
            ("Cricket", self.start_cricket, 'cricket'),
            ("Klockan", self.start_around_the_clock, 'around_the_clock'),
            ("Shanghai", self.start_shanghai, 'shanghai'),
            ("Killer", self.start_killer, 'killer'),
            ("T.Killer", self.start_triple_killer, 'triple_killer'),
            ("H.Killer", self.start_hits_killer, 'hits_killer'),
            ("Halve It", self.start_halveit, 'halveit'),
            ("High Score", self.start_highscore, 'highscore'),
            ("Golf", self.start_golf, 'golf'),
        ]
        
        rows = []
        for r in range(3):
            row_frame = tk.Frame(other_frame, bg=COLORS['bg'])
            row_frame.pack(pady=1)
            rows.append(row_frame)
        
        for i, (name, cmd, help_key) in enumerate(games):
            parent = rows[i // 3]
            
            game_frame = tk.Frame(parent, bg=COLORS['bg'])
            game_frame.pack(side="left", padx=3)
            
            btn = self.styled_button(game_frame, name, cmd)
            btn.config(width=8, height=1, font=("Arial", 10, "bold"))
            btn.pack(side="left")
            
            help_btn = self.styled_button(game_frame, "?",
                                          lambda k=help_key: self.show_help(k, self.show_game_select),
                                          bg=COLORS['accent2'])
            help_btn.config(width=2, font=("Arial", 8))
            help_btn.pack(side="left", padx=1)

    def set_x01_game(self, score):
        """Starta X01-spel"""
        self.start_score = score
        self.double_out = self.double_out_var.get()
        self.game_mode = 'x01'
        self.start_game()

    def start_cricket(self):
        """Starta Cricket"""
        self.game_mode = 'cricket'
        self.start_cricket_game()

    def start_around_the_clock(self):
        """Starta Around the Clock"""
        self.game_mode = 'around_the_clock'
        self.start_clock_game()

    def start_killer(self):
        """Starta Killer"""
        self.game_mode = 'killer'
        self.start_killer_game()

    def start_triple_killer(self):
        """Starta Triple Killer"""
        self.game_mode = 'triple_killer'
        self.start_killer_game(triple_mode=True)

    def start_hits_killer(self):
        """Starta Hits Killer"""
        self.game_mode = 'hits_killer'
        self.start_killer_game(hits_mode=True)

    def start_shanghai(self):
        """Starta Shanghai"""
        self.game_mode = 'shanghai'
        self.start_shanghai_game()

    def start_halveit(self):
        """Starta Halve It"""
        self.game_mode = 'halveit'
        self.start_halveit_game()

    def start_highscore(self):
        """Starta High Score"""
        self.game_mode = 'highscore'
        self.start_highscore_game()

    def start_golf(self):
        """Starta Golf"""
        self.game_mode = 'golf'
        self.start_golf_game()

    # ============================================
    # VINNARE
    # ============================================

    def _collect_game_result(self, winner):
        """Samla ihop spelresultat för alla spelare."""
        result = {}
        for name in self.player_names:
            data = {"winner": name == winner}
            if self.game_mode == 'x01':
                stats = self.player_stats.get(name, {})
                data["remaining"] = self.players.get(name, 0)
                data["darts"] = stats.get("darts", 0)
                data["total_score"] = stats.get("total", 0)
                data["rounds"] = stats.get("rounds", 0)
                data["start_score"] = self.start_score
                data["double_out"] = self.double_out
            elif self.game_mode == 'cricket':
                data["score"] = self.cricket_scores.get(name, 0)
            elif self.game_mode == 'around_the_clock':
                data["position"] = self.clock_position.get(name, 1)
            elif self.game_mode in ('killer', 'triple_killer', 'hits_killer'):
                data["lives"] = self.killer_lives.get(name, 0)
                data["was_killer"] = self.killer_status.get(name, False)
                data["eliminated"] = name in self.eliminated_players
            elif self.game_mode == 'shanghai':
                data["score"] = self.shanghai_scores.get(name, 0)
                data["round_scores"] = self.shanghai_round_scores.get(name, [])
            elif self.game_mode == 'halveit':
                data["score"] = self.halveit_scores.get(name, 0)
                data["round_details"] = self.halveit_round_details.get(name, [])
            elif self.game_mode == 'highscore':
                data["score"] = self.highscore_scores.get(name, 0)
                data["round_scores"] = self.highscore_round_scores.get(name, [])
            elif self.game_mode == 'golf':
                data["score"] = self.golf_scores.get(name, 0)
                data["hole_scores"] = self.golf_hole_scores.get(name, [])
            result[name] = data
        return result

    def show_winner(self, player):
        """Visa vinnaren med detaljerad resultatvy"""
        # Spara resultatet
        player_results = self._collect_game_result(player)
        save_result(self.game_mode, player, list(self.player_names), player_results)

        self.clear()

        # Header med vinnare och knappar
        header = tk.Frame(self.root, bg=COLORS['panel'])
        header.place(x=0, y=0, width=self.W, height=self.sy(55))

        tk.Label(header, text=f"🏆 {player} VANN!", font=("Arial", 18, "bold"),
                fg=COLORS['gold'], bg=COLORS['panel']).place(x=self.sx(10), y=self.sy(5))

        game_label = self.GAME_LABELS.get(self.game_mode, self.game_mode)
        tk.Label(header, text=game_label, font=("Arial", 10),
                fg=COLORS['text'], bg=COLORS['panel']).place(x=self.sx(10), y=self.sy(32))

        btn_frame = tk.Frame(header, bg=COLORS['panel'])
        btn_frame.place(x=self.sx(300), y=self.sy(5), width=self.sx(170), height=self.sy(45))
        
        replay_btn = self.styled_button(btn_frame, "Igen", self.replay_game, bg=COLORS['green'])
        replay_btn.config(font=("Arial", 10, "bold"))
        replay_btn.pack(side="left", padx=3)
        
        menu_btn = self.styled_button(btn_frame, "Meny", self.show_player_select, bg=COLORS['accent2'])
        menu_btn.config(font=("Arial", 10, "bold"))
        menu_btn.pack(side="left", padx=3)

        # Scrollbart resultatområde
        canvas_frame = tk.Frame(self.root, bg=COLORS['bg'])
        canvas_frame.place(x=0, y=self.sy(55), width=self.W, height=self.sy(265))

        canvas = tk.Canvas(canvas_frame, bg=COLORS['bg'], highlightthickness=0)
        scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        scrollable = tk.Frame(canvas, bg=COLORS['bg'])

        scrollable.bind("<Configure>",
                        lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        canvas.create_window((0, 0), window=scrollable, anchor="nw", width=self.sx(460))
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        def on_touch_scroll(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", on_touch_scroll)

        # Bygg resultatinnehåll
        self._build_result_content(scrollable, player)

    def _build_result_content(self, parent, winner):
        """Bygg detaljerat resultatinnehåll beroende på speltyp"""
        # Slutställning
        tk.Label(parent, text="Slutställning", font=("Arial", 14, "bold"),
                fg=COLORS['accent'], bg=COLORS['bg']).pack(anchor="w", padx=10, pady=(10, 5))

        standings = self._get_standings(winner)
        for i, (name, info_text) in enumerate(standings):
            is_winner = name == winner
            row = tk.Frame(parent, bg=COLORS['panel'] if i % 2 == 0 else COLORS['bg'])
            row.pack(fill="x", padx=10, pady=1)

            prefix = "🏆" if is_winner else f"  {i+1}."
            fg = COLORS['gold'] if is_winner else COLORS['text']
            tk.Label(row, text=f"{prefix} {name}", font=("Arial", 12, "bold"),
                    fg=fg, bg=row.cget('bg')).pack(side="left", padx=5, pady=3)
            tk.Label(row, text=info_text, font=("Arial", 11),
                    fg=COLORS['text'], bg=row.cget('bg')).pack(side="right", padx=5, pady=3)

        # Spelspecifika detaljer
        if self.game_mode == 'x01':
            self._build_x01_details(parent)
        elif self.game_mode == 'cricket':
            self._build_cricket_details(parent)
        elif self.game_mode == 'around_the_clock':
            self._build_clock_details(parent)
        elif self.game_mode in ('killer', 'triple_killer', 'hits_killer'):
            self._build_killer_details(parent)
        elif self.game_mode == 'shanghai':
            self._build_shanghai_details(parent)
        elif self.game_mode == 'halveit':
            self._build_halveit_details(parent)
        elif self.game_mode == 'highscore':
            self._build_highscore_details(parent)
        elif self.game_mode == 'golf':
            self._build_golf_details(parent)

    def _get_standings(self, winner):
        """Hämta slutställning baserat på speltyp"""
        if self.game_mode == 'x01':
            sorted_players = sorted(self.player_names,
                                   key=lambda p: (p != winner, self.players.get(p, 0)))
            return [(p, f"{self.players[p]} kvar | {self.player_stats[p]['darts']} pilar | "
                       f"Snitt: {self.player_stats[p]['total']/max(self.player_stats[p]['rounds'],1):.1f}")
                    for p in sorted_players]
        elif self.game_mode == 'cricket':
            sorted_players = sorted(self.player_names,
                                   key=lambda p: (p != winner, -self.cricket_scores.get(p, 0)))
            return [(p, f"{self.cricket_scores.get(p, 0)} poäng") for p in sorted_players]
        elif self.game_mode == 'around_the_clock':
            sorted_players = sorted(self.player_names,
                                   key=lambda p: (p != winner, -self.clock_position.get(p, 1)))
            return [(p, f"Position: {'Klar!' if self.clock_position[p] > 21 else self.clock_position[p]}")
                    for p in sorted_players]
        elif self.game_mode in ('killer', 'triple_killer', 'hits_killer'):
            sorted_players = sorted(self.player_names,
                                   key=lambda p: (p != winner, -self.killer_lives.get(p, 0)))
            return [(p, f"{'♥' * self.killer_lives[p]}{'♡' * (3 - self.killer_lives[p])} "
                       f"Nr: {self.killer_numbers[p]}") for p in sorted_players]
        elif self.game_mode == 'shanghai':
            sorted_players = sorted(self.player_names,
                                   key=lambda p: (p != winner, -self.shanghai_scores.get(p, 0)))
            return [(p, f"{self.shanghai_scores.get(p, 0)} poäng") for p in sorted_players]
        elif self.game_mode == 'halveit':
            sorted_players = sorted(self.player_names,
                                   key=lambda p: (p != winner, -self.halveit_scores.get(p, 0)))
            return [(p, f"{self.halveit_scores.get(p, 0)} poäng") for p in sorted_players]
        elif self.game_mode == 'highscore':
            sorted_players = sorted(self.player_names,
                                   key=lambda p: (p != winner, -self.highscore_scores.get(p, 0)))
            return [(p, f"{self.highscore_scores.get(p, 0)} poäng") for p in sorted_players]
        elif self.game_mode == 'golf':
            sorted_players = sorted(self.player_names,
                                   key=lambda p: (p != winner, self.golf_scores.get(p, 0)))
            return [(p, f"{self.golf_scores.get(p, 0)} slag") for p in sorted_players]
        return [(p, "") for p in self.player_names]

    def _build_round_table(self, parent, title, headers, rows):
        """Hjälpmetod för att bygga en tabell med runddata"""
        tk.Label(parent, text=title, font=("Arial", 13, "bold"),
                fg=COLORS['accent'], bg=COLORS['bg']).pack(anchor="w", padx=10, pady=(15, 5))

        # Header-rad
        header_frame = tk.Frame(parent, bg=COLORS['accent2'])
        header_frame.pack(fill="x", padx=10)
        for i, h in enumerate(headers):
            tk.Label(header_frame, text=h, font=("Arial", 9, "bold"),
                    fg=COLORS['gold'], bg=COLORS['accent2'],
                    width=max(6, len(h)+1)).pack(side="left", padx=2, pady=2)

        # Data-rader
        for r_idx, row_data in enumerate(rows):
            row_frame = tk.Frame(parent, bg=COLORS['panel'] if r_idx % 2 == 0 else COLORS['bg'])
            row_frame.pack(fill="x", padx=10)
            for i, cell in enumerate(row_data):
                w = max(6, len(headers[i])+1) if i < len(headers) else 6
                tk.Label(row_frame, text=str(cell), font=("Arial", 9),
                        fg=COLORS['text'], bg=row_frame.cget('bg'),
                        width=w).pack(side="left", padx=2, pady=1)

    def _build_x01_details(self, parent):
        """X01-specifika detaljer"""
        # Statistik per spelare
        tk.Label(parent, text="Statistik", font=("Arial", 13, "bold"),
                fg=COLORS['accent'], bg=COLORS['bg']).pack(anchor="w", padx=10, pady=(15, 5))

        for name in self.player_names:
            stats = self.player_stats.get(name, {'darts': 0, 'total': 0, 'rounds': 0})
            rounds = max(stats['rounds'], 1)
            avg = stats['total'] / rounds
            frame = tk.Frame(parent, bg=COLORS['panel'])
            frame.pack(fill="x", padx=10, pady=1)
            tk.Label(frame, text=name, font=("Arial", 10, "bold"),
                    fg=COLORS['gold'], bg=COLORS['panel']).pack(side="left", padx=5, pady=2)
            tk.Label(frame, text=f"Rundor: {stats['rounds']}  Pilar: {stats['darts']}  "
                               f"Totalt: {stats['total']}  Snitt/runda: {avg:.1f}",
                    font=("Arial", 9), fg=COLORS['text'], bg=COLORS['panel']).pack(side="left", padx=5, pady=2)

        # Rundhistorik
        if self.history:
            headers = ["Runda", "Spelare", "Pilar", "Poäng", "Kvar"]
            rows = []
            round_num = 0
            prev_player = None
            for h in self.history:
                if h['player'] != prev_player or prev_player == self.player_names[0]:
                    if h['player'] == self.player_names[0]:
                        round_num += 1
                prev_player = h['player']
                darts_str = " ".join(
                    f"{'T' if m==3 else 'D' if m==2 else ''}{v if v > 0 else 'Miss'}"
                    for v, m in h.get('darts', [])
                )
                remaining = h['old_score'] - h['total']
                rows.append([round_num, h['player'][:6], darts_str, h['total'], remaining])
            self._build_round_table(parent, "Rundhistorik", headers, rows)

    def _build_cricket_details(self, parent):
        """Cricket-specifika detaljer"""
        targets_labels = {20: "20", 19: "19", 18: "18", 17: "17", 16: "16", 15: "15", 25: "Bull"}
        headers = ["Mål"] + [n[:6] for n in self.player_names]
        rows = []
        for target in self.cricket_targets:
            row = [targets_labels[target]]
            for name in self.player_names:
                marks = self.cricket_marks[name][target]
                mark_sym = ["", "/", "X", "Ⓧ"][min(marks, 3)]
                row.append(mark_sym)
            rows.append(row)
        # Poängrad
        rows.append(["Poäng"] + [str(self.cricket_scores.get(n, 0)) for n in self.player_names])
        self._build_round_table(parent, "Markeringar", headers, rows)

    def _build_clock_details(self, parent):
        """Clock-specifika detaljer"""
        tk.Label(parent, text="Slutpositioner", font=("Arial", 13, "bold"),
                fg=COLORS['accent'], bg=COLORS['bg']).pack(anchor="w", padx=10, pady=(15, 5))

        for name in self.player_names:
            pos = self.clock_position.get(name, 1)
            pos_text = "Klar! (Bull)" if pos > 21 else f"Position {pos} av 21"
            frame = tk.Frame(parent, bg=COLORS['panel'])
            frame.pack(fill="x", padx=10, pady=1)
            tk.Label(frame, text=name, font=("Arial", 10, "bold"),
                    fg=COLORS['gold'], bg=COLORS['panel']).pack(side="left", padx=5, pady=2)
            tk.Label(frame, text=pos_text, font=("Arial", 10),
                    fg=COLORS['green'] if pos > 21 else COLORS['text'],
                    bg=COLORS['panel']).pack(side="right", padx=5, pady=2)

    def _build_killer_details(self, parent):
        """Killer-specifika detaljer"""
        tk.Label(parent, text="Spelardetaljer", font=("Arial", 13, "bold"),
                fg=COLORS['accent'], bg=COLORS['bg']).pack(anchor="w", padx=10, pady=(15, 5))

        for name in self.player_names:
            lives = self.killer_lives.get(name, 0)
            num = self.killer_numbers.get(name, "?")
            was_killer = self.killer_status.get(name, False)
            eliminated = name in self.eliminated_players

            frame = tk.Frame(parent, bg=COLORS['panel'])
            frame.pack(fill="x", padx=10, pady=1)
            tk.Label(frame, text=name, font=("Arial", 10, "bold"),
                    fg=COLORS['gold'], bg=COLORS['panel']).pack(side="left", padx=5, pady=2)

            status_parts = [f"Nr: {self.killer_prefix}{num}"]
            status_parts.append(f"{'♥' * lives}{'♡' * (3 - lives)}")
            if was_killer:
                status_parts.append("Killer")
            if eliminated:
                status_parts.append("Eliminerad")
            tk.Label(frame, text="  |  ".join(status_parts), font=("Arial", 9),
                    fg=COLORS['red'] if eliminated else COLORS['text'],
                    bg=COLORS['panel']).pack(side="right", padx=5, pady=2)

    def _build_shanghai_details(self, parent):
        """Shanghai-specifika detaljer"""
        if not hasattr(self, 'shanghai_round_scores'):
            return
        round_count = max(len(scores) for scores in self.shanghai_round_scores.values()) if self.shanghai_round_scores else 0
        if round_count == 0:
            return

        headers = ["Runda"] + [n[:6] for n in self.player_names]
        rows = []
        totals = {n: 0 for n in self.player_names}
        for r in range(round_count):
            row = [str(r + 1)]
            for name in self.player_names:
                scores = self.shanghai_round_scores.get(name, [])
                val = scores[r] if r < len(scores) else "-"
                if isinstance(val, int):
                    totals[name] += val
                row.append(str(val))
            rows.append(row)
        # Totalrad
        rows.append(["Totalt"] + [str(totals[n]) for n in self.player_names])
        self._build_round_table(parent, "Poäng per runda", headers, rows)

    def _build_halveit_details(self, parent):
        """Halve It-specifika detaljer"""
        if not hasattr(self, 'halveit_round_details'):
            return
        round_count = max(len(d) for d in self.halveit_round_details.values()) if self.halveit_round_details else 0
        if round_count == 0:
            return

        headers = ["Runda"] + [n[:6] for n in self.player_names]
        rows = []
        for r in range(round_count):
            first_detail = None
            for name in self.player_names:
                details = self.halveit_round_details.get(name, [])
                if r < len(details):
                    first_detail = details[r]
                    break
            round_name = first_detail[0] if first_detail else f"R{r+1}"
            row = [round_name]
            for name in self.player_names:
                details = self.halveit_round_details.get(name, [])
                if r < len(details):
                    target, delta, total = details[r]
                    if delta < 0:
                        row.append(f"½→{total}")
                    else:
                        row.append(f"+{delta}→{total}")
                else:
                    row.append("-")
            rows.append(row)
        self._build_round_table(parent, "Runddetaljer", headers, rows)

    def _build_highscore_details(self, parent):
        """High Score-specifika detaljer"""
        headers = ["Runda"] + [n[:6] for n in self.player_names]
        rows = []
        round_count = max(len(s) for s in self.highscore_round_scores.values()) if self.highscore_round_scores else 0
        totals = {n: 0 for n in self.player_names}
        for r in range(round_count):
            row = [str(r + 1)]
            for name in self.player_names:
                scores = self.highscore_round_scores.get(name, [])
                val = scores[r] if r < len(scores) else "-"
                if isinstance(val, int):
                    totals[name] += val
                row.append(str(val))
            rows.append(row)
        rows.append(["Totalt"] + [str(totals[n]) for n in self.player_names])
        self._build_round_table(parent, "Poäng per runda", headers, rows)

    def _build_golf_details(self, parent):
        """Golf-specifika detaljer"""
        headers = ["Hål"] + [n[:6] for n in self.player_names]
        rows = []
        hole_count = max(len(s) for s in self.golf_hole_scores.values()) if self.golf_hole_scores else 0
        totals = {n: 0 for n in self.player_names}
        for h in range(hole_count):
            row = [str(h + 1)]
            for name in self.player_names:
                scores = self.golf_hole_scores.get(name, [])
                val = scores[h] if h < len(scores) else "-"
                if isinstance(val, int):
                    totals[name] += val
                row.append(str(val))
            rows.append(row)
        rows.append(["Totalt"] + [str(totals[n]) for n in self.player_names])
        self._build_round_table(parent, "Slag per hål", headers, rows)

    def replay_game(self):
        """Starta om samma speltyp"""
        if self.game_mode == 'x01':
            self.start_game()
        elif self.game_mode == 'cricket':
            self.start_cricket_game()
        elif self.game_mode == 'around_the_clock':
            self.start_clock_game()
        elif self.game_mode == 'killer':
            self.start_killer_game()
        elif self.game_mode == 'triple_killer':
            self.start_killer_game(triple_mode=True)
        elif self.game_mode == 'hits_killer':
            self.start_killer_game(hits_mode=True)
        elif self.game_mode == 'shanghai':
            self.start_shanghai_game()
        elif self.game_mode == 'halveit':
            self.start_halveit_game()
        elif self.game_mode == 'highscore':
            self.start_highscore_game()
        elif self.game_mode == 'golf':
            self.start_golf_game()

    # ============================================
    # STATISTIK / RAPPORTER
    # ============================================

    GAME_LABELS = {
        'x01': 'X01',
        'cricket': 'Cricket',
        'around_the_clock': 'Klockan',
        'killer': 'Killer',
        'triple_killer': 'T.Killer',
        'hits_killer': 'H.Killer',
        'shanghai': 'Shanghai',
        'halveit': 'Halve It',
        'highscore': 'High Score',
        'golf': 'Golf',
    }

    def show_stats_menu(self):
        """Visa statistik-meny"""
        self.clear()

        title_frame = tk.Frame(self.root, bg=COLORS['bg'])
        title_frame.pack(pady=5, fill="x")
        back_btn = self.styled_button(title_frame, "← Tillbaka", self.show_player_select,
                                      bg=COLORS['accent2'])
        back_btn.config(font=("Arial", 10, "bold"))
        back_btn.pack(side="left", padx=10)
        self.styled_label(title_frame, "📊 Statistik", 18).pack(side="left", expand=True)

        btn_frame = tk.Frame(self.root, bg=COLORS['bg'])
        btn_frame.pack(pady=20)

        buttons = [
            ("Topplista", self.show_leaderboard),
            ("Senaste matcher", self.show_recent_matches),
            ("Spelarstatistik", self.show_player_stats_select),
            ("Head-to-Head", self.show_h2h_select),
            ("Form & Trender", self.show_form_select),
        ]

        for i, (text, cmd) in enumerate(buttons):
            btn = self.styled_button(btn_frame, text, cmd)
            btn.config(width=18, height=1, font=("Arial", 13, "bold"))
            btn.pack(pady=4)

    def show_leaderboard(self):
        """Visa topplista"""
        self.clear()

        title_frame = tk.Frame(self.root, bg=COLORS['bg'])
        title_frame.pack(pady=5, fill="x")
        back_btn = self.styled_button(title_frame, "← Tillbaka", self.show_stats_menu,
                                      bg=COLORS['accent2'])
        back_btn.config(font=("Arial", 10, "bold"))
        back_btn.pack(side="left", padx=10)
        self.styled_label(title_frame, "🏆 Topplista", 18).pack(side="left", expand=True)

        board = get_leaderboard()

        if not board:
            self.styled_label(self.root, "Inga matcher spelade ännu.", 14).pack(pady=40)
            return

        # Scrollbart område
        canvas_frame = tk.Frame(self.root, bg=COLORS['bg'])
        canvas_frame.pack(pady=5, padx=10, fill="both", expand=True)

        canvas = tk.Canvas(canvas_frame, bg=COLORS['bg'], highlightthickness=0)
        scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        scrollable = tk.Frame(canvas, bg=COLORS['bg'])
        scrollable.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable, anchor="nw", width=self.sx(440))
        canvas.configure(yscrollcommand=scrollbar.set)

        # Tabell-header
        header = tk.Frame(scrollable, bg=COLORS['accent2'])
        header.pack(fill="x", pady=(0, 2))
        cols = [("#", 3), ("Spelare", 10), ("V", 4), ("S", 4), ("V%", 5)]
        for h, w in cols:
            tk.Label(header, text=h, font=("Arial", 11, "bold"),
                     fg=COLORS['gold'], bg=COLORS['accent2'], width=w).pack(side="left", padx=2, pady=3)

        for i, (name, wins, played, pct) in enumerate(board):
            bg = COLORS['panel'] if i % 2 == 0 else COLORS['bg']
            row = tk.Frame(scrollable, bg=bg)
            row.pack(fill="x")

            medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else f" {i+1}."
            fg = COLORS['gold'] if i == 0 else COLORS['text']
            vals = [medal, name[:10], str(wins), str(played), f"{pct:.0f}%"]
            widths = [3, 10, 4, 4, 5]
            for v, w in zip(vals, widths):
                tk.Label(row, text=v, font=("Arial", 11, "bold" if i < 3 else ""),
                         fg=fg, bg=bg, width=w).pack(side="left", padx=2, pady=2)

        # Per-spel topplista
        results = get_all_results()
        if results:
            tk.Label(scrollable, text="", bg=COLORS['bg']).pack(pady=3)
            tk.Label(scrollable, text="Per speltyp", font=("Arial", 13, "bold"),
                    fg=COLORS['accent'], bg=COLORS['bg']).pack(anchor="w", padx=5, pady=(5, 3))

            game_stats = {}
            for r in results:
                if len(r["players"]) < 2:
                    continue
                gm = r["game_mode"]
                if gm not in game_stats:
                    game_stats[gm] = {}
                for p in r["players"]:
                    if p not in game_stats[gm]:
                        game_stats[gm][p] = {"wins": 0, "played": 0}
                    game_stats[gm][p]["played"] += 1
                    if r["winner"] == p:
                        game_stats[gm][p]["wins"] += 1

            for gm in sorted(game_stats.keys()):
                label = self.GAME_LABELS.get(gm, gm)
                players = game_stats[gm]
                top = sorted(players.items(), key=lambda x: (-x[1]["wins"], -x[1]["played"]))[:3]

                gm_frame = tk.Frame(scrollable, bg=COLORS['panel'])
                gm_frame.pack(fill="x", padx=5, pady=1)
                tk.Label(gm_frame, text=label, font=("Arial", 10, "bold"),
                        fg=COLORS['accent'], bg=COLORS['panel'], width=10, anchor="w").pack(side="left", padx=5, pady=2)
                top_str = "  ".join(f"{n[:6]}({s['wins']}/{s['played']})" for n, s in top)
                tk.Label(gm_frame, text=top_str, font=("Arial", 9),
                        fg=COLORS['text'], bg=COLORS['panel']).pack(side="left", padx=5, pady=2)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))

    def show_recent_matches(self):
        """Visa senaste matcher med detaljerad info"""
        self.clear()

        title_frame = tk.Frame(self.root, bg=COLORS['bg'])
        title_frame.pack(pady=5, fill="x")
        back_btn = self.styled_button(title_frame, "← Tillbaka", self.show_stats_menu,
                                      bg=COLORS['accent2'])
        back_btn.config(font=("Arial", 10, "bold"))
        back_btn.pack(side="left", padx=10)
        self.styled_label(title_frame, "📋 Senaste matcher", 16).pack(side="left", expand=True)

        results = get_all_results()

        if not results:
            self.styled_label(self.root, "Inga matcher spelade ännu.", 14).pack(pady=40)
            return

        # Scrollbar lista
        canvas_frame = tk.Frame(self.root, bg=COLORS['bg'])
        canvas_frame.pack(pady=5, padx=5, fill="both", expand=True)

        canvas = tk.Canvas(canvas_frame, bg=COLORS['bg'], highlightthickness=0)
        scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        scrollable = tk.Frame(canvas, bg=COLORS['bg'])
        scrollable.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable, anchor="nw", width=self.sx(450))
        canvas.configure(yscrollcommand=scrollbar.set)

        for idx, r in enumerate(reversed(results[-30:])):
            ts = r["timestamp"][:16].replace("T", " ")
            game_label = self.GAME_LABELS.get(r["game_mode"], r["game_mode"])
            bg = COLORS['panel'] if idx % 2 == 0 else COLORS['bg']

            match_frame = tk.Frame(scrollable, bg=bg)
            match_frame.pack(fill="x", pady=1)

            # Rad 1: datum + speltyp + vinnare
            top_row = tk.Frame(match_frame, bg=bg)
            top_row.pack(fill="x", padx=5, pady=(3, 0))
            tk.Label(top_row, text=ts, font=("Arial", 8),
                    fg=COLORS['accent2'], bg=bg).pack(side="left")
            tk.Label(top_row, text=f"  {game_label}", font=("Arial", 10, "bold"),
                    fg=COLORS['accent'], bg=bg).pack(side="left")
            tk.Label(top_row, text=f"🏆 {r['winner']}", font=("Arial", 10, "bold"),
                    fg=COLORS['gold'], bg=bg).pack(side="right")

            # Rad 2: spelarresultat
            player_results = r.get("player_results", {})
            detail_row = tk.Frame(match_frame, bg=bg)
            detail_row.pack(fill="x", padx=5, pady=(0, 3))

            for pname in r["players"]:
                pr = player_results.get(pname, {})
                detail_text = self._format_match_player_detail(r["game_mode"], pname, pr)
                is_winner = pname == r["winner"]
                fg = COLORS['gold'] if is_winner else COLORS['text']
                tk.Label(detail_row, text=detail_text, font=("Arial", 8),
                        fg=fg, bg=bg).pack(side="left", padx=5)

            # Klickbar detalj-knapp
            match_data = r
            detail_btn = tk.Button(match_frame, text="▸", font=("Arial", 9),
                                  bg=bg, fg=COLORS['accent2'], relief="flat",
                                  command=lambda m=match_data: self.show_match_detail(m))
            detail_btn.pack(side="right", padx=5)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))

    def _format_match_player_detail(self, game_mode, player_name, pr):
        """Formatera spelardetalj för matchlistan"""
        if game_mode == 'x01':
            remaining = pr.get("remaining", "?")
            darts = pr.get("darts", 0)
            rounds = pr.get("rounds", 0)
            avg = pr.get("total_score", 0) / max(rounds, 1)
            if remaining == 0:
                return f"{player_name}: ✓ {darts}p {avg:.0f}snitt"
            return f"{player_name}: {remaining}kvar {darts}p"
        elif game_mode == 'cricket':
            return f"{player_name}: {pr.get('score', 0)}p"
        elif game_mode == 'around_the_clock':
            pos = pr.get("position", 1)
            return f"{player_name}: {'Klar' if pos > 21 else f'pos {pos}'}"
        elif game_mode in ('killer', 'triple_killer', 'hits_killer'):
            lives = pr.get("lives", 0)
            return f"{player_name}: {'♥'*lives}{'♡'*(3-lives)}"
        elif game_mode in ('shanghai', 'halveit', 'highscore'):
            return f"{player_name}: {pr.get('score', 0)}p"
        elif game_mode == 'golf':
            return f"{player_name}: {pr.get('score', 0)}slag"
        return f"{player_name}"

    def show_match_detail(self, match):
        """Visa detaljerad vy av en sparad match"""
        self.clear()

        title_frame = tk.Frame(self.root, bg=COLORS['bg'])
        title_frame.pack(pady=5, fill="x")
        back_btn = self.styled_button(title_frame, "← Tillbaka", self.show_recent_matches,
                                      bg=COLORS['accent2'])
        back_btn.config(font=("Arial", 10, "bold"))
        back_btn.pack(side="left", padx=10)

        game_label = self.GAME_LABELS.get(match["game_mode"], match["game_mode"])
        ts = match["timestamp"][:16].replace("T", " ")
        self.styled_label(title_frame, f"{game_label} - {ts}", 12).pack(side="left", expand=True)

        # Scrollbart resultat
        canvas_frame = tk.Frame(self.root, bg=COLORS['bg'])
        canvas_frame.pack(pady=5, padx=5, fill="both", expand=True)

        canvas = tk.Canvas(canvas_frame, bg=COLORS['bg'], highlightthickness=0)
        scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        scrollable = tk.Frame(canvas, bg=COLORS['bg'])
        scrollable.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable, anchor="nw", width=self.sx(450))
        canvas.configure(yscrollcommand=scrollbar.set)

        # Vinnare
        tk.Label(scrollable, text=f"🏆 {match['winner']} vann!", font=("Arial", 16, "bold"),
                fg=COLORS['gold'], bg=COLORS['bg']).pack(pady=(10, 5))

        # Spelarresultat
        player_results = match.get("player_results", {})
        players = match.get("players", [])
        game_mode = match["game_mode"]

        for i, pname in enumerate(players):
            pr = player_results.get(pname, {})
            is_winner = pname == match["winner"]
            bg = COLORS['panel']
            row = tk.Frame(scrollable, bg=bg)
            row.pack(fill="x", padx=10, pady=2)

            prefix = "🏆" if is_winner else f"  {i+1}."
            tk.Label(row, text=prefix, font=("Arial", 11), fg=COLORS['gold'],
                    bg=bg).pack(side="left", padx=3, pady=4)
            tk.Label(row, text=pname, font=("Arial", 12, "bold"),
                    fg=COLORS['gold'] if is_winner else COLORS['text'],
                    bg=bg).pack(side="left", padx=3, pady=4)

            detail = self._format_match_detail_full(game_mode, pr)
            tk.Label(row, text=detail, font=("Arial", 9),
                    fg=COLORS['text'], bg=bg).pack(side="right", padx=5, pady=4)

        # Runddata om tillgängligt
        self._build_match_round_details(scrollable, game_mode, players, player_results)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))

    def _format_match_detail_full(self, game_mode, pr):
        """Fullständig detalj per spelare för match-detalj"""
        if game_mode == 'x01':
            remaining = pr.get("remaining", "?")
            darts = pr.get("darts", 0)
            rounds = pr.get("rounds", 0)
            total = pr.get("total_score", 0)
            avg = total / max(rounds, 1)
            start = pr.get("start_score", "?")
            parts = [f"Start: {start}"]
            if remaining == 0:
                parts.append("✓ Klart")
            else:
                parts.append(f"Kvar: {remaining}")
            parts.append(f"Pilar: {darts}")
            parts.append(f"Snitt: {avg:.1f}")
            return "  |  ".join(parts)
        elif game_mode == 'cricket':
            return f"Poäng: {pr.get('score', 0)}"
        elif game_mode == 'around_the_clock':
            pos = pr.get("position", 1)
            return f"Position: {'Klar!' if pos > 21 else pos}"
        elif game_mode in ('killer', 'triple_killer', 'hits_killer'):
            lives = pr.get("lives", 0)
            elim = "Eliminerad" if pr.get("eliminated") else ""
            killer = "Killer" if pr.get("was_killer") else ""
            parts = [f"{'♥'*lives}{'♡'*(3-lives)}"]
            if killer:
                parts.append(killer)
            if elim:
                parts.append(elim)
            return "  ".join(parts)
        elif game_mode in ('shanghai', 'halveit', 'highscore'):
            return f"Poäng: {pr.get('score', 0)}"
        elif game_mode == 'golf':
            return f"Slag: {pr.get('score', 0)}"
        return ""

    def _build_match_round_details(self, parent, game_mode, players, player_results):
        """Visa runddetaljer från sparad matchdata"""
        if game_mode == 'highscore':
            self._build_saved_round_table(parent, "Poäng per runda", "Runda", players, player_results, "round_scores")
        elif game_mode == 'golf':
            self._build_saved_round_table(parent, "Slag per hål", "Hål", players, player_results, "hole_scores")
        elif game_mode == 'shanghai':
            self._build_saved_round_table(parent, "Poäng per runda", "Runda", players, player_results, "round_scores")
        elif game_mode == 'halveit':
            # Halveit har specialformat
            has_details = any("round_details" in player_results.get(p, {}) for p in players)
            if has_details:
                headers = ["Runda"] + [p[:6] for p in players]
                rows = []
                max_rounds = max(len(player_results.get(p, {}).get("round_details", [])) for p in players)
                for r in range(max_rounds):
                    round_name = ""
                    row_data = []
                    for p in players:
                        details = player_results.get(p, {}).get("round_details", [])
                        if r < len(details):
                            target, delta, total = details[r]
                            round_name = target
                            if delta < 0:
                                row_data.append(f"½→{total}")
                            else:
                                row_data.append(f"+{delta}→{total}")
                        else:
                            row_data.append("-")
                    rows.append([round_name or f"R{r+1}"] + row_data)
                self._build_round_table(parent, "Runddetaljer", headers, rows)

    def _build_saved_round_table(self, parent, title, round_label, players, player_results, key):
        """Generisk tabell för sparad runddata"""
        has_data = any(key in player_results.get(p, {}) for p in players)
        if not has_data:
            return
        headers = [round_label] + [p[:6] for p in players]
        max_rounds = max(len(player_results.get(p, {}).get(key, [])) for p in players)
        rows = []
        totals = {p: 0 for p in players}
        for r in range(max_rounds):
            row = [str(r + 1)]
            for p in players:
                scores = player_results.get(p, {}).get(key, [])
                val = scores[r] if r < len(scores) else "-"
                if isinstance(val, (int, float)):
                    totals[p] += val
                row.append(str(val))
            rows.append(row)
        rows.append(["Totalt"] + [str(totals[p]) for p in players])
        self._build_round_table(parent, title, headers, rows)

    def show_player_stats_select(self):
        """Visa val av spelare för detaljerad statistik"""
        self.clear()

        title_frame = tk.Frame(self.root, bg=COLORS['bg'])
        title_frame.pack(pady=5, fill="x")
        back_btn = self.styled_button(title_frame, "← Tillbaka", self.show_stats_menu,
                                      bg=COLORS['accent2'])
        back_btn.config(font=("Arial", 10, "bold"))
        back_btn.pack(side="left", padx=10)
        self.styled_label(title_frame, "Välj spelare", 16).pack(side="left", expand=True)

        results = get_all_results()
        if not results:
            self.styled_label(self.root, "Inga matcher spelade ännu.", 14).pack(pady=40)
            return

        # Samla alla unika spelarnamn
        all_players = set()
        for r in results:
            all_players.update(r["players"])

        btn_frame = tk.Frame(self.root, bg=COLORS['bg'])
        btn_frame.pack(pady=10)

        for i, name in enumerate(sorted(all_players)):
            btn = self.styled_button(btn_frame, name,
                                      lambda n=name: self.show_player_detail(n))
            btn.config(width=14, height=1, font=("Arial", 12, "bold"))
            btn.grid(row=i // 2, column=i % 2, padx=5, pady=3)

    def show_player_detail(self, player_name):
        """Visa detaljerad statistik för en spelare"""
        self.clear()

        title_frame = tk.Frame(self.root, bg=COLORS['bg'])
        title_frame.pack(pady=5, fill="x")
        back_btn = self.styled_button(title_frame, "← Tillbaka", self.show_player_stats_select,
                                      bg=COLORS['accent2'])
        back_btn.config(font=("Arial", 10, "bold"))
        back_btn.pack(side="left", padx=10)
        self.styled_label(title_frame, player_name, 18, COLORS['gold']).pack(side="left", expand=True)

        stats = get_player_stats(player_name)

        # Scrollbart område
        canvas_frame = tk.Frame(self.root, bg=COLORS['bg'])
        canvas_frame.pack(pady=5, padx=5, fill="both", expand=True)

        canvas = tk.Canvas(canvas_frame, bg=COLORS['bg'], highlightthickness=0)
        scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        scrollable = tk.Frame(canvas, bg=COLORS['bg'])
        scrollable.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable, anchor="nw", width=self.sx(450))
        canvas.configure(yscrollcommand=scrollbar.set)

        # Översikt - stor tydlig display
        overview = tk.Frame(scrollable, bg=COLORS['panel'])
        overview.pack(fill="x", padx=10, pady=5)

        stats_row = tk.Frame(overview, bg=COLORS['panel'])
        stats_row.pack(fill="x", pady=5)

        stat_items = [
            ("Matcher", str(stats['total_games']), COLORS['text']),
            ("Vinster", str(stats['wins']), COLORS['green']),
            ("Win%", f"{stats['win_rate']:.0f}%", COLORS['gold']),
        ]

        if stats.get('solo_games', 0) > 0:
            stat_items.append(("Solo", str(stats['solo_games']), COLORS['accent2']))

        for label, value, color in stat_items:
            stat_frame = tk.Frame(stats_row, bg=COLORS['panel'])
            stat_frame.pack(side="left", expand=True, padx=5)
            tk.Label(stat_frame, text=value, font=("Arial", 20, "bold"),
                    fg=color, bg=COLORS['panel']).pack()
            tk.Label(stat_frame, text=label, font=("Arial", 9),
                    fg=COLORS['accent2'], bg=COLORS['panel']).pack()

        # Streak och X01-snitt
        extra_row = tk.Frame(overview, bg=COLORS['panel'])
        extra_row.pack(fill="x", pady=(0, 5))

        streak = stats.get('streak', 0)
        if streak > 0:
            streak_text = f"🔥 {streak} vinster i rad"
            streak_fg = COLORS['green']
        elif streak < 0:
            streak_text = f"❄ {abs(streak)} förluster i rad"
            streak_fg = COLORS['red']
        else:
            streak_text = "—"
            streak_fg = COLORS['text']

        tk.Label(extra_row, text=streak_text, font=("Arial", 10),
                fg=streak_fg, bg=COLORS['panel']).pack(side="left", padx=10)

        best = stats.get('best_streak', 0)
        if best > 0:
            tk.Label(extra_row, text=f"Bästa streak: {best}", font=("Arial", 9),
                    fg=COLORS['accent2'], bg=COLORS['panel']).pack(side="left", padx=10)

        x01_avg = stats.get('x01_avg', 0)
        if x01_avg > 0:
            tk.Label(extra_row, text=f"X01 snitt: {x01_avg:.1f}", font=("Arial", 10, "bold"),
                    fg=COLORS['gold'], bg=COLORS['panel']).pack(side="right", padx=10)

        # Per speltyp - tabell
        if stats["per_game"]:
            tk.Label(scrollable, text="Per speltyp", font=("Arial", 13, "bold"),
                    fg=COLORS['accent'], bg=COLORS['bg']).pack(anchor="w", padx=10, pady=(10, 3))

            header = tk.Frame(scrollable, bg=COLORS['accent2'])
            header.pack(fill="x", padx=10)
            for h, w in [("Spel", 12), ("Spelade", 7), ("Vinster", 7), ("V%", 6)]:
                tk.Label(header, text=h, font=("Arial", 10, "bold"),
                        fg=COLORS['gold'], bg=COLORS['accent2'], width=w,
                        anchor="w" if h == "Spel" else "center").pack(side="left", padx=2, pady=2)

            for i, (gm, gd) in enumerate(sorted(stats["per_game"].items())):
                bg = COLORS['panel'] if i % 2 == 0 else COLORS['bg']
                row = tk.Frame(scrollable, bg=bg)
                row.pack(fill="x", padx=10)
                label = self.GAME_LABELS.get(gm, gm)
                multi_played = gd["played"] - gd.get("solo", 0)
                pct = (gd["wins"] / multi_played * 100) if multi_played > 0 else 0
                wins_text = str(gd["wins"])
                if gd.get("solo", 0) > 0:
                    wins_text += f" (+{gd['solo']}s)"
                for v, w, a in [(label, 12, "w"), (str(gd["played"]), 7, "center"),
                                (wins_text, 7, "center"), (f"{pct:.0f}%", 6, "center")]:
                    tk.Label(row, text=v, font=("Arial", 10),
                            fg=COLORS['text'], bg=bg, width=w, anchor=a).pack(side="left", padx=2, pady=1)

        # Rekord per speltyp
        records = stats.get("records", {})
        if records:
            tk.Label(scrollable, text="🏅 Rekord", font=("Arial", 13, "bold"),
                    fg=COLORS['accent'], bg=COLORS['bg']).pack(anchor="w", padx=10, pady=(10, 3))

            record_labels = {
                'x01': [("min_darts", "Minst pilar (vinst)", ""),
                        ("best_avg", "Bästa snitt/runda", "")],
                'highscore': [("best_score", "Bästa totalpoäng", "p"),
                              ("best_round", "Bästa runda", "p")],
                'shanghai': [("best_score", "Bästa totalpoäng", "p"),
                             ("best_round", "Bästa runda", "p")],
                'golf': [("best_score", "Bästa totalscore", " slag"),
                         ("best_hole", "Bästa hål", "")],
                'halveit': [("best_score", "Bästa totalpoäng", "p")],
                'cricket': [("best_score", "Bästa poäng", "p")],
                'around_the_clock': [("completions", "Klarade", " ggr")],
                'killer': [("survivals", "Överlevde", " ggr")],
                'triple_killer': [("survivals", "Överlevde", " ggr")],
                'hits_killer': [("survivals", "Överlevde", " ggr")],
            }

            for gm, rec in sorted(records.items()):
                if not rec:
                    continue
                game_label = self.GAME_LABELS.get(gm, gm)
                labels = record_labels.get(gm, [])

                gm_frame = tk.Frame(scrollable, bg=COLORS['panel'])
                gm_frame.pack(fill="x", padx=10, pady=1)

                tk.Label(gm_frame, text=game_label, font=("Arial", 10, "bold"),
                        fg=COLORS['accent'], bg=COLORS['panel']).pack(side="left", padx=5, pady=3)

                rec_parts = []
                for key, label, suffix in labels:
                    val = rec.get(key)
                    if val is not None:
                        rec_parts.append(f"{label}: {val}{suffix}")

                if rec_parts:
                    tk.Label(gm_frame, text="  |  ".join(rec_parts), font=("Arial", 9),
                            fg=COLORS['gold'], bg=COLORS['panel']).pack(side="left", padx=5, pady=3)

        # Senaste matcher för denna spelare
        all_results = get_all_results()
        player_matches = [r for r in all_results if player_name in r["players"]]
        recent = player_matches[-10:]

        if recent:
            tk.Label(scrollable, text="Senaste matcher", font=("Arial", 13, "bold"),
                    fg=COLORS['accent'], bg=COLORS['bg']).pack(anchor="w", padx=10, pady=(10, 3))

            for idx, r in enumerate(reversed(recent)):
                bg = COLORS['panel'] if idx % 2 == 0 else COLORS['bg']
                row = tk.Frame(scrollable, bg=bg)
                row.pack(fill="x", padx=10, pady=1)

                ts = r["timestamp"][:10]
                game_label = self.GAME_LABELS.get(r["game_mode"], r["game_mode"])
                won = r["winner"] == player_name
                result_text = "✓ Vinst" if won else f"✗ {r['winner']} vann"
                result_fg = COLORS['green'] if won else COLORS['red']

                tk.Label(row, text=ts, font=("Arial", 8),
                        fg=COLORS['accent2'], bg=bg).pack(side="left", padx=3, pady=2)
                tk.Label(row, text=game_label, font=("Arial", 9, "bold"),
                        fg=COLORS['accent'], bg=bg).pack(side="left", padx=3, pady=2)
                tk.Label(row, text=result_text, font=("Arial", 9, "bold"),
                        fg=result_fg, bg=bg).pack(side="right", padx=5, pady=2)

                # Motståndare
                opponents = [p for p in r["players"] if p != player_name]
                if opponents:
                    tk.Label(row, text=f"vs {', '.join(opponents)}", font=("Arial", 8),
                            fg=COLORS['text'], bg=bg).pack(side="right", padx=3, pady=2)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))

    # ============================================
    # HEAD-TO-HEAD
    # ============================================

    def show_h2h_select(self):
        """Välj två spelare för head-to-head"""
        self.clear()

        title_frame = tk.Frame(self.root, bg=COLORS['bg'])
        title_frame.pack(pady=5, fill="x")
        back_btn = self.styled_button(title_frame, "← Tillbaka", self.show_stats_menu,
                                      bg=COLORS['accent2'])
        back_btn.config(font=("Arial", 10, "bold"))
        back_btn.pack(side="left", padx=10)
        self.styled_label(title_frame, "⚔ Head-to-Head", 16).pack(side="left", expand=True)

        results = get_all_results()
        if not results:
            self.styled_label(self.root, "Inga matcher spelade ännu.", 14).pack(pady=40)
            return

        all_players = sorted(set(p for r in results for p in r["players"]))
        if len(all_players) < 2:
            self.styled_label(self.root, "Minst 2 spelare krävs.", 14).pack(pady=40)
            return

        self.styled_label(self.root, "Välj spelare 1", 13).pack(pady=(10, 5))

        self.h2h_player_a = tk.StringVar(value=all_players[0])
        self.h2h_player_b = tk.StringVar(value=all_players[1] if len(all_players) > 1 else all_players[0])

        frame_a = tk.Frame(self.root, bg=COLORS['bg'])
        frame_a.pack(pady=3)
        self._h2h_btns_a = {}
        for name in all_players:
            btn = tk.Button(frame_a, text=name, font=("Arial", 11, "bold"),
                           bg=COLORS['accent'] if name == self.h2h_player_a.get() else COLORS['button'],
                           fg=COLORS['text'], relief="flat",
                           command=lambda n=name: self._h2h_select_a(n, all_players))
            btn.pack(side="left", padx=3)
            self._h2h_btns_a[name] = btn

        self.styled_label(self.root, "vs", 16, COLORS['accent']).pack(pady=3)
        self.styled_label(self.root, "Välj spelare 2", 13).pack(pady=(3, 5))

        frame_b = tk.Frame(self.root, bg=COLORS['bg'])
        frame_b.pack(pady=3)
        self._h2h_btns_b = {}
        for name in all_players:
            btn = tk.Button(frame_b, text=name, font=("Arial", 11, "bold"),
                           bg=COLORS['accent'] if name == self.h2h_player_b.get() else COLORS['button'],
                           fg=COLORS['text'], relief="flat",
                           command=lambda n=name: self._h2h_select_b(n, all_players))
            btn.pack(side="left", padx=3)
            self._h2h_btns_b[name] = btn

        go_btn = self.styled_button(self.root, "Jämför!", self._h2h_go, bg=COLORS['green'])
        go_btn.config(font=("Arial", 14, "bold"), width=14)
        go_btn.pack(pady=15)

    def _h2h_select_a(self, name, all_players):
        self.h2h_player_a.set(name)
        for p in all_players:
            btn = self._h2h_btns_a.get(p)
            if btn:
                btn.config(bg=COLORS['accent'] if p == name else COLORS['button'])

    def _h2h_select_b(self, name, all_players):
        self.h2h_player_b.set(name)
        for p in all_players:
            btn = self._h2h_btns_b.get(p)
            if btn:
                btn.config(bg=COLORS['accent'] if p == name else COLORS['button'])

    def _h2h_go(self):
        a = self.h2h_player_a.get()
        b = self.h2h_player_b.get()
        if a == b:
            return
        self.show_h2h_detail(a, b)

    def show_h2h_detail(self, player_a, player_b):
        """Visa head-to-head-vy"""
        self.clear()

        h2h = get_head_to_head(player_a, player_b)

        title_frame = tk.Frame(self.root, bg=COLORS['bg'])
        title_frame.pack(pady=5, fill="x")
        back_btn = self.styled_button(title_frame, "← Tillbaka", self.show_h2h_select,
                                      bg=COLORS['accent2'])
        back_btn.config(font=("Arial", 10, "bold"))
        back_btn.pack(side="left", padx=10)
        self.styled_label(title_frame, "⚔ Head-to-Head", 14).pack(side="left", expand=True)

        if h2h["total"] == 0:
            self.styled_label(self.root, "Inga gemensamma matcher.", 14).pack(pady=40)
            return

        # Scrollbart
        canvas_frame = tk.Frame(self.root, bg=COLORS['bg'])
        canvas_frame.pack(pady=5, padx=5, fill="both", expand=True)

        canvas = tk.Canvas(canvas_frame, bg=COLORS['bg'], highlightthickness=0)
        scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        scrollable = tk.Frame(canvas, bg=COLORS['bg'])
        scrollable.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable, anchor="nw", width=self.sx(450))
        canvas.configure(yscrollcommand=scrollbar.set)

        # Stor jämförelse-header
        vs_frame = tk.Frame(scrollable, bg=COLORS['panel'])
        vs_frame.pack(fill="x", padx=10, pady=5)

        # Spelare A
        a_frame = tk.Frame(vs_frame, bg=COLORS['panel'])
        a_frame.pack(side="left", expand=True, fill="both", padx=5, pady=8)
        a_wins = h2h["wins_a"]
        a_color = COLORS['green'] if a_wins > h2h["wins_b"] else (COLORS['gold'] if a_wins == h2h["wins_b"] else COLORS['text'])
        tk.Label(a_frame, text=player_a, font=("Arial", 14, "bold"),
                fg=a_color, bg=COLORS['panel']).pack()
        tk.Label(a_frame, text=str(a_wins), font=("Arial", 32, "bold"),
                fg=a_color, bg=COLORS['panel']).pack()
        pct_a = (a_wins / h2h["total"] * 100) if h2h["total"] > 0 else 0
        tk.Label(a_frame, text=f"{pct_a:.0f}%", font=("Arial", 11),
                fg=COLORS['accent2'], bg=COLORS['panel']).pack()

        # VS
        vs_mid = tk.Frame(vs_frame, bg=COLORS['panel'])
        vs_mid.pack(side="left", padx=5, pady=8)
        tk.Label(vs_mid, text="vs", font=("Arial", 14, "bold"),
                fg=COLORS['accent'], bg=COLORS['panel']).pack()
        tk.Label(vs_mid, text=f"{h2h['total']} matcher", font=("Arial", 9),
                fg=COLORS['accent2'], bg=COLORS['panel']).pack()

        # Spelare B
        b_frame = tk.Frame(vs_frame, bg=COLORS['panel'])
        b_frame.pack(side="left", expand=True, fill="both", padx=5, pady=8)
        b_wins = h2h["wins_b"]
        b_color = COLORS['green'] if b_wins > a_wins else (COLORS['gold'] if b_wins == a_wins else COLORS['text'])
        tk.Label(b_frame, text=player_b, font=("Arial", 14, "bold"),
                fg=b_color, bg=COLORS['panel']).pack()
        tk.Label(b_frame, text=str(b_wins), font=("Arial", 32, "bold"),
                fg=b_color, bg=COLORS['panel']).pack()
        pct_b = (b_wins / h2h["total"] * 100) if h2h["total"] > 0 else 0
        tk.Label(b_frame, text=f"{pct_b:.0f}%", font=("Arial", 11),
                fg=COLORS['accent2'], bg=COLORS['panel']).pack()

        # Visuell stapel
        bar_frame = tk.Frame(scrollable, bg=COLORS['accent2'], height=self.sy(14))
        bar_frame.pack(fill="x", padx=10, pady=2)
        bar_frame.pack_propagate(False)

        if h2h["total"] > 0:
            a_pct = a_wins / h2h["total"]
            if a_pct > 0:
                a_bar = tk.Frame(bar_frame, bg=COLORS['green'])
                a_bar.place(relx=0, rely=0, relwidth=a_pct, relheight=1)
            if a_pct < 1:
                b_bar = tk.Frame(bar_frame, bg=COLORS['red'])
                b_bar.place(relx=a_pct, rely=0, relwidth=1-a_pct, relheight=1)

        # Streak-info
        streak_frame = tk.Frame(scrollable, bg=COLORS['bg'])
        streak_frame.pack(fill="x", padx=10, pady=5)

        if h2h["streak_player"] and h2h["streak_count"] > 1:
            streak_text = f"🔥 {h2h['streak_player']} leder med {h2h['streak_count']} vinster i rad"
            tk.Label(streak_frame, text=streak_text, font=("Arial", 10, "bold"),
                    fg=COLORS['gold'], bg=COLORS['bg']).pack()

        best_a = h2h.get("best_streak_a", 0)
        best_b = h2h.get("best_streak_b", 0)
        if best_a > 1 or best_b > 1:
            streak_details = []
            if best_a > 1:
                streak_details.append(f"{player_a}: {best_a} bästa streak")
            if best_b > 1:
                streak_details.append(f"{player_b}: {best_b} bästa streak")
            tk.Label(streak_frame, text="  |  ".join(streak_details), font=("Arial", 9),
                    fg=COLORS['accent2'], bg=COLORS['bg']).pack()

        # Per speltyp
        if h2h["per_game"]:
            tk.Label(scrollable, text="Per speltyp", font=("Arial", 13, "bold"),
                    fg=COLORS['accent'], bg=COLORS['bg']).pack(anchor="w", padx=10, pady=(10, 3))

            header = tk.Frame(scrollable, bg=COLORS['accent2'])
            header.pack(fill="x", padx=10)
            for h, w in [("Spel", 10), (player_a[:6], 7), (player_b[:6], 7), ("Totalt", 6)]:
                tk.Label(header, text=h, font=("Arial", 9, "bold"),
                        fg=COLORS['gold'], bg=COLORS['accent2'], width=w).pack(side="left", padx=2, pady=2)

            for i, (gm, data) in enumerate(sorted(h2h["per_game"].items())):
                bg = COLORS['panel'] if i % 2 == 0 else COLORS['bg']
                row = tk.Frame(scrollable, bg=bg)
                row.pack(fill="x", padx=10)
                label = self.GAME_LABELS.get(gm, gm)
                for v, w in [(label, 10), (str(data["a"]), 7), (str(data["b"]), 7), (str(data["total"]), 6)]:
                    tk.Label(row, text=v, font=("Arial", 10),
                            fg=COLORS['text'], bg=bg, width=w).pack(side="left", padx=2, pady=1)

        # Senaste möten
        recent = h2h.get("recent", [])
        if recent:
            tk.Label(scrollable, text="Senaste möten", font=("Arial", 13, "bold"),
                    fg=COLORS['accent'], bg=COLORS['bg']).pack(anchor="w", padx=10, pady=(10, 3))

            for idx, r in enumerate(reversed(recent)):
                bg = COLORS['panel'] if idx % 2 == 0 else COLORS['bg']
                row = tk.Frame(scrollable, bg=bg)
                row.pack(fill="x", padx=10, pady=1)

                ts = r["timestamp"][:10]
                game_label = self.GAME_LABELS.get(r["game_mode"], r["game_mode"])
                winner = r["winner"]
                winner_color = COLORS['green']

                tk.Label(row, text=ts, font=("Arial", 8),
                        fg=COLORS['accent2'], bg=bg).pack(side="left", padx=3, pady=2)
                tk.Label(row, text=game_label, font=("Arial", 9, "bold"),
                        fg=COLORS['accent'], bg=bg).pack(side="left", padx=3, pady=2)
                tk.Label(row, text=f"🏆 {winner}", font=("Arial", 10, "bold"),
                        fg=winner_color, bg=bg).pack(side="right", padx=5, pady=2)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))

    # ============================================
    # FORM & TRENDER
    # ============================================

    def show_form_select(self):
        """Välj spelare för form/trender"""
        self.clear()

        title_frame = tk.Frame(self.root, bg=COLORS['bg'])
        title_frame.pack(pady=5, fill="x")
        back_btn = self.styled_button(title_frame, "← Tillbaka", self.show_stats_menu,
                                      bg=COLORS['accent2'])
        back_btn.config(font=("Arial", 10, "bold"))
        back_btn.pack(side="left", padx=10)
        self.styled_label(title_frame, "📈 Form & Trender", 16).pack(side="left", expand=True)

        results = get_all_results()
        if not results:
            self.styled_label(self.root, "Inga matcher spelade ännu.", 14).pack(pady=40)
            return

        all_players = sorted(set(p for r in results for p in r["players"]))

        self.styled_label(self.root, "Välj spelare", 14).pack(pady=(15, 10))

        btn_frame = tk.Frame(self.root, bg=COLORS['bg'])
        btn_frame.pack(pady=5)
        for i, name in enumerate(all_players):
            btn = self.styled_button(btn_frame, name,
                                     lambda n=name: self.show_form_detail(n))
            btn.config(width=14, height=1, font=("Arial", 12, "bold"))
            btn.grid(row=i // 2, column=i % 2, padx=5, pady=3)

    def show_form_detail(self, player_name):
        """Visa formkurva och trender för en spelare"""
        self.clear()

        title_frame = tk.Frame(self.root, bg=COLORS['bg'])
        title_frame.pack(pady=5, fill="x")
        back_btn = self.styled_button(title_frame, "← Tillbaka", self.show_form_select,
                                      bg=COLORS['accent2'])
        back_btn.config(font=("Arial", 10, "bold"))
        back_btn.pack(side="left", padx=10)
        self.styled_label(title_frame, f"📈 {player_name}", 16, COLORS['gold']).pack(side="left", expand=True)

        form = get_form_data(player_name, last_n=20)

        if not form:
            self.styled_label(self.root, "Inga flerspelarmatchar ännu.", 14).pack(pady=40)
            return

        # Scrollbart
        canvas_frame = tk.Frame(self.root, bg=COLORS['bg'])
        canvas_frame.pack(pady=5, padx=5, fill="both", expand=True)

        canvas = tk.Canvas(canvas_frame, bg=COLORS['bg'], highlightthickness=0)
        scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        scrollable = tk.Frame(canvas, bg=COLORS['bg'])
        scrollable.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable, anchor="nw", width=self.sx(450))
        canvas.configure(yscrollcommand=scrollbar.set)

        # Formkurva: visuell rad med V/F
        tk.Label(scrollable, text="Formkurva (senaste 20)", font=("Arial", 13, "bold"),
                fg=COLORS['accent'], bg=COLORS['bg']).pack(anchor="w", padx=10, pady=(10, 5))

        form_row = tk.Frame(scrollable, bg=COLORS['panel'])
        form_row.pack(fill="x", padx=10, pady=3)

        wins_total = sum(1 for f in form if f["won"])
        losses_total = len(form) - wins_total

        for i, f in enumerate(form):
            sym = "V" if f["won"] else "F"
            fg = COLORS['green'] if f["won"] else COLORS['red']
            tk.Label(form_row, text=sym, font=("Arial", 12, "bold"),
                    fg=fg, bg=COLORS['panel'], width=2).pack(side="left", padx=1, pady=5)

        # Sammanfattning
        summary = tk.Frame(scrollable, bg=COLORS['panel'])
        summary.pack(fill="x", padx=10, pady=3)

        form_pct = (wins_total / len(form) * 100) if form else 0
        sum_items = [
            (f"{wins_total}V", COLORS['green']),
            (f"{losses_total}F", COLORS['red']),
            (f"({form_pct:.0f}%)", COLORS['gold']),
        ]
        for text, color in sum_items:
            tk.Label(summary, text=text, font=("Arial", 14, "bold"),
                    fg=color, bg=COLORS['panel']).pack(side="left", padx=8, pady=5)

        # Form-rating
        rating = "🔥🔥🔥" if form_pct >= 80 else "🔥🔥" if form_pct >= 60 else "🔥" if form_pct >= 40 else "❄"
        tk.Label(summary, text=rating, font=("Arial", 16),
                bg=COLORS['panel']).pack(side="right", padx=10, pady=5)

        # Win% i fönster: senaste 5 vs senaste 10
        tk.Label(scrollable, text="Trender", font=("Arial", 13, "bold"),
                fg=COLORS['accent'], bg=COLORS['bg']).pack(anchor="w", padx=10, pady=(10, 3))

        windows = [(5, "Senaste 5"), (10, "Senaste 10")]
        trend_frame = tk.Frame(scrollable, bg=COLORS['bg'])
        trend_frame.pack(fill="x", padx=10, pady=3)

        for window_size, label in windows:
            window = form[-window_size:] if len(form) >= window_size else form
            w_wins = sum(1 for f in window if f["won"])
            w_pct = (w_wins / len(window) * 100) if window else 0

            block = tk.Frame(trend_frame, bg=COLORS['panel'])
            block.pack(side="left", expand=True, fill="both", padx=3, pady=3)

            tk.Label(block, text=label, font=("Arial", 10),
                    fg=COLORS['accent2'], bg=COLORS['panel']).pack(pady=(5, 0))
            tk.Label(block, text=f"{w_pct:.0f}%", font=("Arial", 20, "bold"),
                    fg=COLORS['green'] if w_pct >= 50 else COLORS['red'],
                    bg=COLORS['panel']).pack()
            tk.Label(block, text=f"{w_wins}/{len(window)}", font=("Arial", 9),
                    fg=COLORS['text'], bg=COLORS['panel']).pack(pady=(0, 5))

            # Trend-pil jämfört med totalt
            if form_pct > 0:
                diff = w_pct - form_pct
                if diff > 5:
                    trend = "↑"
                    trend_fg = COLORS['green']
                elif diff < -5:
                    trend = "↓"
                    trend_fg = COLORS['red']
                else:
                    trend = "→"
                    trend_fg = COLORS['text']
                tk.Label(block, text=trend, font=("Arial", 14, "bold"),
                        fg=trend_fg, bg=COLORS['panel']).pack(pady=(0, 3))

        # Visuell form-graf (bar chart per speltyp)
        tk.Label(scrollable, text="Win% per speltyp (form)", font=("Arial", 13, "bold"),
                fg=COLORS['accent'], bg=COLORS['bg']).pack(anchor="w", padx=10, pady=(10, 3))

        game_form = {}
        for f in form:
            gm = f["game_mode"]
            if gm not in game_form:
                game_form[gm] = {"wins": 0, "total": 0}
            game_form[gm]["total"] += 1
            if f["won"]:
                game_form[gm]["wins"] += 1

        for gm, data in sorted(game_form.items()):
            pct = (data["wins"] / data["total"] * 100) if data["total"] > 0 else 0
            label = self.GAME_LABELS.get(gm, gm)

            row = tk.Frame(scrollable, bg=COLORS['bg'])
            row.pack(fill="x", padx=10, pady=2)

            tk.Label(row, text=f"{label}", font=("Arial", 10, "bold"),
                    fg=COLORS['text'], bg=COLORS['bg'], width=10, anchor="w").pack(side="left")

            # Visuell stapel
            bar_bg = tk.Frame(row, bg=COLORS['accent2'], height=self.sy(12))
            bar_bg.pack(side="left", fill="x", expand=True, padx=3)
            bar_bg.pack_propagate(False)

            if pct > 0:
                bar_fill = tk.Frame(bar_bg, bg=COLORS['green'] if pct >= 50 else COLORS['red'])
                bar_fill.place(relx=0, rely=0, relwidth=pct/100, relheight=1)

            tk.Label(row, text=f"{pct:.0f}% ({data['wins']}/{data['total']})", font=("Arial", 9),
                    fg=COLORS['gold'], bg=COLORS['bg'], width=10).pack(side="left")

        # Matchlista
        tk.Label(scrollable, text="Matchdetaljer", font=("Arial", 13, "bold"),
                fg=COLORS['accent'], bg=COLORS['bg']).pack(anchor="w", padx=10, pady=(10, 3))

        for idx, f in enumerate(reversed(form)):
            bg = COLORS['panel'] if idx % 2 == 0 else COLORS['bg']
            row = tk.Frame(scrollable, bg=bg)
            row.pack(fill="x", padx=10, pady=1)

            ts = f["timestamp"][:10]
            game_label = self.GAME_LABELS.get(f["game_mode"], f["game_mode"])
            result_sym = "✓" if f["won"] else "✗"
            result_fg = COLORS['green'] if f["won"] else COLORS['red']

            tk.Label(row, text=result_sym, font=("Arial", 12, "bold"),
                    fg=result_fg, bg=bg).pack(side="left", padx=3, pady=2)
            tk.Label(row, text=ts, font=("Arial", 8),
                    fg=COLORS['accent2'], bg=bg).pack(side="left", padx=3, pady=2)
            tk.Label(row, text=game_label, font=("Arial", 9, "bold"),
                    fg=COLORS['accent'], bg=bg).pack(side="left", padx=3, pady=2)

            if f["opponents"]:
                tk.Label(row, text=f"vs {', '.join(f['opponents'])}", font=("Arial", 8),
                        fg=COLORS['text'], bg=bg).pack(side="right", padx=5, pady=2)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))
