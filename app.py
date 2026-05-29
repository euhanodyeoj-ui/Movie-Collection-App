from pathlib import Path
import re
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Joey's Movie Crypt",
    page_icon="📼",
    layout="wide",
    initial_sidebar_state="collapsed",
)

DATA_PATH = Path(__file__).with_name("movie_library.csv")
TMDB_IMG_BASE = "https://image.tmdb.org/t/p/w500"


def clean_text(value, default=""):
    if value is None:
        return default
    text = str(value).strip()
    if text.lower() in {"nan", "none", "<na>"}:
        return default
    return text


def poster_url(row):
    """Return a browser-ready poster URL.

    This handles all formats that can appear in the workbook:
    - a direct https://image.tmdb.org/... URL in Cover URL
    - a TMDB poster path like /abc123.jpg in Poster Path
    - a Google Sheets =IMAGE("https://...") formula in Cover Image
    """
    direct = clean_text(row.get("Cover URL", ""))
    if direct.startswith("http"):
        return direct.replace("/w342/", "/w500/")

    formula = clean_text(row.get("Cover Image", ""))
    match = re.search(r'https?://[^"\)]+', formula)
    if match:
        return match.group(0).replace("/w342/", "/w500/")

    path = clean_text(row.get("Poster Path", ""))
    if path.startswith("/"):
        return f"{TMDB_IMG_BASE}{path}"
    return ""


