import csv
from typing import List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float


@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py

    Critique insight: using only favorite_genre + favorite_mood is too narrow.
    A profile with just those two fields can only make binary (match / no-match)
    decisions. Adding numeric targets (target_energy, likes_acoustic) gives the
    algorithm a continuous signal, so it can rank "intense rock" far above "chill
    lofi" even when the genre label alone is ambiguous or missing.
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool


def _score_song_for_profile(profile: UserProfile, song: Song) -> Tuple[float, str]:
    """Return a (score, explanation) tuple for a Song scored against a UserProfile.

    Point scale (max 4.5 pts):
        +2.0  genre match          — primary label, biggest discriminator
        +1.0  mood match           — secondary label, captures the vibe
        +1.0  energy similarity    — continuous; 1.0 * (1 - |target - actual|)
        +0.5  acoustic preference  — 0.5 * acousticness or 0.5 * (1-acousticness)

    The 2:1 genre-to-mood ratio reflects that genre defines the broad sonic
    category (rock vs. jazz) while mood is a modifier within that category.
    Energy gets equal weight to mood because it separates "intense rock" from
    "chill lofi" numerically even when genre labels are absent or mixed.
    """
    score = 0.0
    reasons: List[str] = []

    # +2.0 — Genre match
    if song.genre == profile.favorite_genre:
        score += 2.0
        reasons.append(f"genre matches your favorite ({song.genre})")

    # +1.0 — Mood match
    if song.mood == profile.favorite_mood:
        score += 1.0
        reasons.append(f"mood '{song.mood}' fits your preference")

    # up to +1.0 — Energy similarity
    # Key differentiator: rock energy ≈ 0.91, lofi ≈ 0.40
    energy_pts = (1.0 - abs(profile.target_energy - song.energy)) * 1.0
    score += energy_pts
    if energy_pts >= 0.85:
        reasons.append(f"energy ({song.energy:.2f}) closely matches your target")

    # up to +0.5 — Acoustic preference
    # likes_acoustic=False rewards low-acousticness (electric/produced) sounds
    acoustic_pts = (song.acousticness if profile.likes_acoustic else (1.0 - song.acousticness)) * 0.5
    score += acoustic_pts
    if acoustic_pts >= 0.375:
        reasons.append("acoustic profile aligns with your preference")

    explanation = "; ".join(reasons) if reasons else "general style similarity"
    return round(score, 4), explanation


