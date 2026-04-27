# Model Card: VibeScore 1.0 — Music Recommender Simulation

> Built as part of the **CodePath Applied AI Course**

---

## 1. Model Name

**VibeScore 1.0**

A rule-based music recommender that scores songs against a listener's stated preferences and
returns the top five most relevant tracks, each with a transparent per-rule score breakdown.

---

## 2. Intended Use

**What it is for:**
VibeScore 1.0 is a classroom simulation designed to show how music recommendation systems make
decisions. It takes a user preference profile — favorite genre, mood, target energy level, and
acoustic texture — and ranks a 28-song catalog from most to least relevant. It is built for
learning and experimentation, not for deployment in a real product.

**What it is not for:**
This system should not be used to recommend music to real users. The catalog is too small
(28 songs), the scoring rules are hand-crafted rather than learned from data, and the system
has no way to adapt to feedback or listening history. It should not be used to evaluate the
quality of real recommender systems — its behavior reflects deliberate design choices for
teaching purposes, not industry best practices.

---

## 3. How the Model Works

VibeScore 1.0 scores every song in the catalog on five rules, adds up the points, and returns
the five highest-scoring songs.

**The five rules (max 5.0 points total):**

1. **Genre match (+1.0 pt):** If the song's genre matches the user's favorite genre exactly,
   it earns a full point. This is a yes-or-no check — "pop" matches "pop" but not "indie pop."

2. **Mood match (+1.0 pt):** Same logic for mood. "Happy" only matches "happy," not "playful"
   or "energetic," even if those feel similar to a human listener.

3. **Energy similarity (up to +2.0 pts):** Measures how close the song's energy level (0–1)
   is to the user's target. A perfect match scores the full 2.0. This is currently the most
   influential rule.

4. **Acousticness similarity (up to +0.5 pts):** Rewards songs whose acoustic texture —
   warm and unplugged vs. electric and produced — matches the user's preference.

5. **Tempo similarity (up to +0.5 pts):** Rewards songs whose BPM is close to the user's
   target tempo, normalized over a 0–200 BPM range.

**Weight change from the original design:** The starter logic weighted genre at +2.0 and
energy at +1.0. After a weight-shift experiment showed that the +2.0 genre bonus allowed
songs with the wrong feel to outrank better matches, the weights were rebalanced to genre +1.0
and energy +2.0. This makes the system more sensitive to sonic feel and less dependent on the
genre label alone.

---

## 4. Data

The catalog contains **28 songs** across **25 unique genres**, hand-curated to cover a wide
range of musical styles. Each song has ten attributes: title, artist, genre label, mood label,
and six numeric features — energy (0–1), tempo in BPM, valence (0–1), danceability (0–1),
and acousticness (0–1).

**Genre coverage is intentionally uneven.** Lofi has 3 songs, pop has 2, and every other
genre has exactly 1. This imbalance was kept because it is useful for testing — it exposes
how catalog depth affects ranking quality.

**Moods represented:** happy (4 songs), chill (3), intense, relaxed, moody, peaceful,
romantic, angry, and energetic (2 each), with one song each for focused, melancholy,
nostalgic, sad, playful, hopeful, and dreamy.

**What is missing:** No country pop, no indie folk, no reggaeton, no classical crossover.
Jazz, blues, bossa nova, and gospel each have a single representative, so users who prefer
those styles receive only one genre match — the remaining four recommendations come from
entirely different genres. The scoring also accepts `target_danceability` and `target_valence`
as user inputs but does not use them in the final calculation, so those two dimensions of
taste are invisible to the algorithm.

---

## 5. Strengths

VibeScore 1.0 works well in three situations.

**When the catalog has depth for the target genre:** Lofi and pop users receive multiple
genre-matching results, so their top five feels cohesive. The Chill Lofi profile returned
three lofi songs in the top three slots, which matches exactly what a study-session listener
would want.

**When all five signals point the same direction:** The High-Energy Pop profile produced a
near-perfect #1 result — "Sunrise City" scored 4.97/5.00 because it matched on genre, mood,
energy, acousticness, and tempo simultaneously. When a user's stated preferences align with
a real song in the catalog, the ranking is both accurate and intuitive.

