"""
Command line runner for the Music Recommender Simulation.

Runs seven user profiles — three standard and four adversarial — so the
scoring logic can be evaluated across normal and edge-case inputs.
"""

from src.recommender import load_songs, recommend_songs

_WIDTH = 62


def _score_bar(score: float, max_score: float = 5.0, width: int = 20) -> str:
    """Return a filled/empty block progress bar scaled to score out of max_score."""
    filled = round((score / max_score) * width)
    return "█" * filled + "░" * (width - filled)


def _print_section(label: str, note: str, user_prefs: dict) -> None:
    """Print a labelled profile header showing the key preference values."""
    print("\n" + "=" * _WIDTH)
    print(f"  {label}")
    if note:
        print(f"  [{note}]")
    print("=" * _WIDTH)
    print(f"  genre={user_prefs['favorite_genre']}  mood={user_prefs['favorite_mood']}")
    print(
        f"  energy={user_prefs.get('target_energy','—')}  "
        f"acousticness={user_prefs.get('target_acousticness','—')}  "
        f"tempo={user_prefs.get('target_tempo_bpm','—')} BPM"
    )
    print("-" * _WIDTH)


def _print_recommendation(rank: int, song: dict, score: float, explanation: str) -> None:
    """Print a single ranked recommendation with its score bar and per-rule reasons."""
    score_display = _score_bar(score)
    print(f"\n  #{rank}  {song['title']}")
    print(f"       {song['artist']}  [{song['genre']} / {song['mood']}]")
    print(f"       Score : {score:.2f} / 5.00  {score_display}")
    print("       Why   :")
    for reason in explanation.split("; "):
        print(f"         • {reason}")


def run_profile(label: str, note: str, user_prefs: dict, songs: list, k: int = 5) -> None:
    """Score the full catalog for one profile and print the top-k results."""
    _print_section(label, note, user_prefs)
    results = recommend_songs(user_prefs, songs, k=k)
    for rank, (song, score, explanation) in enumerate(results, start=1):
        _print_recommendation(rank, song, score, explanation)


def main() -> None:
    """Load the song catalog, run all evaluation profiles, and print results."""
    songs = load_songs("data/songs.csv")

    # ------------------------------------------------------------------
    # Standard profiles — expected to produce intuitive results
    # ------------------------------------------------------------------

    run_profile(
        label="PROFILE 1 — High-Energy Pop",
        note="standard: upbeat, danceable, produced sound",
        user_prefs={
            "favorite_genre":      "pop",
            "favorite_mood":       "happy",
            "target_energy":       0.82,
            "target_acousticness": 0.15,
            "target_tempo_bpm":    122,
            "target_valence":      0.88,
            "target_danceability": 0.85,
            "likes_acoustic":      False,
        },
        songs=songs,
    )

    run_profile(
        label="PROFILE 2 — Chill Lofi",
        note="standard: low energy, slow tempo, warm acoustic texture",
        user_prefs={
            "favorite_genre":      "lofi",
            "favorite_mood":       "chill",
            "target_energy":       0.38,
            "target_acousticness": 0.80,
            "target_tempo_bpm":    76,
            "target_valence":      0.58,
            "target_danceability": 0.55,
            "likes_acoustic":      True,
        },
        songs=songs,
    )

    run_profile(
        label="PROFILE 3 — Deep Intense Rock",
        note="standard: maximum energy, electric, fast, dark tone",
        user_prefs={
            "favorite_genre":      "rock",
            "favorite_mood":       "intense",
            "target_energy":       0.92,
            "target_acousticness": 0.08,
            "target_tempo_bpm":    155,
            "target_valence":      0.40,
            "target_danceability": 0.62,
            "likes_acoustic":      False,
        },
        songs=songs,
    )

    # ------------------------------------------------------------------
    # Adversarial profiles — designed to expose scoring weaknesses
    # (suggested via "System Evaluation" Copilot Chat session with #codebase)
    # ------------------------------------------------------------------

    run_profile(
        label="ADVERSARIAL 1 — Sad Gym Beast",
        note="conflict: mood=sad clashes with energy=0.93; expects low-energy "
             "songs (blues) but numeric targets pull toward metal/EDM",
        user_prefs={
            "favorite_genre":      "blues",
            "favorite_mood":       "sad",
            "target_energy":       0.93,
            "target_acousticness": 0.10,
            "target_tempo_bpm":    150,
            "target_valence":      0.25,
            "target_danceability": 0.70,
            "likes_acoustic":      False,
        },
        songs=songs,
    )

    run_profile(
        label="ADVERSARIAL 2 — Genre Ghost",
        note="genre='opera' does not exist in the catalog; genre match (+2.0) "
             "can never fire, so ranking relies entirely on continuous features",
        user_prefs={
            "favorite_genre":      "opera",
            "favorite_mood":       "peaceful",
            "target_energy":       0.25,
            "target_acousticness": 0.90,
            "target_tempo_bpm":    65,
            "target_valence":      0.70,
            "target_danceability": 0.30,
            "likes_acoustic":      True,
        },
        songs=songs,
    )

    run_profile(
        label="ADVERSARIAL 3 — The Fence-Sitter",
        note="all numeric targets at 0.50; no genre/mood match; the system "
             "has almost no signal and continuous features nearly tie",
        user_prefs={
            "favorite_genre":      "country",
            "favorite_mood":       "nostalgic",
            "target_energy":       0.50,
            "target_acousticness": 0.50,
            "target_tempo_bpm":    100,
            "target_valence":      0.50,
            "target_danceability": 0.50,
            "likes_acoustic":      False,
        },
        songs=songs,
    )

    run_profile(
        label="ADVERSARIAL 4 — Acoustic High-Energy",
        note="contradiction: high energy (0.88) + high acousticness (0.90); "
             "almost no real songs combine both — exposes catalog blind spots",
        user_prefs={
            "favorite_genre":      "folk",
            "favorite_mood":       "energetic",
            "target_energy":       0.88,
            "target_acousticness": 0.90,
            "target_tempo_bpm":    130,
            "target_valence":      0.75,
            "target_danceability": 0.72,
            "likes_acoustic":      True,
        },
        songs=songs,
    )

    print("\n" + "=" * _WIDTH)
    print("  Evaluation complete.")
    print("=" * _WIDTH + "\n")


if __name__ == "__main__":
    main()