class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """

    def __init__(self, songs: List[Song]):
        """Store the catalog of Song objects used for all recommendations."""
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        """Return the top-k Songs ranked by score against the given UserProfile."""
        scored = [(song, _score_song_for_profile(user, song)[0]) for song in self.songs]
        scored.sort(key=lambda x: x[1], reverse=True)
        return [song for song, _ in scored[:k]]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        """Return a human-readable explanation of why a Song was recommended."""
        _, explanation = _score_song_for_profile(user, song)
        return explanation


# ---------------------------------------------------------------------------
# Functional API used by src/main.py
# ---------------------------------------------------------------------------

def load_songs(csv_path: str) -> List[Dict]:
    """Read songs.csv and return a list of dicts with numeric fields cast to float/int."""
    songs: List[Dict] = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            songs.append({
                "id":           int(row["id"]),
                "title":        row["title"],
                "artist":       row["artist"],
                "genre":        row["genre"],
                "mood":         row["mood"],
                "energy":       float(row["energy"]),
                "tempo_bpm":    float(row["tempo_bpm"]),
                "valence":      float(row["valence"]),
                "danceability": float(row["danceability"]),
                "acousticness": float(row["acousticness"]),
            })
    print(f"Loaded songs: {len(songs)}")
    return songs


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Score one song dict against user preferences and return (total_pts, reasons).

    Algorithm Recipe — point-based scoring for a single song.

    Scoring Logic Design (informed by songs.csv analysis):
    -------------------------------------------------------
    Rule 1  +2.0 pts  Genre match
            Rationale: genre is the strongest signal — it defines the sonic
            universe (rock vs. jazz vs. lofi). Weighted 2× mood because a
            wrong genre almost always means a wrong recommendation.

    Rule 2  +1.0 pt   Mood match
            Rationale: mood is a modifier within a genre. "Happy pop" and
            "moody pop" share production style but feel very different.
            Half the genre weight keeps it influential without overriding
            continuous features when genre is absent.

    Rule 3  up to +1.0 pt  Energy similarity
            Formula: (1 - |target_energy - song_energy|) * 1.0
            Rationale: energy is the single best continuous discriminator.
            It separates "intense rock" (≈0.91) from "chill lofi" (≈0.40)
            with a 0.51-point gap even when genre/mood labels don't match.
            Equal weight to mood means the vibe matters as much as the label.

    Rule 4  up to +0.5 pt  Acousticness similarity
            Formula: (1 - |target_acousticness - song_acousticness|) * 0.5
            Rationale: acoustic texture (warm/unplugged vs. electric/produced)
            strongly shapes listener experience. Half the mood weight keeps it
            as a tie-breaker rather than a primary signal.

    Rule 5  up to +0.5 pt  Tempo similarity
            Formula: (1 - |target_tempo_bpm - song_tempo_bpm| / 200) * 0.5
            Rationale: tempo controls physical energy and feel. Normalised
            over 0–200 BPM so a 50-BPM miss costs 0.125 pts — noticeable
            but not decisive.

    Maximum possible score: 2.0 + 1.0 + 1.0 + 0.5 + 0.5 = 5.0 pts
    """
    score = 0.0
    reasons: List[str] = []

    # Rule 1 — Genre match (+2.0)
    if song["genre"] == user_prefs.get("favorite_genre"):
        score += 2.0
        reasons.append("genre match (+2.0)")
    else:
        reasons.append(f"genre mismatch — song is {song['genre']} (+0.0)")

    # Rule 2 — Mood match (+1.0)
    if song["mood"] == user_prefs.get("favorite_mood"):
        score += 1.0
        reasons.append("mood match (+1.0)")
    else:
        reasons.append(f"mood mismatch — song is {song['mood']} (+0.0)")

    # Rule 3 — Energy similarity (up to +1.0)
    # Formula: (1 - |target_energy - song_energy|) * 1.0
    if "target_energy" in user_prefs:
        energy_pts = (1.0 - abs(user_prefs["target_energy"] - song["energy"])) * 1.0
        score += energy_pts
        reasons.append(f"energy similarity (+{energy_pts:.2f})")

    # Rule 4 — Acousticness similarity (up to +0.5)
    # Formula: (1 - |target_acousticness - song_acousticness|) * 0.5
    if "target_acousticness" in user_prefs:
        acoustic_pts = (1.0 - abs(user_prefs["target_acousticness"] - song["acousticness"])) * 0.5
        score += acoustic_pts
        reasons.append(f"acousticness similarity (+{acoustic_pts:.2f})")

    # Rule 5 — Tempo similarity (up to +0.5, normalised over 0–200 BPM)
    # Formula: (1 - |target_tempo - song_tempo| / 200) * 0.5
    if "target_tempo_bpm" in user_prefs:
        tempo_pts = (1.0 - abs(user_prefs["target_tempo_bpm"] - song["tempo_bpm"]) / 200.0) * 0.5
        score += tempo_pts
        reasons.append(f"tempo similarity (+{tempo_pts:.2f})")

    return round(score, 4), reasons


def recommend_songs(
    user_prefs: Dict, songs: List[Dict], k: int = 5
) -> List[Tuple[Dict, float, str]]:
    """Score every song in the catalog and return the top-k as (song, score, explanation) tuples.

    Pythonic design:
      - _rank() is a small helper that calls score_song and packages the
        result into the (song, score, explanation) tuple this function promises.
      - sorted() with a generator expression avoids building a temporary list
        before sorting; Python lazily evaluates each _rank(song) as it sorts.
      - key=lambda item: item[1] tells sorted() to compare by score (index 1).
      - reverse=True gives highest-first ordering.
      - [:k] slices off exactly the top-k results.
    """
    def _rank(song: Dict) -> Tuple[Dict, float, str]:
        """Call score_song and pack the result into the (song, score, explanation) tuple."""
        score, reasons = score_song(user_prefs, song)
        explanation = "; ".join(reasons) if reasons else "general style similarity"
        return song, score, explanation

    return sorted(
        (_rank(song) for song in songs),
        key=lambda item: item[1],
        reverse=True,
    )[:k]