**When explaining its decisions:** Every result includes a per-rule breakdown showing exactly
how many points each rule contributed. The reasoning is fully transparent — a user can see
at a glance whether a song ranked highly because of a genre match, a close energy value, or
both.

---

## 6. Proving It Works: Testing and Reliability

### Automated Tests

Two unit tests live in `tests/test_recommender.py` and run with `pytest`:

| Test | What It Checks | Result |
|---|---|---|
| `test_recommend_returns_songs_sorted_by_score` | Results are ordered highest-first; pop/happy song ranks #1 for a pop/happy user | Passes |
| `test_explain_recommendation_returns_non_empty_string` | Every recommendation includes a non-empty explanation string | Passes |

Both tests pass consistently and act as a regression guard — if a weight change accidentally
breaks sort order or drops explanations, the tests catch it immediately.

### Human Evaluation Across 7 Profiles

Beyond automated tests, the system was evaluated by running it against seven deliberately
designed profiles and reviewing whether the output made sense:

| Profile | Type | Result |
|---|---|---|
| High-Energy Pop | Standard | #1 scored 4.97/5.00 — correct and intuitive |
| Chill Lofi | Standard | Top 3 were all lofi/chill — correct |
| Deep Intense Rock | Standard | #1 correct; #2–5 reverted to energy-only with no genre connection |
| Sad Gym Beast | Adversarial | #1 technically correct by label, wrong by feel |
| Genre Ghost | Adversarial | Graceful fallback to adjacent genres — better than expected |
| Fence-Sitter | Adversarial | Unexpectedly decisive winner due to catalog coincidence |
| Acoustic High-Energy | Adversarial | Genuinely confused — returned an electric latin track for a folk request |

**Summary:** 5 out of 7 profiles produced output that was reasonable or better. The system
struggled in the 2 cases where user signals directly contradicted each other (Sad Gym Beast,
Acoustic High-Energy). Confidence was highest when genre and energy agreed; it collapsed when
they pointed in opposite directions.

### Confidence Scoring

The scoring formula itself acts as a built-in confidence signal. A song that scores 4.5–5.0
matched on multiple dimensions simultaneously and is a high-confidence recommendation. A song
that scores below 3.0 won only on continuous features with no label match — the system is
effectively saying "this is the closest thing I have, not a real match."

Across the standard profiles, top-ranked songs averaged **4.6 / 5.0**. Across adversarial
profiles, top-ranked songs averaged **3.5 / 5.0** — a measurable drop that correctly signals
the system is less certain.

### What Automated Tests Cannot Cover

Automated tests verified structure (sort order, non-empty strings) but not meaning. A test
cannot check whether "Rainy Day Blues" is a bad gym song — that requires a human to read the
output and recognize that a slow blues track does not match a target energy of 0.93. Human
review is not a fallback; it is a required layer of the evaluation.

---

## 7. Limitations and Bias

**Energy scoring creates a genre-blind filter bubble.**
The energy similarity formula scores closeness on a single linear axis, which means it cannot
distinguish *why* a user wants high energy. A pop fan and a metal fan both set energy=0.90
and receive identical energy scores for every song — after the genre-match bonus is exhausted,
both profiles surface the same cluster of high-energy songs regardless of whether those songs
fit the style. This effect worsened when energy weight was raised to +2.0 during the
weight-shift experiment: a pop profile's #2–4 slots filled with disco, indie pop, and reggae
purely because their energy values were numerically close.

**Catalog depth inequality.**
Lofi has 3 songs, pop has 2, and 23 other genres each have exactly 1. A rock or blues
listener can receive at most one genre-matching result — the remaining four fall back entirely
to continuous-feature similarity. Users whose preferred genre is underrepresented are
systematically pushed toward a "best numeric approximation" rather than a genuine genre match.

**Silent input fields.**
The profile accepts `target_danceability` and `target_valence` as inputs, but `score_song()`
silently ignores both. Any preference signal a user expresses through those dimensions has
zero effect on their results. This is a known gap and the highest-priority future fix.

**Single-user, static taste.**
Every recommendation assumes one unchanging taste profile. Real listening shifts by context —
working, working out, relaxing — but the system treats the user as always wanting the same
thing. There is no session awareness, no feedback loop, and no history.

---

## 8. Reflection and Ethics

### Could This System Be Misused?

