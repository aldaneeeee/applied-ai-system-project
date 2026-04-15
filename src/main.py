"""
Command line runner for the Music Recommender Simulation.
"""

from src.recommender import load_songs, recommend_songs

# Terminal display width used for divider lines
_WIDTH = 60


def _score_bar(score: float, max_score: float = 5.0, width: int = 20) -> str:
    """Return a filled/empty block progress bar scaled to score out of max_score."""
    filled = round((score / max_score) * width)
    return "█" * filled + "░" * (width - filled)


def _print_header(user_prefs: dict) -> None:
    print("=" * _WIDTH)
    print("  🎵  Music Recommender")
    print("=" * _WIDTH)
    print(f"  Profile  : {user_prefs['favorite_genre']} / {user_prefs['favorite_mood']}")
    print(f"  Energy   : {user_prefs.get('target_energy', '—')}")
    print(f"  Acoustic : {user_prefs.get('target_acousticness', '—')}")
    print(f"  Tempo    : {user_prefs.get('target_tempo_bpm', '—')} BPM")
    print("=" * _WIDTH)


def _print_recommendation(rank: int, song: dict, score: float, explanation: str) -> None:
    """Print a single ranked recommendation with its score bar and per-rule reasons."""
    score_display = _score_bar(score)
    print(f"\n  #{rank}  {song['title']}")
    print(f"       {song['artist']}  [{song['genre']} / {song['mood']}]")
    print(f"       Score : {score:.2f} / 5.00  {score_display}")
    print("       Why   :")
    for reason in explanation.split("; "):
        print(f"         • {reason}")


def main() -> None:
    """Load the song catalog, run the recommender for the default profile, and print results."""
    songs = load_songs("data/songs.csv")

    # ------------------------------------------------------------------
    # Default "pop / happy" profile
    # ------------------------------------------------------------------
    # Switched from the rock/intense profile used during algorithm design
    # to the pop/happy baseline so the top results can be verified against
    # songs we expect to rank highly: Sunrise City, Rooftop Lights, etc.
    #
    # Numeric targets chosen to match a typical upbeat pop song:
    #   energy        0.80  — lively but not exhausting
    #   acousticness  0.20  — produced/electric sound preferred
    #   tempo_bpm     120   — standard pop dance tempo
    # ------------------------------------------------------------------
    user_prefs = {
        "favorite_genre":      "pop",
        "favorite_mood":       "happy",
        "target_energy":       0.80,
        "target_acousticness": 0.20,
        "target_tempo_bpm":    120,
        "target_valence":      0.85,
        "target_danceability": 0.80,
        "likes_acoustic":      False,
    }

    recommendations = recommend_songs(user_prefs, songs, k=5)

    _print_header(user_prefs)
    print(f"\n  Top {len(recommendations)} recommendations:\n")
    print("-" * _WIDTH)

    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        _print_recommendation(rank, song, score, explanation)

    print("\n" + "=" * _WIDTH)


if __name__ == "__main__":
    main()
