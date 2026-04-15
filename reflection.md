# Reflection: Profile Pair Comparisons

Each section below compares two profiles side-by-side — what changed in the output, and why
the difference makes sense given what each profile is actually testing for.

---

## Pair 1 — Profile 1 (High-Energy Pop) vs. Profile 2 (Chill Lofi)

These two profiles sit at opposite ends of the energy and acousticness spectrum. Profile 1
targets energy=0.82 and acousticness=0.15 (loud, produced), while Profile 2 targets
energy=0.38 and acousticness=0.80 (quiet, warm, textured).

The outputs flip almost completely. Profile 1's top result is "Sunrise City" (pop/happy,
energy=0.82), while Profile 2's top two results are "Library Rain" and "Midnight Coding" —
both lofi/chill songs with energy below 0.45 and acousticness above 0.70. Not a single song
appears in both top-5 lists.

This makes sense: energy and acousticness together are the strongest continuous discriminators
in the catalog. High-energy produced songs and low-energy acoustic songs occupy completely
different regions of the feature space, so the two profiles naturally pull from non-overlapping
pools. The results feel valid — a study-session lofi listener and a dance-floor pop listener
really do want different things.

One thing worth noting: Profile 2's #5 is "Coffee Shop Stories" (jazz/relaxed), which scores
2.90 despite having no genre or mood match. It earned its slot purely on energy (0.37, nearly
identical to the 0.38 target) and high acousticness (0.89). This shows the system can
accidentally surface adjacent genres as reasonable fallbacks when the catalog depth for the
target genre is limited.

---

## Pair 2 — Profile 1 (High-Energy Pop) vs. Profile 3 (Deep Intense Rock)

Both profiles want high energy and low acousticness, but they diverge on genre and mood —
pop/happy vs. rock/intense — and Profile 3 pushes even harder on energy (0.92 vs 0.82) and
tempo (155 BPM vs 122 BPM).

The #1 results are completely different and both feel correct: "Sunrise City" for pop and
"Storm Runner" for rock. The interesting comparison is what fills slots #2–5. Profile 1 gets
disco, indie pop, and reggae — all genre misses but mood=happy matches. Profile 3 gets pop,
punk, electronic, and latin — all genre misses with no mood match either, ranked purely by
energy proximity.

This reveals the catalog depth problem clearly. Pop has two songs in the catalog, so a pop
fan gets at least one more genre match at #4. Rock has only one song, so after "Storm Runner",
the rock fan is immediately pushed into pure energy-based recommendations with no stylistic
connection to rock at all. A real rock listener would probably reject "Fuego en la Pista"
(latin/energetic) as a rock recommendation, even though its energy score is nearly identical
to "Storm Runner."

---

## Pair 3 — Adversarial 1 (Sad Gym Beast) vs. Adversarial 2 (Genre Ghost)

These two adversarial profiles both have broken label signals, but in different ways.
Adversarial 1 has a genre that exists (blues) but a mood/energy contradiction: mood=sad
but target_energy=0.93 pulls toward metal and EDM. Adversarial 2 has a genre that does not
exist in the catalog at all (opera) but coherent continuous targets (low energy, high
acousticness, peaceful).

The outputs tell the story. Adversarial 1's #1 is "Rainy Day Blues" (blues/sad, score 3.46),
which is technically correct by label but feels wrong for a user who set energy=0.93 and
tempo=150 BPM — that user is not looking for a slow delta blues track. The genre+mood match
(+2.0 combined) simply outweighs the large energy gap. Slots #2–5 then snap to pure
high-energy songs (rock, pop, electronic, punk) with no blues connection.

Adversarial 2 actually performs more gracefully. With no genre match ever possible, the
system falls back entirely on continuous features and mood — and surfaces "Moonlight Reverie"
(classical/peaceful) and "Autumn Porch" (folk/peaceful) as the top two. These are genuinely
reasonable substitutes for someone who wanted opera: both are quiet, acoustic, and have a
peaceful character. The genre ghost case degrades more gracefully than the conflicted label
case, because a missing label causes clean fallback while a contradictory label causes the
system to split its attention between two incompatible signals.

---

## Pair 4 — Adversarial 3 (Fence-Sitter) vs. Adversarial 4 (Acoustic High-Energy)

Both profiles are designed to expose edge cases, but they fail in opposite directions.
The Fence-Sitter sets all numeric targets at 0.50 and uses a genre/mood pair (country/nostalgic)
that happens to exist in the catalog. Adversarial 4 gives very specific numeric targets
(energy=0.88, acousticness=0.90) that contradict each other — almost no real song is both
very loud and very acoustic at the same time.

The Fence-Sitter's result was the biggest surprise: despite being designed to produce near-ties,
"Dusty Road Home" (country/nostalgic) scored 4.77 while #2 scored only 2.81. The genre+mood
double match provided a +2.0 floor that no other song could reach, even though every numeric
feature was set to the ambiguous midpoint. The system found a clear winner despite the
intentionally weak signal — but only because of a lucky catalog coincidence, not good scoring.

Adversarial 4 produced the opposite outcome: the system was genuinely confused. "Fuego en
la Pista" (latin/energetic) ranked #1 with 3.60, earning its score entirely from mood match
and energy similarity — but its acousticness is 0.14, not 0.90. The user wanted a high-energy
acoustic folk song and the system delivered an electric latin track. The #3 result,
"Autumn Porch" (folk/peaceful), actually has the right genre and high acousticness (0.91),
but its low energy (0.33) tanked its score under the doubled energy weight. This is a direct
consequence of the weight-shift experiment: acoustic folk songs can never win when energy is
worth +2.0 and acoustic folk energy averages around 0.33.

---

## Overall Takeaway

The standard profiles show the system works well when the catalog has depth for the target
genre and when mood and energy point in the same direction. The adversarial profiles reveal
that the system's graceful fallback depends entirely on whether continuous features and label
features agree — when they contradict, the scoring hedges awkwardly rather than resolving
the conflict. The weight-shift experiment made this more visible by amplifying the energy
signal, which pushed genre-diverse songs to the surface and exposed how little the algorithm
understands that high energy means different things in different genres.
