import tkinter as tk
from constants import COLORS, PRESET_NAMES, GAME_HELP
from games import X01Mixin, CricketMixin, ClockMixin, KillerMixin, ShanghaiMixin, HalveItMixin, HighScoreMixin, GolfMixin
from results_store import save_result, get_leaderboard, get_player_stats, get_all_results


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
            elif self.game_mode == 'halveit':
                data["score"] = self.halveit_scores.get(name, 0)
            elif self.game_mode == 'highscore':
                data["score"] = self.highscore_scores.get(name, 0)
                data["round_scores"] = self.highscore_round_scores.get(name, [])
            elif self.game_mode == 'golf':
                data["score"] = self.golf_scores.get(name, 0)
                data["hole_scores"] = self.golf_hole_scores.get(name, [])
            result[name] = data
        return result

    def show_winner(self, player):
        """Visa vinnaren"""
        # Spara resultatet
        player_results = self._collect_game_result(player)
        save_result(self.game_mode, player, list(self.player_names), player_results)

        self.clear()

        frame = tk.Frame(self.root, bg=COLORS['bg'])
        frame.place(x=0, y=0, width=self.W, height=self.H)

        self.styled_label(frame, "🎯", 40).pack(pady=10)
        self.styled_label(frame, f"{player}", 24, COLORS['gold']).pack()
        self.styled_label(frame, "VANN!", 28, COLORS['accent']).pack()

        if self.game_mode == 'x01' and player in self.player_stats:
            stats = self.player_stats[player]
            if stats['rounds'] > 0:
                avg = stats['total'] / stats['rounds']
                self.styled_label(frame, f"Snitt: {avg:.1f} per runda", 12).pack(pady=5)

        btn_frame = tk.Frame(frame, bg=COLORS['bg'])
        btn_frame.pack(pady=20)

        self.styled_button(btn_frame, "Spela igen", self.replay_game).grid(row=0, column=0, padx=10)
        self.styled_button(btn_frame, "Ny match", self.show_player_select).grid(row=0, column=1, padx=10)

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
        ]

        for i, (text, cmd) in enumerate(buttons):
            btn = self.styled_button(btn_frame, text, cmd)
            btn.config(width=18, height=2, font=("Arial", 13, "bold"))
            btn.pack(pady=5)

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

        # Tabell-header
        table = tk.Frame(self.root, bg=COLORS['panel'])
        table.pack(pady=10, padx=10, fill="x")

        headers = ["#", "Spelare", "V", "S", "V%"]
        widths = [3, 10, 4, 4, 5]
        for c, (h, w) in enumerate(zip(headers, widths)):
            tk.Label(table, text=h, font=("Arial", 11, "bold"),
                     fg=COLORS['gold'], bg=COLORS['panel'], width=w).grid(row=0, column=c, pady=2)

        for i, (name, wins, played, pct) in enumerate(board[:8]):
            row = i + 1
            fg = COLORS['gold'] if i == 0 else COLORS['text']
            vals = [str(row), name[:10], str(wins), str(played), f"{pct:.0f}%"]
            for c, (v, w) in enumerate(zip(vals, widths)):
                tk.Label(table, text=v, font=("Arial", 11),
                         fg=fg, bg=COLORS['panel'], width=w).grid(row=row, column=c, pady=1)

    def show_recent_matches(self):
        """Visa senaste matcher"""
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
        canvas_frame = tk.Frame(self.root, bg=COLORS['panel'])
        canvas_frame.pack(pady=5, padx=10, fill="both", expand=True)

        canvas = tk.Canvas(canvas_frame, bg=COLORS['panel'], highlightthickness=0)
        scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        scrollable = tk.Frame(canvas, bg=COLORS['panel'])
        scrollable.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scrollable, anchor="nw", width=self.sx(440))
        canvas.configure(yscrollcommand=scrollbar.set)

        for r in reversed(results[-20:]):
            ts = r["timestamp"][:16].replace("T", " ")
            game_label = self.GAME_LABELS.get(r["game_mode"], r["game_mode"])
            players_str = ", ".join(r["players"])
            text = f"{ts}  {game_label}\n{players_str}  →  🏆 {r['winner']}"

            lbl = tk.Label(scrollable, text=text, font=("Arial", 9),
                           fg=COLORS['text'], bg=COLORS['panel'],
                           justify="left", anchor="w", wraplength=420)
            lbl.pack(fill="x", padx=5, pady=3)

            sep = tk.Frame(scrollable, bg=COLORS['accent2'], height=1)
            sep.pack(fill="x", padx=10)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        def on_scroll(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", on_scroll)

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

        # Översikt
        overview = tk.Frame(self.root, bg=COLORS['panel'])
        overview.pack(pady=5, padx=10, fill="x")

        info_text = (f"Spelade: {stats['total_games']}    "
                     f"Vinster: {stats['wins']}    "
                     f"Win%: {stats['win_rate']:.0f}%")
        tk.Label(overview, text=info_text, font=("Arial", 12, "bold"),
                 fg=COLORS['text'], bg=COLORS['panel']).pack(pady=5)

        # Per speltyp
        if stats["per_game"]:
            table = tk.Frame(self.root, bg=COLORS['panel'])
            table.pack(pady=5, padx=10, fill="x")

            tk.Label(table, text="Spel", font=("Arial", 10, "bold"),
                     fg=COLORS['gold'], bg=COLORS['panel'], width=12, anchor="w").grid(row=0, column=0)
            tk.Label(table, text="Spelade", font=("Arial", 10, "bold"),
                     fg=COLORS['gold'], bg=COLORS['panel'], width=8).grid(row=0, column=1)
            tk.Label(table, text="Vinster", font=("Arial", 10, "bold"),
                     fg=COLORS['gold'], bg=COLORS['panel'], width=8).grid(row=0, column=2)
            tk.Label(table, text="V%", font=("Arial", 10, "bold"),
                     fg=COLORS['gold'], bg=COLORS['panel'], width=6).grid(row=0, column=3)

            for i, (gm, gd) in enumerate(sorted(stats["per_game"].items())):
                row = i + 1
                label = self.GAME_LABELS.get(gm, gm)
                pct = (gd["wins"] / gd["played"] * 100) if gd["played"] > 0 else 0
                vals = [label, str(gd["played"]), str(gd["wins"]), f"{pct:.0f}%"]
                anchors = ["w", "center", "center", "center"]
                widths = [12, 8, 8, 6]
                for c, (v, a, w) in enumerate(zip(vals, anchors, widths)):
                    tk.Label(table, text=v, font=("Arial", 10),
                             fg=COLORS['text'], bg=COLORS['panel'],
                             width=w, anchor=a).grid(row=row, column=c, pady=1)
