# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

---

## How The System Works

### Song Features

Each song in `data/songs.csv` is described by nine features:

| Feature | Type | Description |
|---|---|---|
| `genre` | text | Broad musical category (rock, lofi, jazz, pop, …) |
| `mood` | text | Emotional tone (happy, intense, chill, melancholy, …) |
| `energy` | 0.0 – 1.0 | Physical intensity — high for metal/EDM, low for ambient/lofi |
| `tempo_bpm` | number | Beats per minute (55 BPM lofi → 180 BPM metal) |
| `valence` | 0.0 – 1.0 | Emotional positivity (1.0 = joyful, 0.0 = dark/tense) |
| `danceability` | 0.0 – 1.0 | How suitable the track is for dancing |
| `acousticness` | 0.0 – 1.0 | Acoustic warmth vs. electric/produced sound |

### User Profile

The `UserProfile` stores a listener's taste targets:

- `favorite_genre` — preferred genre label
- `favorite_mood` — preferred mood label
- `target_energy` — ideal energy level on the 0.0–1.0 scale
- `likes_acoustic` — whether the user prefers acoustic or produced sounds

The functional API in `main.py` extends this with `target_acousticness`, `target_tempo_bpm`, `target_valence`, and `target_danceability` for finer-grained matching.

### Algorithm Recipe

Every song in the catalog is scored against the user profile. Scores are summed, and the top-k songs are returned as recommendations.

**Maximum possible score: 5.0 points**

```
+2.0 pts   Genre match
           Strongest signal. Genre defines the sonic universe —
           a rock fan hearing jazz feels like a wrong recommendation
           regardless of other features.

+1.0 pt    Mood match
           Secondary label. "Happy rock" and "moody rock" share
           production style but feel completely different.
           Weighted at half of genre so it refines rather than overrides.

+1.0 pt    Energy similarity   (continuous)
           Formula: (1 - |target_energy - song_energy|) × 1.0
           Best numeric discriminator. Separates "intense rock" (≈ 0.91)
           from "chill lofi" (≈ 0.40) with a 0.51-point gap even when
           genre and mood labels don't match.

+0.5 pt    Acousticness similarity   (continuous)
           Formula: (1 - |target_acousticness - song_acousticness|) × 0.5
           Captures warm/unplugged vs. electric/produced texture.
           Half-weight keeps it as a tie-breaker, not a primary driver.

+0.5 pt    Tempo similarity   (continuous, normalised over 0–200 BPM)
           Formula: (1 - |target_tempo - song_tempo| / 200) × 0.5
           A 50-BPM gap costs ~0.125 pts — noticeable but not decisive.
```

Songs are ranked highest-score-first and the top 5 are shown by default.

### Potential Biases

- **Genre over-prioritization.** The +2.0 genre bonus dominates the score. A song that perfectly matches the user's energy, mood, acousticness, and tempo but belongs to a different genre will almost never outscore a weak genre match. Great cross-genre discoveries (e.g. a jazz track with rock-level energy) will be buried.

- **Catalog representation.** The 28-song dataset skews toward Western genres. Genres like k-pop, latin, and reggae each have only one representative, so users whose favorite genre is underrepresented will receive lower-quality matches by default.

- **Single-user design.** Every recommendation assumes one static taste profile. Real listening sessions shift by context (working, working out, relaxing), but the system treats the user as always wanting the same thing.

- **No novelty or diversity.** The algorithm always picks the closest match. A user who slightly prefers "chill" moods will receive five nearly identical chill songs rather than a mix that might surface something new.

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this


---

## 7. `model_card_template.md`

Combines reflection and model card framing from the Module 3 guidance. :contentReference[oaicite:2]{index=2}  

```markdown
# 🎧 Model Card - Music Recommender Simulation

## 1. Model Name

Give your recommender a name, for example:

> VibeFinder 1.0

---

## 2. Intended Use

- What is this system trying to do
- Who is it for

Example:

> This model suggests 3 to 5 songs from a small catalog based on a user's preferred genre, mood, and energy level. It is for classroom exploration only, not for real users.

---

## 3. How It Works (Short Explanation)

Describe your scoring logic in plain language.

- What features of each song does it consider
- What information about the user does it use
- How does it turn those into a number

Try to avoid code in this section, treat it like an explanation to a non programmer.

---

## 4. Data

Describe your dataset.

- How many songs are in `data/songs.csv`
- Did you add or remove any songs
- What kinds of genres or moods are represented
- Whose taste does this data mostly reflect

---

## 5. Strengths

Where does your recommender work well

You can think about:
- Situations where the top results "felt right"
- Particular user profiles it served well
- Simplicity or transparency benefits

---

## 6. Limitations and Bias

Where does your recommender struggle

Some prompts:
- Does it ignore some genres or moods
- Does it treat all users as if they have the same taste shape
- Is it biased toward high energy or one genre by default
- How could this be unfair if used in a real product

---

## 7. Evaluation

How did you check your system

Examples:
- You tried multiple user profiles and wrote down whether the results matched your expectations
- You compared your simulation to what a real app like Spotify or YouTube tends to recommend
- You wrote tests for your scoring logic

You do not need a numeric metric, but if you used one, explain what it measures.

---

## 8. Future Work

If you had more time, how would you improve this recommender

Examples:

- Add support for multiple users and "group vibe" recommendations
- Balance diversity of songs instead of always picking the closest match
- Use more features, like tempo ranges or lyric themes

---

## 9. Personal Reflection

A few sentences about what you learned:

- What surprised you about how your system behaved
- How did building this change how you think about real music recommenders
- Where do you think human judgment still matters, even if the model seems "smart"