At its current scale (28 songs, classroom use), the risk is low. But the patterns it
demonstrates appear in real products at massive scale, and the same design flaws become
genuinely harmful there:

- **Filter bubbles at scale.** A genre-weighted recommender running on millions of users
  could systematically under-surface music from genres that are underrepresented in the
  catalog. Artists from smaller or non-Western genres get fewer plays, less revenue, and
  less algorithmic exposure — a feedback loop that concentrates attention on already-popular
  genres.

- **Taste homogenization.** A system that always returns the closest match — never diverse,
  never surprising — gradually narrows what users hear. Over time users may not realize their
  taste has been shaped by the algorithm rather than their own exploration.

- **Silent bias in ignored fields.** If `danceability` and `valence` were wired in for some
  user groups but not others, those groups would receive systematically different
  recommendation quality with no visible indication of the disparity.

**How to prevent it:** Require that every input field actually affects output (no silent
ignoring). Run periodic audits comparing recommendation rates across genre and mood categories.
Add a diversity parameter that occasionally surfaces lower-scoring but stylistically distinct
results. Be transparent with users about what signals the system uses.

### What Surprised Me During Testing

The **Fence-Sitter** profile was the biggest surprise. It was designed to produce near-ties
by setting all numeric targets at 0.50 and using a genre/mood pair (country/nostalgic) that
felt unlikely to match anything strongly. Instead, "Dusty Road Home" scored 4.77/5.00 while
#2 scored only 2.81. A country/nostalgic song happened to exist in the catalog, and the
genre + mood double-match (+2.0 combined) created a decisive winner despite the profile being
built to have almost no signal.

The lesson: the system can appear very confident even when its reasoning is based on a lucky
coincidence. Confidence scores alone do not tell you whether the recommendation was *good* —
they only tell you how well the profile and song descriptions happened to overlap. That is a
meaningful distinction in any AI system.

### Collaboration With AI During This Project

AI tools (GitHub Copilot and Claude) were used throughout this project. Here is one honest
example of each kind of outcome:

**One instance where the AI gave a helpful suggestion:**
When designing the adversarial profiles, I asked Copilot Chat (via `#codebase`) to suggest
edge cases that would stress-test the scoring logic. It proposed the "Genre Ghost" concept —
a user whose preferred genre does not exist in the catalog at all — which I had not thought of.
That profile turned out to produce some of the most interesting results in the entire
evaluation: it showed that missing labels cause graceful fallback, while contradictory labels
cause messy hedging. That distinction became one of the key findings in the reflection.

**One instance where the AI suggestion was flawed:**
When I used an AI agent to apply the weight-shift experiment (changing genre from +2.0 to
+1.0 and energy from +1.0 to +2.0), the agent correctly updated the formula and the inline
comments — but it did not verify that the new weights still summed to the same maximum of
5.0. I had to manually re-check that `1.0 + 1.0 + 2.0 + 0.5 + 0.5 = 5.0` to confirm the
score bar in the terminal output was still calibrated correctly. If I had not understood the
math well enough to know what to check, the terminal output would have silently displayed
wrong score percentages. The AI did the mechanical work faster than I could, but it did not
think about the system as a whole — that responsibility stayed with me.

---

## 9. Future Work

**1. Wire in danceability and valence.**
Both fields are collected in the user profile but ignored by the scorer. Adding them as
tie-breaker dimensions — each worth up to +0.25 pts — would close the gap between what the
user tells the system and what the system actually responds to.

**2. Replace exact mood matching with fuzzy similarity.**
Right now "happy" never matches "playful" or "energetic." A simple similarity table giving
partial credit to adjacent moods (happy ↔ playful ↔ energetic, sad ↔ melancholy, chill ↔
relaxed ↔ peaceful) would make recommendations feel more natural without requiring any new
data.

**3. Expand the catalog to at least 3 songs per genre.**
The single biggest structural problem is that 23 of 25 genres have one song. Adding two more
songs per underrepresented genre would make genre a meaningful ranking factor rather than a
one-shot bonus that runs out after the first result.

**4. Add a diversity parameter.**
The algorithm always returns the closest match. A tunable diversity knob that occasionally
surfaces lower-scoring but stylistically distinct results would reduce filter-bubble effects
and surface songs the user might not have found otherwise.
