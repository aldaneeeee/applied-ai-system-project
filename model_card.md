# Model Card: Music Recommender Simulation

---

## 1. Model Name

**VibeScore 1.0**

A rule-based music recommender that scores songs against a listener's stated preferences
and returns the top five most relevant tracks from a small curated catalog.

---

## 2. Intended Use

**What it's for:**
VibeScore 1.0 is a classroom simulation designed to show how music recommendation systems
make decisions. It takes a user preference profile — favorite genre, mood, target energy
level, and a few other settings — and ranks a 28-song catalog from most to least relevant.
It is built for learning and experimentation, not for deployment in a real product.

**What it's not for:**
This system should not be used to recommend music to real users. The catalog is too small
(28 songs), the scoring rules are hand-crafted rather than learned from data, and the system
has no way to adapt to feedback or listening history. It also should not be used to evaluate
the quality of real recommender systems — its behavior reflects deliberate design choices
for teaching purposes, not industry best practices.

---

## 3. How the Model Works

VibeScore 1.0 scores every song in the catalog on five rules, adds up the points, and
returns the five highest-scoring songs.

**The five rules (max 5.0 points total):**

1. **Genre match (+1.0 pt):** If the song's genre matches the user's favorite genre exactly,
   it gets a full point. This is a yes-or-no check — "pop" matches "pop" but not "indie pop."

2. **Mood match (+1.0 pt):** Same idea for mood. "Happy" only matches "happy," not "playful"
   or "energetic," even if those feel similar.

3. **Energy similarity (up to +2.0 pts):** The scoring measures how close the song's energy
   level (a number from 0 to 1) is to the user's target. A perfect match scores the full 2.0.
   Every 0.10 gap costs 0.20 points. This is currently the most influential rule.

4. **Acousticness similarity (up to +0.5 pts):** Rewards songs whose acoustic texture — warm
   and unplugged vs. electric and produced — matches the user's preference.

5. **Tempo similarity (up to +0.5 pts):** Rewards songs whose BPM is close to the user's
   target tempo. A 50 BPM difference costs about 0.13 points.

Songs are sorted from highest to lowest score and the top five are displayed with a breakdown
showing how many points each rule contributed.

**Change from the original design:** The original starter logic weighted genre at +2.0 and
energy at +1.0. After a weight-shift experiment showed that the +2.0 genre bonus caused
songs with the wrong mood and wrong feel to outrank better matches, the weights were
rebalanced to genre +1.0 and energy +2.0. This makes the system more sensitive to sonic
feel and less dependent on the genre label alone.

---

## 4. Data

The catalog contains **28 songs** across **25 unique genres**, hand-curated to cover a wide
range of musical styles. Each song has ten attributes: a title, artist name, genre label,
mood label, and six numeric features — energy (0–1), tempo in BPM, valence (0–1),
danceability (0–1), and acousticness (0–1).

**Genre coverage is intentionally uneven.** Lofi has 3 songs, pop has 2, and every other
genre has exactly 1. This was not corrected because the imbalance itself is useful for
testing — it exposes how genre depth affects ranking quality.

**Moods represented:** happy (4 songs), chill (3), intense, relaxed, moody, peaceful,
romantic, angry, and energetic (2 each), plus one song each for focused, melancholy,
nostalgic, sad, playful, hopeful, and dreamy.

**What's missing:** The catalog has no country pop, no indie folk, no reggaeton, and no
classical crossover. Genres like jazz, blues, bossa nova, and gospel each have a single
representative song, so users who prefer those styles can only ever receive one genre
match — the remaining four recommendations will come from different genres entirely.
The scoring also accepts danceability and valence as user inputs but does not use them
in the final calculation, so those two dimensions of taste are effectively invisible
to the algorithm.

---

## 5. Strengths

VibeScore 1.0 works well in three situations.

**When the catalog has depth for the target genre:** Lofi and pop users can receive multiple
genre-matching results, so their top five feels cohesive. The Chill Lofi profile returned
three lofi songs in the top three slots, which matches exactly what a study-session listener
would want.

**When all five signals point the same direction:** The High-Energy Pop profile (genre=pop,
mood=happy, energy=0.82) produced a near-perfect #1 result — "Sunrise City" scored 4.97/5.00
because it matched on genre, mood, energy, acousticness, and tempo simultaneously. When a
user's stated preferences align with a real song in the catalog, the ranking is both accurate
and intuitive.

**When explaining its decisions:** Every result comes with a per-rule breakdown showing
exactly how many points each rule contributed. This makes the system's reasoning fully
transparent — a user (or a student) can see at a glance whether a song ranked highly because
of a genre match, a close energy value, or both.

---

## 6. Limitations and Bias

**Discovered weakness — Energy scoring creates a genre-blind filter bubble.**
The energy similarity formula scores closeness on a single linear axis (`1 − |target − actual|`),
which means it cannot distinguish *why* a user wants high energy. A listener who wants
high-energy pop and a listener who wants high-energy metal receive identical energy scores
for every song in the catalog, so after the genre-match bonus is exhausted, both profiles
surface the same cluster of high-energy songs regardless of whether those songs are
stylistically appropriate. This effect worsens as energy weight increases: during a
weight-shift experiment (energy raised to +2.0), a pop profile's #2–4 slots were filled by
disco, indie pop, and reggae purely because their energy values happened to be close — the
system treated sonic texture, genre culture, and production style as irrelevant. A second
compounding bias is catalog depth inequality: lofi has three songs and pop has two, while
23 other genres each have exactly one, meaning a rock or blues listener can receive at most
one genre-matching result before the remaining four slots fall back entirely on
continuous-feature similarity. Users whose preferred genre is underrepresented are therefore
systematically pushed toward a "best numeric approximation" rather than a genuine genre
recommendation. Finally, the profile accepts `target_danceability` and `target_valence` as
inputs but `score_song()` silently ignores both fields, so any preference signal a user
expresses through those dimensions has zero effect on their results.