@st.cache_data(show_spinner=False)
def load_data():
    df = pd.read_csv(DATA_PATH, keep_default_na=False)
    for col in df.columns:
        if df[col].dtype == object:
            df[col] = df[col].astype(str).fillna("")

    for col in ["Year", "Runtime (min)"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    for col in ["TMDB Rating", "My Rating (1-5)"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df["Poster Display URL"] = df.apply(poster_url, axis=1)
    if "Title" in df.columns:
        df = df[df["Title"].astype(str).str.strip() != ""].copy()
    return df


df = load_data()

st.markdown(
    """
<style>
[data-testid="stAppViewContainer"] {
    background:
      radial-gradient(circle at 12% 8%, rgba(151, 20, 28, .36), transparent 28%),
      radial-gradient(circle at 88% 3%, rgba(244, 184, 66, .14), transparent 26%),
      linear-gradient(180deg, #050405 0%, #13090b 48%, #050405 100%);
    color: #f8ead0;
}
.block-container { padding-top: 1rem; max-width: 1100px; }
[data-testid="stSidebar"] { background: #12080a; }
.crypt-title {
    font-size: clamp(2.25rem, 9vw, 5rem);
    line-height: .85;
    font-weight: 950;
    letter-spacing: .04em;
    color: #f7d37e;
    text-shadow: 0 0 14px rgba(151,20,28,.95), 4px 4px 0 #25080b;
    text-transform: uppercase;
    margin-bottom: .15rem;
}
.subtitle { color: #cdbd9f; margin-bottom: .9rem; }
.stat-card {
    background: linear-gradient(135deg, rgba(59,30,23,.92), rgba(16,8,8,.96));
    border: 1px solid rgba(247,211,126,.28);
    border-radius: 16px;
    padding: 12px 14px;
    box-shadow: 0 10px 26px rgba(0,0,0,.42);
}
.stat-number { font-size: 1.55rem; color: #f7d37e; font-weight: 900; }
.stat-label { color:#cdbd9f; font-size:.78rem; text-transform: uppercase; letter-spacing:.08em; }
.movie-card {
    background: linear-gradient(145deg, rgba(36,22,22,.98), rgba(10,7,7,.98));
    border: 1px solid rgba(247,211,126,.24);
    border-left: 10px solid rgba(151,20,28,.72);
    border-radius: 18px;
    padding: 12px;
    margin-bottom: 14px;
    box-shadow: inset 0 -8px 0 rgba(69,35,24,.45), 0 12px 28px rgba(0,0,0,.5);
}
.movie-title { font-size: 1.05rem; font-weight: 900; color:#fff2c7; line-height:1.1; margin-bottom: 3px; }
.meta { color:#d1c0a1; font-size:.85rem; margin-bottom: 4px; }
.genre { color:#f2b74a; font-size:.82rem; margin: 6px 0; }
.overview { color:#ddcfb8; font-size:.82rem; line-height:1.3; }
.badge { display:inline-block; padding:3px 8px; border-radius:999px; background:rgba(151,20,28,.75); color:#ffe6b0; font-size:.75rem; margin-top: 7px; }

.grid-card {
    background: linear-gradient(145deg, rgba(36,22,22,.98), rgba(10,7,7,.98));
    border: 1px solid rgba(247,211,126,.24);
    border-radius: 16px;
    padding: 9px;
    margin-bottom: 14px;
    box-shadow: inset 0 -6px 0 rgba(69,35,24,.42), 0 10px 24px rgba(0,0,0,.48);
    min-height: 100%;
}
.grid-title { font-size: .86rem; font-weight: 900; color:#fff2c7; line-height:1.12; margin-top: 7px; }
.grid-meta { color:#d1c0a1; font-size:.74rem; line-height:1.2; margin-top: 3px; }
.grid-genre { color:#f2b74a; font-size:.72rem; line-height:1.2; margin-top: 4px; }
.view-note { color:#cdbd9f; font-size:.82rem; margin: .25rem 0 .75rem 0; }

.no-poster {
    aspect-ratio: 2 / 3;
    width: 100%;
    border-radius: 12px;
    background: #0b0808;
    border: 1px solid rgba(255,255,255,.12);
    display:flex;
    align-items:center;
    justify-content:center;
    text-align:center;
    color:#9e9078;
    font-weight:900;
}
img { border-radius: 12px; }
@media (max-width: 640px) {
    .block-container { padding-left: .65rem; padding-right: .65rem; }
    .movie-card { padding: 9px; margin-bottom: 12px; border-radius: 14px; }
    .movie-title { font-size: .96rem; }
    .overview { display: none; }
}
</style>
""",
    unsafe_allow_html=True,
)

st.markdown('<div class="crypt-title">Movie Crypt</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">A dark retro video-store shelf for browsing your movie collection on iPhone.</div>', unsafe_allow_html=True)

with st.sidebar:
    st.header("Filter the shelves")
    search = st.text_input("Search", placeholder="Title, genre, notes...")

    watched_values = sorted([x for x in df.get("Watched?", pd.Series(dtype=str)).astype(str).unique() if x])
    watched = st.selectbox("Watched status", ["All"] + watched_values)

    genre_values = sorted({g.strip() for cell in df.get("Genre", pd.Series(dtype=str)).astype(str) for g in cell.split(",") if g.strip()})
    selected_genres = st.multiselect("Genres", genre_values, help="Choose one or more genres to narrow the shelf.")
    genre_match_mode = st.radio("Genre match", ["Any selected", "All selected"], horizontal=True)

    view_mode = st.radio("View", ["VHS Shelf", "Poster Grid"], horizontal=True)
    grid_columns = st.slider("Grid columns", min_value=2, max_value=5, value=3, help="Use 2–3 columns on iPhone for the best poster size.")

    format_values = sorted([x for x in df.get("Format", pd.Series(dtype=str)).astype(str).unique() if x])
    selected_format = st.selectbox("Format", ["All"] + format_values)

    sort_by = st.selectbox("Sort by", [c for c in ["Title", "Year", "TMDB Rating", "Runtime (min)"] if c in df.columns])
    ascending = st.toggle("Ascending", value=True)
    show_overviews = st.toggle("Show overviews", value=True)

filtered = df.copy()
if search:
    s = search.lower().strip()
    searchable_cols = [c for c in ["Title", "Original Entry", "Genre", "Notes", "Overview"] if c in filtered.columns]
    haystack = filtered[searchable_cols].astype(str).agg(" ".join, axis=1).str.lower()
    filtered = filtered[haystack.str.contains(s, regex=False, na=False)]

if watched != "All" and "Watched?" in filtered.columns:
    filtered = filtered[filtered["Watched?"].astype(str) == watched]

if selected_genres and "Genre" in filtered.columns:
    def genre_matches(cell):
        movie_genres = {g.strip() for g in str(cell).split(",") if g.strip()}
        selected = set(selected_genres)
        if genre_match_mode == "All selected":
            return selected.issubset(movie_genres)
        return bool(movie_genres & selected)
    filtered = filtered[filtered["Genre"].apply(genre_matches)]

if selected_format != "All" and "Format" in filtered.columns:
    filtered = filtered[filtered["Format"].astype(str) == selected_format]

if sort_by in filtered.columns:
    filtered = filtered.sort_values(sort_by, ascending=ascending, na_position="last")

m1, m2, m3, m4 = st.columns(4)
with m1:
    st.markdown(f'<div class="stat-card"><div class="stat-number">{len(filtered)}</div><div class="stat-label">Showing</div></div>', unsafe_allow_html=True)
with m2:
    st.markdown(f'<div class="stat-card"><div class="stat-number">{len(df)}</div><div class="stat-label">Total Movies</div></div>', unsafe_allow_html=True)
with m3:
    watched_count = int((df.get("Watched?", pd.Series(dtype=str)).astype(str).str.lower() == "watched").sum()) if "Watched?" in df else 0
    st.markdown(f'<div class="stat-card"><div class="stat-number">{watched_count}</div><div class="stat-label">Watched</div></div>', unsafe_allow_html=True)
with m4:
    avg = df["TMDB Rating"].dropna().mean() if "TMDB Rating" in df.columns else None
    avg_text = "—" if avg is None or pd.isna(avg) else f"{avg:.1f}"
    st.markdown(f'<div class="stat-card"><div class="stat-number">{avg_text}</div><div class="stat-label">Avg TMDB</div></div>', unsafe_allow_html=True)

st.write("")

# Native Streamlit image rendering is intentionally used here instead of raw HTML <img> tags.
# This avoids the escaped-code/terminal-looking display issue on phones and some Streamlit hosts.
def movie_fields(row):
    title = clean_text(row.get("Title", "Untitled"), "Untitled")
    year = row.get("Year", "")
    year_txt = "" if pd.isna(year) else str(int(year))
    runtime = row.get("Runtime (min)", "")
    runtime_txt = "" if pd.isna(runtime) else f" • {int(runtime)} min"
    rating = row.get("TMDB Rating", "")
    rating_txt = "" if pd.isna(rating) else f" • ⭐ {float(rating):.1f}"
    fmt = clean_text(row.get("Format", ""))
    watched_txt = clean_text(row.get("Watched?", ""), "Unwatched")
    genre = clean_text(row.get("Genre", ""))
    overview = clean_text(row.get("Overview", ""))
    source = clean_text(row.get("TMDB Source URL", ""))
    url = clean_text(row.get("Poster Display URL", ""))
    return title, year_txt, runtime_txt, rating_txt, fmt, watched_txt, genre, overview, source, url

st.markdown(f'<div class="view-note">Current view: <b>{view_mode}</b>. Use the sidebar to search, sort, and filter by one or more genres.</div>', unsafe_allow_html=True)

if view_mode == "Poster Grid":
    rows = list(filtered.iterrows())
    for start_idx in range(0, len(rows), grid_columns):
        cols = st.columns(grid_columns, gap="small")
        for col, (_, row) in zip(cols, rows[start_idx:start_idx + grid_columns]):
            title, year_txt, runtime_txt, rating_txt, fmt, watched_txt, genre, overview, source, url = movie_fields(row)
            with col:
                st.markdown('<div class="grid-card">', unsafe_allow_html=True)
                if url.startswith("http"):
                    st.image(url, use_container_width=True)
                else:
                    st.markdown('<div class="no-poster">NO POSTER<br>FOUND</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="grid-title">{title}</div>', unsafe_allow_html=True)
                meta = f"{year_txt}{rating_txt}"
                if meta:
                    st.markdown(f'<div class="grid-meta">{meta}</div>', unsafe_allow_html=True)
                if runtime_txt or fmt:
                    st.markdown(f'<div class="grid-meta">{runtime_txt.replace(" • ", "")} {fmt}</div>', unsafe_allow_html=True)
                if genre:
                    short_genre = genre[:42] + ("…" if len(genre) > 42 else "")
                    st.markdown(f'<div class="grid-genre">{short_genre}</div>', unsafe_allow_html=True)
                st.markdown(f'<span class="badge">{watched_txt}</span>', unsafe_allow_html=True)
                if source.startswith("http"):
                    st.link_button("TMDB", source, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
else:
    for _, row in filtered.iterrows():
        title, year_txt, runtime_txt, rating_txt, fmt, watched_txt, genre, overview, source, url = movie_fields(row)

        with st.container():
            st.markdown('<div class="movie-card">', unsafe_allow_html=True)
            img_col, info_col = st.columns([0.85, 1.35], vertical_alignment="top")
            with img_col:
                if url.startswith("http"):
                    st.image(url, use_container_width=True)
                else:
                    st.markdown('<div class="no-poster">NO POSTER<br>FOUND</div>', unsafe_allow_html=True)
            with info_col:
                st.markdown(f'<div class="movie-title">{title}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="meta">{year_txt}{runtime_txt}{rating_txt}</div>', unsafe_allow_html=True)
                if fmt:
                    st.markdown(f'<div class="meta">{fmt}</div>', unsafe_allow_html=True)
                if genre:
                    st.markdown(f'<div class="genre">{genre}</div>', unsafe_allow_html=True)
                if show_overviews and overview:
                    short = overview[:260] + ("…" if len(overview) > 260 else "")
                    st.markdown(f'<div class="overview">{short}</div>', unsafe_allow_html=True)
                st.markdown(f'<span class="badge">{watched_txt}</span>', unsafe_allow_html=True)
                if source.startswith("http"):
                    st.link_button("Open on TMDB", source)
            st.markdown('</div>', unsafe_allow_html=True)

st.caption("iPhone tip: run `streamlit run app.py --server.address 0.0.0.0`, then open the Network URL on your phone while connected to the same Wi‑Fi.")
