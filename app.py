import streamlit as st
from src.recommender import load_songs, recommend_songs

# ── Page config ──────────────────────────────────────────────
st.set_page_config(
    page_title="VibeScore 1.0",
    page_icon="🎵",
    layout="centered",
)

# ── Load catalog once ─────────────────────────────────────────
@st.cache_data
def get_songs():
    return load_songs("data/songs.csv")

SONGS = get_songs()

GENRES = sorted({s["genre"] for s in SONGS})
MOODS  = sorted({s["mood"]  for s in SONGS})

# ── Header ────────────────────────────────────────────────────
st.title("🎵 VibeScore 1.0")
st.caption("A rule-based music recommender — CodePath Applied AI Final Project")
st.divider()

# ── Sidebar: user profile inputs ──────────────────────────────
with st.sidebar:
    st.header("Your Taste Profile")

    genre_option = st.selectbox("Favorite Genre", ["— type a custom genre —"] + GENRES)
    if genre_option == "— type a custom genre —":
        genre = st.text_input("Custom genre (e.g. opera, reggaeton)", value="opera")
    else:
        genre = genre_option

    mood = st.selectbox("Favorite Mood", MOODS, index=MOODS.index("happy"))

    st.markdown("---")
    energy       = st.slider("Energy",       0.0, 1.0, 0.75, 0.01,
                             help="0 = very calm, 1 = very intense")
    acousticness = st.slider("Acousticness", 0.0, 1.0, 0.20, 0.01,
                             help="0 = electric/produced, 1 = warm/acoustic")
    tempo        = st.slider("Tempo (BPM)",  55,  180, 120,
                             help="Beats per minute")

    st.markdown("---")
    k = st.radio("Number of recommendations", [3, 5, 10], index=1)
    run = st.button("Find My Songs", use_container_width=True, type="primary")

# ── Main area ─────────────────────────────────────────────────
if not run:
    st.markdown(
        """
        ### How it works
        1. Set your taste profile in the sidebar on the left.
        2. Click **Find My Songs**.
        3. Each result shows a score out of 5.0 and a breakdown of why it ranked there.

        **Scoring rules (max 5.0 pts):**

        | Rule | Points |
        |---|---|
        | Genre match | +1.0 |
        | Mood match | +1.0 |
        | Energy similarity | up to +2.0 |
        | Acousticness similarity | up to +0.5 |
        | Tempo similarity | up to +0.5 |
        """
    )
    st.info("👈 Open the sidebar to set your preferences, then hit **Find My Songs**.")

else:
    user_prefs = {
        "favorite_genre":      genre,
        "favorite_mood":       mood,
        "target_energy":       energy,
        "target_acousticness": acousticness,
        "target_tempo_bpm":    tempo,
    }

    results = recommend_songs(user_prefs, SONGS, k=k)

    st.subheader(f"Top {k} picks for you")
    st.caption(
        f"genre=**{genre}** · mood=**{mood}** · "
        f"energy=**{energy}** · acousticness=**{acousticness}** · tempo=**{tempo} BPM**"
    )
    st.divider()

    for rank, (song, score, explanation) in enumerate(results, 1):
        confidence = score / 5.0

        # Choose medal for top 3
        medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(rank, f"#{rank}")

        with st.container():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"### {medal} {song['title']}")
                st.caption(f"{song['artist']} · {song['genre']} / {song['mood']}")
            with col2:
                st.metric("Score", f"{score:.2f} / 5.00")

            st.progress(confidence, text=f"Confidence: {confidence:.0%}")

            with st.expander("Why this song?"):
                for reason in explanation.split("; "):
                    st.markdown(f"- {reason}")

                st.markdown("---")
                col_a, col_b, col_c = st.columns(3)
                col_a.metric("Energy",       song["energy"])
                col_b.metric("Acousticness", song["acousticness"])
                col_c.metric("Tempo",        f"{song['tempo_bpm']} BPM")

            st.divider()

    # Summary bar
    avg_conf = sum(s for _, s, _ in results) / (len(results) * 5.0)
    top_score = results[0][1]

    if top_score >= 4.5:
        st.success(f"Strong match found! Your #1 pick scored {top_score:.2f}/5.00.")
    elif top_score >= 3.0:
        st.warning(
            f"Decent match — top score {top_score:.2f}/5.00. "
            "Try adjusting energy or acousticness for a closer fit."
        )
    else:
        st.error(
            f"Weak match — top score only {top_score:.2f}/5.00. "
            f"'{genre}' may have limited catalog coverage. "
            "Results are the closest numeric approximations available."
        )
