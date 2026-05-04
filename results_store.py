"""Resultatlagring för Dart Scoreboard.

Sparar matchresultat i en JSON-fil och ger funktioner för att
läsa/söka historik per spelare och speltyp.
"""
import json
import os
from datetime import datetime

RESULTS_FILE = os.path.join(os.path.dirname(__file__), "results.json")


def _load_results():
    """Läs alla resultat från fil."""
    if not os.path.exists(RESULTS_FILE):
        return []
    with open(RESULTS_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except (json.JSONDecodeError, ValueError):
            return []


def _save_results(results):
    """Skriv alla resultat till fil."""
    with open(RESULTS_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)


def save_result(game_mode, winner, players, player_results):
    """Spara ett matchresultat.

    Args:
        game_mode: Speltyp (t.ex. 'x01', 'cricket', 'killer')
        winner: Namn på vinnaren
        players: Lista med spelarnamn (i spelordning)
        player_results: Dict {spelarnamn: {spelspecifik data}}
    """
    results = _load_results()
    entry = {
        "timestamp": datetime.now().isoformat(),
        "game_mode": game_mode,
        "winner": winner,
        "players": players,
        "player_results": player_results,
    }
    results.append(entry)
    _save_results(results)


def get_all_results():
    """Returnera alla sparade resultat."""
    return _load_results()


def get_results_by_player(player_name):
    """Returnera alla matcher där en spelare deltagit."""
    return [r for r in _load_results() if player_name in r["players"]]


def get_results_by_game(game_mode):
    """Returnera alla matcher av en viss speltyp."""
    return [r for r in _load_results() if r["game_mode"] == game_mode]


def get_player_stats(player_name):
    """Beräkna statistik för en spelare.

    Returnerar dict med:
        total_games, wins, win_rate, per_game (dict med stats per speltyp),
        streak (nuvarande vinst/förlust-streak), best_streak, avg_x01,
        solo_games, records (dict med rekord per speltyp)
    Solo-matcher (1 spelare) räknas inte som vinster i statistiken.
    """
    results = get_results_by_player(player_name)
    total = len(results)
    multi_results = [r for r in results if len(r["players"]) > 1]
    solo_games = total - len(multi_results)
    wins = sum(1 for r in multi_results if r["winner"] == player_name)

    per_game = {}
    for r in results:
        gm = r["game_mode"]
        is_multi = len(r["players"]) > 1
        if gm not in per_game:
            per_game[gm] = {"played": 0, "wins": 0, "solo": 0}
        per_game[gm]["played"] += 1
        if not is_multi:
            per_game[gm]["solo"] += 1
        elif r["winner"] == player_name:
            per_game[gm]["wins"] += 1

    # Streaks (bara flerspelarmatchar)
    streak = 0
    best_streak = 0
    current_streak = 0
    for r in multi_results:
        if r["winner"] == player_name:
            current_streak += 1
            best_streak = max(best_streak, current_streak)
        else:
            current_streak = 0
    if multi_results:
        streak_val = 0
        is_win = multi_results[-1]["winner"] == player_name
        for r in reversed(multi_results):
            if (r["winner"] == player_name) == is_win:
                streak_val += 1
            else:
                break
        streak = streak_val if is_win else -streak_val

    # X01-snitt
    x01_avg = 0
    x01_rounds = 0
    x01_total = 0
    for r in results:
        if r["game_mode"] == "x01":
            pr = r.get("player_results", {}).get(player_name, {})
            rounds = pr.get("rounds", 0)
            total_score = pr.get("total_score", 0)
            if rounds > 0:
                x01_rounds += rounds
                x01_total += total_score
    if x01_rounds > 0:
        x01_avg = x01_total / x01_rounds

    # Rekord per speltyp
    records = _calc_player_records(player_name, results)

    multi_total = len(multi_results)
    return {
        "total_games": total,
        "solo_games": solo_games,
        "wins": wins,
        "win_rate": (wins / multi_total * 100) if multi_total > 0 else 0,
        "per_game": per_game,
        "streak": streak,
        "best_streak": best_streak,
        "x01_avg": x01_avg,
        "records": records,
    }


def _calc_player_records(player_name, results):
    """Beräkna rekord per speltyp för en spelare."""
    records = {}

    for r in results:
        gm = r["game_mode"]
        pr = r.get("player_results", {}).get(player_name, {})
        if not pr:
            continue

        if gm not in records:
            records[gm] = {}

        if gm == "x01":
            rounds = pr.get("rounds", 0)
            darts = pr.get("darts", 0)
            total_score = pr.get("total_score", 0)
            remaining = pr.get("remaining", None)
            if remaining == 0 and darts > 0:
                # Snabbaste vinst (minst pilar)
                prev = records[gm].get("min_darts")
                if prev is None or darts < prev:
                    records[gm]["min_darts"] = darts
            if rounds > 0:
                avg = total_score / rounds
                prev = records[gm].get("best_avg")
                if prev is None or avg > prev:
                    records[gm]["best_avg"] = round(avg, 1)

        elif gm in ("highscore", "shanghai"):
            score = pr.get("score", 0)
            prev = records[gm].get("best_score")
            if prev is None or score > prev:
                records[gm]["best_score"] = score
            round_scores = pr.get("round_scores", [])
            if round_scores:
                best_round = max(round_scores)
                prev_r = records[gm].get("best_round")
                if prev_r is None or best_round > prev_r:
                    records[gm]["best_round"] = best_round

        elif gm == "golf":
            score = pr.get("score", 0)
            prev = records[gm].get("best_score")
            if prev is None or (score < prev and score > 0):
                records[gm]["best_score"] = score
            hole_scores = pr.get("hole_scores", [])
            if hole_scores:
                best_hole = min(hole_scores)
                prev_h = records[gm].get("best_hole")
                if prev_h is None or best_hole < prev_h:
                    records[gm]["best_hole"] = best_hole

        elif gm == "halveit":
            score = pr.get("score", 0)
            prev = records[gm].get("best_score")
            if prev is None or score > prev:
                records[gm]["best_score"] = score

        elif gm == "cricket":
            score = pr.get("score", 0)
            prev = records[gm].get("best_score")
            if prev is None or score > prev:
                records[gm]["best_score"] = score

        elif gm == "around_the_clock":
            pos = pr.get("position", 1)
            if pos > 21:
                records[gm]["completions"] = records[gm].get("completions", 0) + 1

        elif gm in ("killer", "triple_killer", "hits_killer"):
            lives = pr.get("lives", 0)
            if not pr.get("eliminated", True):
                records[gm]["survivals"] = records[gm].get("survivals", 0) + 1

    return records


def get_head_to_head(player_a, player_b):
    """Beräkna head-to-head-statistik mellan två spelare.

    Returnerar dict med wins_a, wins_b, draws (aldrig i dart),
    per_game, recent (senaste 10), streaks.
    """
    results = _load_results()
    shared = [r for r in results if player_a in r["players"] and player_b in r["players"]
              and len(r["players"]) > 1]

    wins_a = sum(1 for r in shared if r["winner"] == player_a)
    wins_b = sum(1 for r in shared if r["winner"] == player_b)

    per_game = {}
    for r in shared:
        gm = r["game_mode"]
        if gm not in per_game:
            per_game[gm] = {"a": 0, "b": 0, "total": 0}
        per_game[gm]["total"] += 1
        if r["winner"] == player_a:
            per_game[gm]["a"] += 1
        elif r["winner"] == player_b:
            per_game[gm]["b"] += 1

    # Streak: vem leder just nu?
    current_streak_player = None
    current_streak_count = 0
    if shared:
        last_winner = shared[-1]["winner"]
        current_streak_player = last_winner
        for r in reversed(shared):
            if r["winner"] == last_winner:
                current_streak_count += 1
            else:
                break

    # Längsta streak per spelare
    best_a = 0
    best_b = 0
    cur_a = 0
    cur_b = 0
    for r in shared:
        if r["winner"] == player_a:
            cur_a += 1
            cur_b = 0
            best_a = max(best_a, cur_a)
        elif r["winner"] == player_b:
            cur_b += 1
            cur_a = 0
            best_b = max(best_b, cur_b)

    return {
        "total": len(shared),
        "wins_a": wins_a,
        "wins_b": wins_b,
        "per_game": per_game,
        "recent": shared[-10:],
        "streak_player": current_streak_player,
        "streak_count": current_streak_count,
        "best_streak_a": best_a,
        "best_streak_b": best_b,
    }


def get_form_data(player_name, last_n=20):
    """Hämta formdata för en spelare (senaste N flerspelarmatchar).

    Returnerar lista med dicts: [{game_mode, won, timestamp, opponent}]
    """
    results = get_results_by_player(player_name)
    multi = [r for r in results if len(r["players"]) > 1]
    recent = multi[-last_n:]

    form = []
    for r in recent:
        opponents = [p for p in r["players"] if p != player_name]
        form.append({
            "game_mode": r["game_mode"],
            "won": r["winner"] == player_name,
            "timestamp": r["timestamp"],
            "opponents": opponents,
        })
    return form


def get_leaderboard():
    """Returnera topplista: [(namn, vinster, spelade, win%)].

    Solo-matcher (1 spelare) räknas inte.
    Sorterad efter flest vinster, sedan högst win%.
    """
    results = _load_results()
    multi_results = [r for r in results if len(r["players"]) > 1]
    stats = {}
    for r in multi_results:
        for p in r["players"]:
            if p not in stats:
                stats[p] = {"wins": 0, "played": 0}
            stats[p]["played"] += 1
            if r["winner"] == p:
                stats[p]["wins"] += 1

    board = []
    for name, s in stats.items():
        pct = (s["wins"] / s["played"] * 100) if s["played"] > 0 else 0
        board.append((name, s["wins"], s["played"], pct))

    board.sort(key=lambda x: (-x[1], -x[3]))
    return board
