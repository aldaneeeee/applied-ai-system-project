# VibeScore 1.0 — AI Music Recommender System

> Final project for the **CodePath Applied AI Course**

---

## Title & Summary

**VibeScore 1.0** is a rule-based music recommendation engine that scores every song in a
curated catalog against a listener's stated preferences and returns the top five most relevant
tracks — with a transparent, per-rule explanation of why each song ranked where it did.

This project matters because recommendation systems shape what billions of people hear, watch,
and read every day.It's literally what builds our algorithm and part of out digital profile. Building one forces you to confront the design decisions that are usually hidden inside a black box: What features matter most? How do you weight them? What happens when the user's preferences contradict each other? VibeScore 1.0 makes those decisions visible and debuggable.

---

## Original Project (Modules 1–3)

This project began in **Module 3** of the CodePath Applied AI course as a
**Music Recommender Simulation**. The original goal was to represent songs and user taste
profiles as structured data, design a point-based scoring rule to turn that data into ranked
recommendations, and evaluate where the system succeeded and where it failed. The starter
system awarded **+2.0 points for a genre match** and **+1.0 for energy similarity**, which
prioritized categorical labels over continuous feel. This final project builds on that
foundation by rebalancing the weights, adding adversarial evaluation profiles, and documenting
the full system with tests, a model card, and this README.

---

## Architecture Overview

The system is organized into four layers:

```
INPUT
  data/songs.csv (28-song catalog)  +  User Profiles (3 standard + 4 adversarial)
        |
        v
PROCESS
  load_songs()       — reads CSV, casts numeric fields, returns list of dicts
        |
        v
  score_song()       — applies 5-rule point formula to each song (max 5.0 pts)
        |
        v
  recommend_songs()  — sorts all scored songs, returns top-k with explanations
        |
        v
  main.py            — runs all 7 profiles end-to-end, formats output
        |
        v
OUTPUT
  Terminal: ranked songs with ASCII score bars and per-rule breakdowns

TESTING & HUMAN REVIEW
  tests/test_recommender.py  — automated checks (sort order, non-empty explanations)
  Adversarial profiles       — human review of edge-case outputs
```

**Scoring rules — max 5.0 points per song:**

| Rule | Points | Signal |
|---|---|---|
| Genre match | +1.0 | Exact label match — defines the sonic category |
| Mood match | +1.0 | Exact label match — the emotional character |
| Energy similarity | up to +2.0 | `(1 − |target − actual|) × 2.0` — strongest continuous signal |
| Acousticness similarity | up to +0.5 | Distance from user's warm/produced preference |
| Tempo similarity | up to +0.5 | BPM gap normalized over 0–200 BPM |

The `Recommender` class and `UserProfile` data class in `src/recommender.py` provide a clean
OOP interface used by the test suite. The functional `score_song` / `recommend_songs` API in
the same file is used by `src/main.py` for full evaluation runs.

---

## Setup Instructions

**Requirements:** Python 3.9+

**1. Clone the repository**

```bash
git clone <your-repo-url>
cd applied-ai-system-final
```

**2. Create and activate a virtual environment (recommended)**

```bash
python -m venv .venv
source .venv/bin/activate       # Mac / Linux
.venv\Scripts\activate          # Windows
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

**4. Run the recommender**

```bash
python -m src.main
```

This runs all seven evaluation profiles (three standard + four adversarial) and prints ranked
results with score bars and per-rule explanations to the terminal.

**5. Run the tests**

```bash
pytest
```

---

## Sample Interactions

### Example 1 — High-Energy Pop (standard profile)

**Input profile:**

```
genre=pop  mood=happy  energy=0.82  acousticness=0.15  tempo=122 BPM
```

**Output (top result):**

```
#1  Sunrise City
    Neon Pulse  [pop / happy]
    Score : 4.97 / 5.00  ████████████████████
    Why   :
      • genre match (+1.0)
      • mood match (+1.0)
      • energy similarity (+1.97)
      • acousticness similarity (+0.50)
      • tempo similarity (+0.50)
