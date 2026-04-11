import tkinter as tk
from constants import COLORS, PRESET_NAMES, GAME_HELP
from games import X01Mixin, CricketMixin, ClockMixin, KillerMixin, ShanghaiMixin, HalveItMixin, HighScoreMixin, GolfMixin


class DartApp(X01Mixin, CricketMixin, ClockMixin, KillerMixin, ShanghaiMixin, HalveItMixin, HighScoreMixin, GolfMixin):
    """Huvudapplikation för Dart Scoreboard"""

    def __init__(self, root, fullscreen=False):
        self.root = root
        self.root.title("Dart Scoreboard")
        self.root.geometry("480x320")
        self.root.resizable(False, False)
        self.root.configure(bg=COLORS['bg'])
        if fullscreen:
            self.root.attributes('-fullscreen', True)

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
        self.styled_label(self.root, help_data['title'], 14, COLORS['gold']).place(x=10, y=5)
        
        # Stäng-knapp (fast position längst upp till höger)
        close_btn = self.styled_button(self.root, "✕ Stäng", return_callback, bg=COLORS['accent'])
        close_btn.config(font=("Arial", 11, "bold"))
        close_btn.place(x=380, y=5, width=90, height=30)
        
        # Scrollbar hjälptext med Canvas
        canvas_frame = tk.Frame(self.root, bg=COLORS['panel'])
        canvas_frame.place(x=10, y=40, width=460, height=270)
        
        canvas = tk.Canvas(canvas_frame, bg=COLORS['panel'], highlightthickness=0)
        scrollbar = tk.Scrollbar(canvas_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=COLORS['panel'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=440)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Hjälptext
        help_label = tk.Label(scrollable_frame, text=help_data['text'],
                             font=("Arial", 10),
                             fg=COLORS['text'], bg=COLORS['panel'],
                             justify="left", anchor="nw",
                             wraplength=420)
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
        self.styled_label(self.root, "DART", 28, COLORS['accent']).pack(pady=5)
        self.styled_label(self.root, "Antal spelare", 16).pack(pady=5)

        frame = tk.Frame(self.root, bg=COLORS['bg'])
        frame.pack(pady=10)
        for i in range(1, 5):
            btn = self.styled_button(frame, str(i), lambda n=i: self.set_players(n))
            btn.config(width=5, height=2)
            btn.grid(row=0, column=i-1, padx=5)

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
        
        # Game buttons in centered rows
        games = [
            ("Cricket", self.start_cricket, 'cricket'),
            ("Klockan", self.start_around_the_clock, 'around_the_clock'),
            ("Killer", self.start_killer, 'killer'),
            ("Shanghai", self.start_shanghai, 'shanghai'),
            ("Halve It", self.start_halveit, 'halveit'),
            ("High Score", self.start_highscore, 'highscore'),
            ("Golf", self.start_golf, 'golf'),
        ]
        
        row1_frame = tk.Frame(other_frame, bg=COLORS['bg'])
        row1_frame.pack(pady=2)
        row2_frame = tk.Frame(other_frame, bg=COLORS['bg'])
        row2_frame.pack(pady=2)
        
        for i, (name, cmd, help_key) in enumerate(games):
            parent = row1_frame if i < 4 else row2_frame
            
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

    def show_winner(self, player):
        """Visa vinnaren"""
        self.clear()

        frame = tk.Frame(self.root, bg=COLORS['bg'])
        frame.place(x=0, y=0, width=480, height=320)

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
