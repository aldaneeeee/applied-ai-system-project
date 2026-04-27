"""
Evaluation harness for VibeScore 1.0.

Runs the recommender against 8 predefined test cases and prints a structured
pass/fail summary with confidence scores. Satisfies the Test Harness extra-credit
requirement: a script that evaluates the system on multiple predefined inputs and
prints a summary of results.

Usage:
    python eval_harness.py
"""

from src.recommender import load_songs, recommend_songs

_WIDTH = 62
_SONGS = load_songs("data/songs.csv")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _confidence(score: float, max_score: float = 5.0) -> float:
    """Return score as a 0.0–1.0 confidence ratio."""
    return round(score / max_score, 3)


def _run_test(name: str, user_prefs: dict, check_fn, k: int = 5):
    """
    Run one test case and return a result dict.

    check_fn receives the list of (song, score, explanation) tuples and returns
    (passed: bool, detail: str).
    """
    try:
        results = recommend_songs(user_prefs, _SONGS, k=k)
        passed, detail = check_fn(results)
        top_score = results[0][1] if results else 0.0
        confidence = _confidence(top_score)
    except Exception as exc:
        passed, detail, confidence = False, f"EXCEPTION: {exc}", 0.0

    return {
        "name":       name,
        "passed":     passed,
        "detail":     detail,
        "confidence": confidence,
    }


# ---------------------------------------------------------------------------
# Test cases
# ---------------------------------------------------------------------------

def test_returns_correct_count():
    """System returns exactly k results for a well-formed profile."""
    prefs = {"favorite_genre": "pop", "favorite_mood": "happy",
             "target_energy": 0.82, "target_acousticness": 0.15,
             "target_tempo_bpm": 122}

    def check(results):
        if len(results) == 5:
            return True, f"returned {len(results)} results as expected"
        return False, f"expected 5 results, got {len(results)}"

    return _run_test("Returns exactly k=5 results", prefs, check)


def test_scores_sorted_descending():
    """All returned scores are in non-increasing order."""
    prefs = {"favorite_genre": "rock", "favorite_mood": "intense",
             "target_energy": 0.92, "target_acousticness": 0.08,
             "target_tempo_bpm": 155}

    def check(results):
        scores = [s for _, s, _ in results]
        for i in range(len(scores) - 1):
            if scores[i] < scores[i + 1]:
                return False, f"score at position {i} ({scores[i]}) < position {i+1} ({scores[i+1]})"
        return True, f"scores correctly sorted: {[round(s, 2) for s in scores]}"

    return _run_test("Scores are sorted descending", prefs, check)


def test_scores_within_bounds():
    """Every score falls within the valid 0.0–5.0 range."""
    prefs = {"favorite_genre": "lofi", "favorite_mood": "chill",
             "target_energy": 0.38, "target_acousticness": 0.80,
             "target_tempo_bpm": 76}

    def check(results):
        for song, score, _ in results:
            if not (0.0 <= score <= 5.0):
                return False, f"'{song['title']}' has out-of-bounds score {score}"
        return True, "all scores within [0.0, 5.0]"

    return _run_test("All scores within valid range", prefs, check)


def test_pop_happy_top_result():
    """A pop/happy user's #1 result should be a pop song."""
    prefs = {"favorite_genre": "pop", "favorite_mood": "happy",
             "target_energy": 0.82, "target_acousticness": 0.15,
             "target_tempo_bpm": 122}

    def check(results):
        top_song, top_score, _ = results[0]
        if top_song["genre"] == "pop":
            return True, f"#{1} is '{top_song['title']}' (pop) — score {top_score:.2f}"
        return False, (f"expected genre=pop at #1, "
                       f"got genre={top_song['genre']} ('{top_song['title']}')")

    return _run_test("Pop/happy profile: #1 result is a pop song", prefs, check)


