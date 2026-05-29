import html
from pathlib import Path
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Joey's Movie Crypt", page_icon="📼", layout="wide", initial_sidebar_state="collapsed")
DATA_PATH = Path(__file__).with_name("movie_library.csv")

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH, keep_default_na=False)
    for col in ["Title", "Genre", "Overview", "Cover URL", "Watched?", "Format", "Match Status", "TMDB Source URL"]:
        if col in df.columns:
            df[col] = df[col].astype(str).fillna("")
    for col in ["Year", "Runtime (min)"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")
    for col in ["TMDB Rating", "My Rating (1-5)"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df

df = load_data()

st.markdown('''
<style>
[data-testid="stAppViewContainer"] { background: radial-gradient(circle at 15% 10%, rgba(141,16,26,.32), transparent 30%), radial-gradient(circle at 85% 15%, rgba(241,182,74,.13), transparent 28%), linear-gradient(180deg, #080606 0%, #140b0d 45%, #060405 100%); color: #f5ead6; }
[data-testid="stSidebar"] { background: #12090b; }
.block-container { padding-top: 1.25rem; max-width: 1200px; }
.crypt-title { font-size: clamp(2rem, 8vw, 5rem); line-height: .9; letter-spacing: .04em; color: #f8d78d; text-shadow: 0 0 12px rgba(141,16,26,.9), 4px 4px #23080a; font-weight: 900; text-transform: uppercase; margin-bottom: .15rem; }
.subtitle { color:#c9b99a; font-size:1rem; margin-bottom: 1rem; }
.metric-card { background: linear-gradient(135deg, rgba(51,27,23,.9), rgba(16,10,10,.96)); border: 1px solid rgba(248,215,141,.28); border-radius: 16px; padding: 14px; box-shadow: 0 8px 24px rgba(0,0,0,.45); }
.metric-card .num { font-size: 1.65rem; color:#f8d78d; font-weight: 800; }
.metric-card .label { color:#c9b99a; font-size:.8rem; text-transform:uppercase; letter-spacing:.08em; }
.shelf { display:grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap:18px; padding: 16px; border-radius: 18px; background: linear-gradient(180deg, rgba(54,29,21,.72), rgba(12,7,6,.86)); border:1px solid rgba(248,215,141,.18); box-shadow: inset 0 -14px 0 rgba(73,38,25,.65), 0 10px 30px rgba(0,0,0,.45); }
.vhs-card { background: linear-gradient(145deg, #211717, #0d0909); border:1px solid rgba(248,215,141,.22); border-radius: 14px; padding: 10px; min-height: 100%; box-shadow: 0 10px 24px rgba(0,0,0,.55); position: relative; overflow:hidden; }
.vhs-card:before { content:""; position:absolute; inset:0; border-left: 9px solid rgba(141,16,26,.55); pointer-events:none; }
.poster-wrap { width:100%; aspect-ratio: 2/3; background:#0b0808; border-radius:10px; overflow:hidden; border:1px solid rgba(255,255,255,.12); }
.poster { width:100%; height:100%; object-fit:cover; display:block; }
.no-poster { height:100%; display:flex; align-items:center; justify-content:center; text-align:center; color:#9b8d77; font-weight:800; padding:12px; }
.movie-title { font-weight:900; color:#fff2c8; font-size:1rem; line-height:1.1; margin-top:10px; }
.meta { color:#d0bfa0; font-size:.82rem; margin-top:4px; }
.genre { color:#f1b64a; font-size:.78rem; margin-top:6px; }
.overview { color:#d7c8ad; font-size:.78rem; margin-top:8px; line-height:1.25; }
.badge { display:inline-block; padding: 3px 7px; border-radius:999px; background:rgba(141,16,26,.7); color:#ffe6b0; margin-top:7px; font-size:.72rem; }
a { color:#f1b64a!important; }
@media (max-width: 640px) { .block-container { padding-left:.75rem; padding-right:.75rem; } .shelf { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; padding: 10px; } .vhs-card { padding: 8px; border-radius: 12px; } .movie-title { font-size:.88rem; } .overview { display:none; } }
</style>
''', unsafe_allow_html=True)

st.markdown('<div class="crypt-title">Movie Crypt</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">A creepy retro video-store database for your movie collection. Optimized for iPhone scrolling.</div>', unsafe_allow_html=True)

with st.sidebar:
    st.header("Filter the shelves")
    search = st.text_input("Search title, notes, or overview", "")
    watched_options = ["All"] + sorted([x for x in df.get("Watched?", pd.Series(dtype=str)).unique() if x])
    watched = st.selectbox("Watched status", watched_options)
    all_genres = sorted({g.strip() for cell in df.get("Genre", pd.Series(dtype=str)).astype(str) for g in cell.split(",") if g.strip()})
    genres = st.multiselect("Genre", all_genres)
    formats = ["All"] + sorted([x for x in df.get("Format", pd.Series(dtype=str)).unique() if x])
    fmt = st.selectbox("Format", formats)
    sort_by = st.selectbox("Sort by", ["Title", "Year", "TMDB Rating", "Runtime (min)"])
    ascending = st.toggle("Ascending", value=True)
    show_overview = st.toggle("Show overviews", value=True)

filtered = df.copy()
if search:
    s = search.lower().strip()
    cols = [c for c in ["Title", "Original Entry", "Notes", "Overview"] if c in filtered.columns]
    hay = filtered[cols].astype(str).agg(" ".join, axis=1).str.lower()
    filtered = filtered[hay.str.contains(s, regex=False)]
if watched != "All" and "Watched?" in filtered.columns:
    filtered = filtered[filtered["Watched?"] == watched]
if genres and "Genre" in filtered.columns:
    filtered = filtered[filtered["Genre"].apply(lambda x: any(g in str(x) for g in genres))]
if fmt != "All" and "Format" in filtered.columns:
    filtered = filtered[filtered["Format"] == fmt]
if sort_by in filtered.columns:
    filtered = filtered.sort_values(sort_by, ascending=ascending, na_position="last")

c1, c2, c3, c4 = st.columns(4)
with c1: st.markdown(f'<div class="metric-card"><div class="num">{len(filtered)}</div><div class="label">Showing</div></div>', unsafe_allow_html=True)
with c2: st.markdown(f'<div class="metric-card"><div class="num">{len(df)}</div><div class="label">Total Movies</div></div>', unsafe_allow_html=True)
with c3:
    watched_count = int((df.get("Watched?", pd.Series(dtype=str)) == "Watched").sum()) if "Watched?" in df else 0
    st.markdown(f'<div class="metric-card"><div class="num">{watched_count}</div><div class="label">Watched</div></div>', unsafe_allow_html=True)
with c4:
    avg = df["TMDB Rating"].dropna().mean() if "TMDB Rating" in df else float("nan")
    avg_text = "—" if pd.isna(avg) else f"{avg:.1f}"
    st.markdown(f'<div class="metric-card"><div class="num">{avg_text}</div><div class="label">Avg TMDB</div></div>', unsafe_allow_html=True)

st.write("")
html_blocks = ['<div class="shelf">']
for _, row in filtered.iterrows():
    title = html.escape(str(row.get("Title", "Untitled")))
    year_val = row.get("Year", "")
    year = "" if pd.isna(year_val) or str(year_val) == "<NA>" else str(year_val)
    runtime = row.get("Runtime (min)", "")
    runtime_txt = "" if pd.isna(runtime) or runtime == "" else f" • {int(runtime)} min"
    rating = row.get("TMDB Rating", "")
    rating_txt = "" if pd.isna(rating) or rating == "" else f" • ⭐ {float(rating):.1f}"
    format_txt = html.escape(str(row.get("Format", "")))
    watched_txt = html.escape(str(row.get("Watched?", "")) or "Unwatched")
    genre = html.escape(str(row.get("Genre", "")))
    overview = html.escape(str(row.get("Overview", "")))
    cover = str(row.get("Cover URL", ""))
    source = str(row.get("TMDB Source URL", ""))
    poster_html = f'<img class="poster" src="{html.escape(cover)}" alt="{title} poster">' if cover.startswith("http") else '<div class="no-poster">NO POSTER<br>FOUND</div>'
    link = f'<a href="{html.escape(source)}" target="_blank">TMDB</a>' if source.startswith("http") else ""
    overview_html = f'<div class="overview">{overview[:210]}{"…" if len(overview)>210 else ""}</div>' if show_overview and overview else ""
    html_blocks.append(f'''
    <div class="vhs-card">
      <div class="poster-wrap">{poster_html}</div>
      <div class="movie-title">{title}</div>
      <div class="meta">{year}{runtime_txt}{rating_txt}</div>
      <div class="meta">{format_txt} {link}</div>
      <div class="genre">{genre}</div>
      {overview_html}
      <span class="badge">{watched_txt}</span>
    </div>
    ''')
html_blocks.append('</div>')
st.markdown("\n".join(html_blocks), unsafe_allow_html=True)
st.caption("Tip for iPhone: run `streamlit run app.py --server.address 0.0.0.0`, then open the shown Network URL on your phone while on the same Wi‑Fi.")