```

**What this shows:** When a user's preferences align with a song across all five dimensions,
the scoring is both accurate and intuitive. "Sunrise City" earned a near-perfect score because
it matched every signal simultaneously — this is the system working exactly as intended.

---

### Example 2 — Genre Ghost (adversarial profile)

**Input profile:**

```
genre=opera  mood=peaceful  energy=0.25  acousticness=0.90  tempo=65 BPM
```

`opera` does not exist in the catalog, so the +1.0 genre bonus can never fire.

**Output (top results):**

```
#1  Moonlight Reverie
    Luna Strings  [classical / peaceful]
    Score : 3.23 / 5.00 
    Why   :
      • genre mismatch — song is classical (+0.0)
      • mood match (+1.0)
      • energy similarity (+1.87)
      • acousticness similarity (+0.48)
      • tempo similarity (+0.38)

#2  Autumn Porch
    Birch & Rain  [folk / peaceful]
    Score : 3.10 / 5.00 
```

**What this shows:** When the user's preferred genre is missing from the catalog, the system
degrades gracefully — falling back to continuous features and mood to surface genuinely
adjacent results (quiet, acoustic, peaceful classical and folk). A missing label causes clean
fallback. A contradictory label, as in Example 3, causes messier behavior.

---

### Example 3 — Sad Gym Beast (adversarial profile)

**Input profile:**

```
genre=blues  mood=sad  energy=0.93  acousticness=0.10  tempo=150 BPM
```

The mood/energy combination is deliberately contradictory — "sad" blues listeners expect slow,
low-energy music, but the numeric targets point toward metal and EDM.

**Output (top result):**

```
#1  Rainy Day Blues
    Muddy Creek  [blues / sad]
    Score : 3.46 / 5.00 
    Why   :
      • genre match (+1.0)
      • mood match (+1.0)
      • energy similarity (+0.07)
      • acousticness similarity (+0.39)
      • tempo similarity (+0.00)