def test_lofi_chill_top_result():
    """A lofi/chill user's #1 result should be a lofi song."""
    prefs = {"favorite_genre": "lofi", "favorite_mood": "chill",
             "target_energy": 0.38, "target_acousticness": 0.80,
             "target_tempo_bpm": 76}

    def check(results):
        top_song, top_score, _ = results[0]
        if top_song["genre"] == "lofi":
            return True, f"#1 is '{top_song['title']}' (lofi) — score {top_score:.2f}"
        return False, (f"expected genre=lofi at #1, "
                       f"got genre={top_song['genre']} ('{top_song['title']}')")

    return _run_test("Lofi/chill profile: #1 result is a lofi song", prefs, check)


def test_rock_intense_top_result():
    """A rock/intense user's #1 result should be a rock song."""
    prefs = {"favorite_genre": "rock", "favorite_mood": "intense",
             "target_energy": 0.92, "target_acousticness": 0.08,
             "target_tempo_bpm": 155}

    def check(results):
        top_song, top_score, _ = results[0]
        if top_song["genre"] == "rock":
            return True, f"#1 is '{top_song['title']}' (rock) — score {top_score:.2f}"
        return False, (f"expected genre=rock at #1, "
                       f"got genre={top_song['genre']} ('{top_song['title']}')")

    return _run_test("Rock/intense profile: #1 result is a rock song", prefs, check)


def test_unknown_genre_graceful_fallback():
    """A user with a genre not in the catalog still gets 5 results without crashing."""
    prefs = {"favorite_genre": "opera", "favorite_mood": "peaceful",
             "target_energy": 0.25, "target_acousticness": 0.90,
             "target_tempo_bpm": 65}

    def check(results):
        if len(results) == 5:
            top_song, top_score, _ = results[0]
            # Genre ghost: no genre match possible, so score must be < 4.0
            if top_score < 4.0:
                return True, (f"graceful fallback — 5 results returned, "
                              f"top score {top_score:.2f} (no genre bonus fired)")
            return False, f"top score {top_score:.2f} suspiciously high for unknown genre"
        return False, f"expected 5 results, got {len(results)}"

    return _run_test("Unknown genre: graceful fallback (no crash)", prefs, check)


def test_all_explanations_non_empty():
    """Every recommendation must include a non-empty explanation string."""
    prefs = {"favorite_genre": "jazz", "favorite_mood": "relaxed",
             "target_energy": 0.37, "target_acousticness": 0.89,
             "target_tempo_bpm": 90}

    def check(results):
        for i, (song, _, explanation) in enumerate(results):
            if not explanation or not explanation.strip():
                return False, f"result #{i+1} ('{song['title']}') has empty explanation"
        return True, "all 5 results have non-empty explanations"

    return _run_test("All results have non-empty explanations", prefs, check)


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def main():
    tests = [
        test_returns_correct_count,
        test_scores_sorted_descending,
        test_scores_within_bounds,
        test_pop_happy_top_result,
        test_lofi_chill_top_result,
        test_rock_intense_top_result,
        test_unknown_genre_graceful_fallback,
        test_all_explanations_non_empty,
    ]

    results = [t() for t in tests]

    passed = sum(1 for r in results if r["passed"])
    total = len(results)
    avg_confidence = round(sum(r["confidence"] for r in results) / total, 3)

    print("\n" + "=" * _WIDTH)
    print("  VIBESCORE 1.0 — EVALUATION HARNESS")
    print("=" * _WIDTH)

    for i, r in enumerate(results, 1):
        status = "PASS" if r["passed"] else "FAIL"
        conf   = f"conf={r['confidence']:.2f}"
        print(f"\n  [{status}] ({conf})  Test {i}: {r['name']}")
        print(f"         {r['detail']}")

    print("\n" + "-" * _WIDTH)
    print(f"  Results : {passed} / {total} passed")
    print(f"  Avg confidence (top-result score / 5.0) : {avg_confidence:.3f}")

    if passed == total:
        print("  Status  : ALL TESTS PASSED")
    elif passed >= total - 1:
        print("  Status  : MOSTLY PASSING — review failing test above")
    else:
        print(f"  Status  : {total - passed} TESTS FAILED — see details above")

    print("=" * _WIDTH + "\n")


if __name__ == "__main__":
    main()