---

## 7. Evaluation

**Profiles tested:** Seven profiles were run — three standard (High-Energy Pop, Chill Lofi,
Deep Intense Rock) designed to produce intuitive results, and four adversarial (Sad Gym Beast,
Genre Ghost, Fence-Sitter, Acoustic High-Energy) designed to stress-test the scoring under
conflicting or missing inputs.

**What I looked for:** For standard profiles, I checked whether the #1 result was the most
obvious genre+mood+energy match and whether the #2–5 results felt like reasonable
alternatives. For adversarial profiles, I watched for whether the system degraded gracefully
or collapsed to nonsensical results.

**What surprised me:** Three findings stood out. First, the Fence-Sitter (all numeric targets
at 0.50, no genre/mood match in catalog) produced a surprisingly decisive winner — "Dusty
Road Home" scored 4.77 while #2 scored only 2.81, because the country and nostalgic labels
happened to exist in the catalog and matched perfectly despite the profile being designed to
have no signal. Second, the Deep Intense Rock profile exposed the catalog depth problem
clearly: rock has only one song, so "Storm Runner" scores 4.96 at #1, but #2–5 (pop, punk,
electronic, latin) score 2.84–3.91 and are ranked entirely by energy similarity with no
genre connection. Third, the Sad Gym Beast adversarial profile revealed that "Rainy Day
Blues" still wins #1 despite being a slow blues song for a profile that declared
target energy 0.93 — the genre+mood double-match (+2.0 points combined) outweighed the
energy mismatch, which is arguably the correct result but also means the system returns
a song the user would never actually want playing at the gym.

**Weight-shift experiment:** Doubling the energy weight (from +1.0 to +2.0) and halving
genre (from +2.0 to +1.0) caused Profile 1's #2–4 ranking to shuffle significantly: Gym Hero
(pop, wrong mood) dropped from #2 to #4, overtaken by Disco Fever and Rooftop Lights, which
matched on mood and energy even though neither is pop. This confirmed that energy weight
controls how strongly the system prioritizes sonic feel over categorical genre identity.

---

## 8. Future Work

**1. Wire in danceability and valence.**
Both fields are already collected in the user profile but ignored by the scoring function.
Adding them as tie-breaker dimensions — each worth up to +0.25 pts — would let users signal
preferences like "I want something upbeat and positive" (high valence) or "I want to dance
to it" (high danceability) without those signals disappearing silently.

**2. Replace exact mood matching with fuzzy similarity.**
Right now "happy" never matches "playful" or "energetic," even though a user who wants happy
music would probably enjoy either. A simple similarity table that groups adjacent moods
(happy ↔ playful ↔ energetic, sad ↔ melancholy, chill ↔ relaxed ↔ peaceful) would give
partial credit rather than all-or-nothing, reducing the gap between label vocabulary and
real human taste.

**3. Expand the catalog to at least 3 songs per genre.**
The single biggest structural problem is that 23 out of 25 genres have one song. Any user
whose favorite genre falls in that group gets only one genre-relevant result, and the other
four slots are filled by numeric approximations. Adding two more songs per underrepresented
genre would make genre a meaningful ranking factor rather than a one-shot bonus.

---

## 9. Personal Reflection

**Biggest learning moment**

The most clarifying moment came during the weight-shift experiment. I changed a single
number — the genre weight from 2.0 to 1.0 — and Gym Hero dropped from #2 to #4, replaced
by Disco Fever and Rooftop Lights. That felt surprising at first, but then it made total
sense: those two songs had the right mood and nearly the right energy, and now the algorithm
could actually "see" that. The learning wasn't that the new weights were better — it was
that every weight is a claim about what matters most to the listener, and changing it is a
design decision, not just a math change. I had been treating the numbers as fixed, but
they're actually assumptions that can be questioned.

**Using AI tools — and when I had to double-check them**

AI tools were useful throughout, but they required oversight at almost every step. When I
used Agent Mode to apply the weight-shift, the agent correctly updated the formula and the
inline comments — but I still had to verify manually that the new maximum score still totaled
5.0 (1.0 + 1.0 + 2.0 + 0.5 + 0.5). If any one of those line-level edits had been off by
a small amount, the score bar in the terminal output would have silently been wrong. The
agent did the mechanical work faster than I could, but I had to understand the math well
enough to know what to check. I also used inline chat to ask why a specific song ranked
first — and the explanation it gave was accurate, but only because I had already read the
scoring code myself. If I hadn't, I wouldn't have known whether to trust the answer.

**What surprised me about simple algorithms feeling like real recommendations**

I expected the output to feel obviously fake — a small catalog, hand-written rules, no
machine learning. But "Sunrise City" scoring 4.97/5.00 for the High-Energy Pop profile felt
genuinely correct. It matched on every dimension: genre, mood, energy to two decimal places,
acousticness, and tempo. For a moment it felt like the system understood music. What actually
happened was that the profile and the song were defined using the same vocabulary, so of
course they aligned. The "intelligence" was really just consistency between the input format
and the catalog format. That's the part that surprised me — how much of what feels like a
smart recommendation is actually just careful data design, not algorithmic sophistication.

**What I would try next**

The change I most want to make is fuzzy mood matching. Right now "happy" and "playful" score
zero points together even though they're emotionally adjacent. A simple similarity table that
gives partial credit to related moods would make the recommendations feel more natural without
requiring any new data. After that, I would wire in the danceability and valence fields that
the profile already accepts but the scoring function silently ignores. Both changes are small
in terms of code but would meaningfully close the gap between what the user tells the system
and what the system actually responds to.