```

**What this shows:** The genre + mood double-match (combined +2.0) outweighed the large energy
gap, so the #1 result is technically correct by label but wrong by feel — a slow delta blues
track is not what someone targeting energy=0.93 at 150 BPM would want at the gym. Slots #2–5
then snap entirely to high-energy songs with no blues connection at all. This is the clearest
demonstration of the core tension in the scoring design.

---

## Design Decisions

**Why rule-based scoring instead of machine learning?**
The goal was to build something fully transparent and debuggable. A neural model would perform
better on a large dataset, but it would hide its reasoning. A rule-based system lets you see
exactly why a song ranked where it did — which is essential for a learning project where the
value comes from questioning the rules, not just accepting the output.

**Why shift energy weight from +1.0 to +2.0 and genre from +2.0 to +1.0?**
The original starter design gave genre a +2.0 bonus, which caused songs with completely wrong
energy and mood to outrank better matches just because their genre label matched. A
weight-shift experiment confirmed that doubling energy weight and halving genre weight made the
system more sensitive to sonic feel. The trade-off: genre is now only a tie-breaker in many
cases, so a pop fan might see more cross-genre results. That is an acceptable cost for a system
where "it feels right" matters more than label correctness.

**Why include adversarial profiles?**
Standard profiles only confirm the system works under ideal conditions. Adversarial profiles
expose how the system behaves at the edges — a genre that doesn't exist, all numeric targets
at the ambiguous midpoint, or contradictory mood/energy signals. Real users are constantly
at the edges. A Spotify user who wants opera is not unusual; they just get surfaced as an edge
case when the catalog is small.

**Known trade-offs:**

- `target_danceability` and `target_valence` are collected in the user profile but silently
  ignored by the scorer. This is the highest-priority future fix — wiring them in as +0.25
  tie-breakers each would meaningfully extend the system without redesigning anything.
- Exact string matching for genre and mood means "happy" never partially matches "playful."
  Fuzzy mood grouping (a simple similarity table giving partial credit to adjacent moods)
  would close this gap without any new data.
- 23 of 25 genres in the catalog have exactly one song. Any user whose favorite genre falls
  there gets only one genre-matching result; the remaining four slots are pure numeric
  approximations of songs from completely different genres.

---

## Testing Summary

**Automated tests** (`tests/test_recommender.py`) cover two things:

1. **Sort order** — verifies that results are ordered highest score first and that the correct
   song (pop / happy) ranks #1 for a pop / happy / high-energy user.
2. **Explanation quality** — verifies that every recommendation comes with a non-empty,
   human-readable explanation string.

Both tests pass consistently and serve as a regression guard whenever scoring weights change.

**What the tests do not cover:** semantic correctness. Automated tests can verify that results
are sorted and explanations are non-empty, but they cannot check whether the #1 result actually
sounds like what the user wants. That judgment requires human review — which is why the seven
evaluation profiles in `main.py` exist alongside the automated suite.

**Key findings from the evaluation runs:**

- The **Fence-Sitter** profile (all numeric targets at 0.50, no genre/mood match) was designed
  to produce near-ties. Instead, "Dusty Road Home" scored 4.77 while #2 scored only 2.81 —
  a lucky catalog coincidence (country/nostalgic both exist) caused a decisive win despite
  intentionally weak signal. The system can appear very confident even when it has almost no
  real information.

- The **weight-shift experiment** (genre +1.0, energy +2.0) caused Profile 1's #2–4 ranking
  to shuffle significantly. Gym Hero dropped from #2 to #4, replaced by Disco Fever and
  Rooftop Lights — songs with the right mood and energy but a different genre. Changing one
  number changed the implicit claim about what matters most to the listener.

- The **Genre Ghost** adversarial profile degraded more gracefully than the Sad Gym Beast
  profile. A missing label causes clean fallback to continuous features. A contradictory label
  (sad mood + 0.93 energy target) causes the system to hedge between two incompatible signals
  and return a result that is technically correct but practically useless.

- The **Deep Intense Rock** profile exposed the catalog depth problem clearly. Rock has only
  one song, so "Storm Runner" scores 4.96 at #1 — but #2 through #5 are pop, punk, electronic,
  and latin, ranked entirely by energy similarity with no genre connection whatsoever.

---

## Reflection

Building VibeScore 1.0 as part of the CodePath Applied AI course changed how I think about
recommendation systems in two concrete ways.

**Weights are design claims,it's neither random nor math facts.** When I changed genre weight from 2.0 to 1.0, I
was not just adjusting a formula — I was making a statement that sonic feel matters more than
a categorical label. The algorithm does not know which claim is true; it executes whatever I
decided. Every real recommender system — Spotify, YouTube, Netflix, ect — is full of decisions like
that, most of them invisible to the user. Building one from scratch made those decisions
visible and forced me to defend them out loud.

**"Intelligent" output can come from consistent data design, not real understanding.** When
"Sunrise City" scored 4.97/5.00 for the High-Energy Pop profile, it felt like the system
understood music. It did not. What happened was that the profile and the song were defined
using the same vocabulary — same genre string, overlapping numeric ranges — so of course they
aligned. The "intelligence" was careful data design. That distinction matters enormously when
evaluating real AI systems: a model that performs perfectly in testing may be measuring its
own consistency rather than genuine comprehension.

The most important skill this project taught is knowing when to trust the output and when to
go look at the code. This is a critical part of the project to know when to trust the output and when to go review the code because you catch that the output is slightly inaccurate. Human review is not a fallback for when the system fails. It is part of the system and process.

---

## Extra Credit Features

### Test Harness and Evaluation Script (+2 pts)

`eval_harness.py` is a standalone evaluation script that runs the recommender against
8 predefined test cases and prints a structured pass/fail summary with confidence scores.

**Run it:**

```bash
python eval_harness.py
```

**Sample output:**

```
==============================================================
  VIBESCORE 1.0 — EVALUATION HARNESS
==============================================================

  [PASS] (conf=0.99)  Test 1: Returns exactly k=5 results
         returned 5 results as expected

  [PASS] (conf=0.99)  Test 2: Scores are sorted descending
         scores correctly sorted: [4.96, 3.91, 3.84, 3.72, 3.68]

  [PASS] (conf=0.96)  Test 3: All scores within valid range
         all scores within [0.0, 5.0]

  [PASS] (conf=0.99)  Test 4: Pop/happy profile: #1 result is a pop song
         #1 is 'Sunrise City' (pop) — score 4.97

  [PASS] (conf=0.98)  Test 5: Lofi/chill profile: #1 result is a lofi song
         #1 is 'Library Rain' (lofi) — score 4.90

  [PASS] (conf=0.99)  Test 6: Rock/intense profile: #1 result is a rock song
         #1 is 'Storm Runner' (rock) — score 4.96

  [PASS] (conf=0.65)  Test 7: Unknown genre: graceful fallback (no crash)
         graceful fallback — 5 results returned, top score 3.23 (no genre bonus fired)

  [PASS] (conf=0.74)  Test 8: All results have non-empty explanations
         all 5 results have non-empty explanations

