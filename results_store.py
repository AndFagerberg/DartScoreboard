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
        total_games, wins, win_rate, per_game (dict med stats per speltyp)
    """
    results = get_results_by_player(player_name)
    total = len(results)
    wins = sum(1 for r in results if r["winner"] == player_name)

    per_game = {}
    for r in results:
        gm = r["game_mode"]
        if gm not in per_game:
            per_game[gm] = {"played": 0, "wins": 0}
        per_game[gm]["played"] += 1
        if r["winner"] == player_name:
            per_game[gm]["wins"] += 1

    return {
        "total_games": total,
        "wins": wins,
        "win_rate": (wins / total * 100) if total > 0 else 0,
        "per_game": per_game,
    }


def get_leaderboard():
    """Returnera topplista: [(namn, vinster, spelade, win%)].

    Sorterad efter flest vinster, sedan högst win%.
    """
    results = _load_results()
    stats = {}
    for r in results:
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