--------------------------------------------------------------
  Results : 8 / 8 passed
  Avg confidence (top-result score / 5.0) : 0.911
  Status  : ALL TESTS PASSED
==============================================================
```

**What the confidence score means:** Each test reports the top-ranked song's score divided
by 5.0 (the maximum possible). Tests 1–6 show confidence above 0.96 — the system is
certain when genre and energy align. Test 7 (unknown genre) drops to 0.65, correctly
signaling that the system is working from incomplete information.

---

### Fine-Tuning and Specialization (+2 pts)

The weight-shift experiment documents measurable behavioral change from a single parameter
adjustment — the closest analog to fine-tuning in a rule-based system.

**Baseline (original weights):** genre +2.0, energy +1.0

**After specialization:** genre +1.0, energy +2.0

**Measured impact on Profile 1 (High-Energy Pop):**

| Rank | Baseline | After Weight Shift |
|---|---|---|
| #1 | Sunrise City (pop/happy) | Sunrise City (pop/happy) |
| #2 | Gym Hero (pop/intense) | Disco Fever (disco/happy) |
| #3 | Rooftop Lights (indie pop) | Rooftop Lights (indie pop) |
| #4 | Disco Fever (disco/happy) | Gym Hero (pop/intense) |
| #5 | Island Morning (reggae) | Island Morning (reggae) |

Gym Hero dropped from #2 to #4. Disco Fever rose from #4 to #2 — not because it is a
pop song (it is not), but because its energy value (0.87) is closer to the user's target
(0.82) than Gym Hero's (0.93). The rebalancing made the system more sensitive to sonic
feel and less dependent on genre label, which is the intended specialization.

---

### RAG Enhancement and Agentic Workflow (stretch goals)

These two features were not implemented in this version but are documented here as the
most natural next steps for extending the project.

**RAG Enhancement:** The current system retrieves from a single 28-song flat CSV. A RAG
extension would index songs by embedding their genre + mood + energy description as a
vector, then retrieve the nearest neighbors using cosine similarity rather than a
hand-written scoring formula. This would allow the system to work across a catalog of
thousands of songs and surface matches the rule engine would never find.

**Agentic Workflow:** A multi-step agent version would first ask clarifying questions
("Are you working out or winding down?"), then select a scoring weight profile based on
the answer, then run the recommender, and finally explain its chain of reasoning at each
step. The intermediate steps — profile selection, weight choice, score computation —
would be logged and visible in output rather than collapsed into a single ranked list.

---

## Project Structure

```
applied-ai-system-final/
├── data/
│   └── songs.csv               # 28-song catalog with 10 features per song
├── src/
│   ├── main.py                 # Evaluation runner — 3 standard + 4 adversarial profiles
│   └── recommender.py          # Core logic: Song, UserProfile, Recommender, score_song
├── tests/
│   └── test_recommender.py     # Automated regression tests (pytest)
├── eval_harness.py             # Test harness — 8 predefined test cases with pass/fail summary
├── model_card.md               # Limitations, bias, ethics, and AI collaboration reflection
└── requirements.txt
```

---

## Portfolio Artifact

**GitHub Repository:**
[https://github.com/aldaneeeee/applied-ai-system-project](https://github.com/aldaneeeee/applied-ai-system-project)

**What this project says about me as an AI engineer:**

VibeScore 1.0 shows that I approach AI not as a black box to deploy, but as a system to
understand, question, and honestly evaluate. I did not just build something that produces
output. I built adversarial test cases designed to break it, ran a controlled experiment
to measure how a single weight change shifted behavior, and documented the results including
the moments where the system was wrong . I know how to distinguish between a
model that performs well and a model that merely looks like it performs well, and I know
that gap is where most real world AI failures live. I can write clean, testable code, think
critically about bias and edge cases, and communicate technical decisions to an audience that
was not in the room when those decisions were made. I am able to test, break, and rebuild a project. 

---

## About This Course

This project was built as the final submission for the **CodePath Applied AI course** — a
hands on program that walks students through building, evaluating, and reflecting on
AI-powered systems from the ground up. The course emphasizes not just making AI work, but
understanding why it works, where it fails, and what human judgment is still required even
when the output looks correct. This course taught me how to build off of AI rather than fully depending on it, using it as a tool to help clean and perfect my vision for a project.
