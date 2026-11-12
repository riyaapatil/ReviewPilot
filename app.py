# app.py
import streamlit as st
import tempfile
import os
import time
from html import escape

from extractor import extract_text_from_pdf
from analyzer import analyze_paper
from grouper import group_papers
from generator import generate_section

st.set_page_config(
    page_title="ReviewPilot",
    page_icon="📚",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Design tokens
#   ink      #14213D  deep navy (text, hero)
#   teal     #0F766E  primary accent
#   mint     #E6F4F1  soft teal surface
#   gold     #C98A1B  highlight accent
#   ink      #14213D  page background
#   line     #DCE3EC  borders
# ---------------------------------------------------------------------------
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Source+Serif+4:wght@500;600;700&display=swap');

:root {
    --ink: #14213D;
    --muted: #5B6B82;
    --teal: #0F766E;
    --teal-dark: #0B5A54;
    --mint: #E6F4F1;
    --gold: #C98A1B;
    --paper: #F6F8FB;
    --card: #FFFFFF;
    --line: #DCE3EC;
    --good-bg: #E8F5EE;
    --good-ink: #1E6B45;
    --bad-bg: #FBEDEC;
    --bad-ink: #9B2C2C;
}

html, body, [class*="css"], .stApp {
    font-family: 'Inter', sans-serif;
    color: #E8EEF7;
}
.stApp { background: var(--ink); }
.block-container { padding-top: 2rem; padding-bottom: 4rem; max-width: 1200px; }
header[data-testid="stHeader"] { background: transparent; }
[data-testid="stCaptionContainer"], .stCaption { color: #A9B9D0 !important; }

h1, h2, h3, h4 {
    font-family: 'Source Serif 4', serif !important;
    color: var(--ink) !important;
    letter-spacing: -0.01em;
}

/* Hero */
.hero {
    background: linear-gradient(135deg, #1F3D68 0%, #15605F 100%);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 18px;
    padding: 2.4rem 2.6rem;
    margin-bottom: 1.6rem;
    box-shadow: 0 14px 36px rgba(0, 0, 0, 0.35);
}
.hero h1 {
    color: #FFFFFF !important;
    font-size: 2.4rem;
    margin: 0 0 0.4rem 0;
    padding: 0;
}
.hero p {
    color: #C9D6E8;
    font-size: 1.05rem;
    margin: 0;
    max-width: 640px;
    line-height: 1.55;
}
.hero .pill {
    display: inline-block;
    background: rgba(201, 138, 27, 0.18);
    color: #F2C46B;
    border: 1px solid rgba(242, 196, 107, 0.4);
    border-radius: 999px;
    padding: 0.2rem 0.8rem;
    font-size: 0.8rem;
    font-weight: 500;
    margin-bottom: 0.9rem;
}

/* Section headings */
.section-title {
    font-family: 'Source Serif 4', serif;
    font-size: 1.5rem;
    font-weight: 600;
    color: #FFFFFF;
    margin: 2rem 0 0.2rem 0;
    padding-left: 0.8rem;
    border-left: 4px solid var(--gold);
}
.section-sub { color: #A9B9D0; margin: 0 0 1rem 0.95rem; font-size: 0.95rem; }

/* Upload area */
[data-testid="stFileUploader"] section {
    background: var(--card);
    border: 2px dashed #9DB8B4;
    border-radius: 14px;
    padding: 1.4rem;
}
[data-testid="stFileUploader"] section, [data-testid="stFileUploader"] section * { color: var(--ink) !important; }
[data-testid="stFileUploader"] section small { color: var(--muted) !important; }
[data-testid="stFileUploader"] section:hover { border-color: var(--teal); background: var(--mint); }

/* Buttons */
.stButton > button, .stDownloadButton > button {
    background: var(--teal);
    color: #FFFFFF;
    border: none;
    border-radius: 10px;
    padding: 0.65rem 1.6rem;
    font-weight: 600;
    font-size: 1rem;
    transition: background 0.15s ease, box-shadow 0.15s ease;
}
.stButton > button:hover, .stDownloadButton > button:hover {
    background: var(--teal-dark);
    color: #FFFFFF;
    box-shadow: 0 6px 16px rgba(15, 118, 110, 0.28);
}
.stButton > button:focus-visible, .stDownloadButton > button:focus-visible {
    outline: 3px solid var(--gold);
    outline-offset: 2px;
}

/* Progress */
.stProgress > div > div > div > div { background-color: var(--teal); }

/* Paper card */
.paper-head {
    display: flex; align-items: baseline; gap: 0.8rem; flex-wrap: wrap;
    margin-bottom: 0.9rem;
}
.paper-badge {
    background: var(--ink); color: #fff; border-radius: 8px;
    padding: 0.15rem 0.6rem; font-size: 0.8rem; font-weight: 600;
}
.paper-title {
    font-family: 'Source Serif 4', serif;
    font-size: 1.3rem; font-weight: 600; color: var(--ink); line-height: 1.3;
}
.meta-grid {
    display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 0.8rem; margin-bottom: 1.1rem;
}
.meta-item {
    background: var(--mint); border-radius: 12px; padding: 0.75rem 0.95rem;
}
.meta-label { font-size: 0.78rem; font-weight: 600; color: var(--teal-dark); margin-bottom: 0.2rem; }
.meta-value { font-size: 0.95rem; color: var(--ink); line-height: 1.4; }

.block {
    background: var(--card); border: 1px solid var(--line);
    border-radius: 12px; padding: 0.95rem 1.1rem; margin-bottom: 0.8rem;
    height: 100%;
}
.block-label { font-size: 0.82rem; font-weight: 600; color: var(--gold); margin-bottom: 0.3rem; }
.block-text { font-size: 0.95rem; line-height: 1.6; color: var(--ink); }

.pro {
    background: var(--good-bg); border-left: 4px solid var(--good-ink);
    border-radius: 10px; padding: 0.95rem 1.1rem; height: 100%;
}
.pro .block-label { color: var(--good-ink); }
.con {
    background: var(--bad-bg); border-left: 4px solid var(--bad-ink);
    border-radius: 10px; padding: 0.95rem 1.1rem; height: 100%;
}
.con .block-label { color: var(--bad-ink); }

/* Expanders */
[data-testid="stExpander"] {
    background: var(--card);
    border: 1px solid var(--line);
    border-radius: 14px;
    box-shadow: 0 2px 10px rgba(20, 33, 61, 0.05);
    margin-bottom: 1rem;
}
[data-testid="stExpander"] summary { font-weight: 600; color: var(--ink); }

/* Tabs */
.stTabs [data-baseweb="tab-list"] { gap: 6px; border-bottom: 1px solid rgba(255, 255, 255, 0.18); }
.stTabs [data-baseweb="tab"] {
    background: transparent; border-radius: 10px 10px 0 0;
    padding: 0.6rem 1.1rem; font-weight: 500; color: #A9B9D0;
}
.stTabs [aria-selected="true"] { background: var(--mint); color: var(--teal-dark); font-weight: 600; }
.stTabs [data-baseweb="tab-highlight"] { background-color: var(--gold); }

.review-body {
    background: var(--card); border: 1px solid var(--line); border-radius: 14px;
    padding: 1.6rem 1.9rem; font-family: 'Source Serif 4', serif;
    font-size: 1.05rem; line-height: 1.8; color: var(--ink); margin-top: 0.8rem;
}
.ref-list {
    margin-top: 0.9rem; padding: 0.9rem 1.2rem; background: var(--mint);
    border-radius: 12px; font-size: 0.88rem; color: var(--ink); line-height: 1.6;
}
.ref-list strong { color: var(--teal-dark); }

</style>
""",
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def esc(value, fallback="Not reported"):
    """Escape model output for safe HTML display."""
    if value is None or str(value).strip() == "":
        return escape(fallback)
    return escape(str(value)).replace("\n", "<br>")


def section_title(title, subtitle=""):
    st.markdown(f'<div class="section-title">{escape(title)}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="section-sub">{escape(subtitle)}</div>', unsafe_allow_html=True)


def text_block(label, value):
    return (
        f'<div class="block"><div class="block-label">{escape(label)}</div>'
        f'<div class="block-text">{esc(value)}</div></div>'
    )


# ---------------------------------------------------------------------------
# Hero
# ---------------------------------------------------------------------------
st.markdown(
    """
<div class="hero">
    <span class="pill">Literature review assistant</span>
    <h1>ReviewPilot</h1>
    <p>Upload research papers to extract key details, compare findings, and get a literature review draft organised by theme.</p>
</div>
""",
    unsafe_allow_html=True,
)

section_title("Upload papers", "Two to five PDFs from the same field work best.")

uploaded_files = st.file_uploader(
    "Upload research PDFs",
    type="pdf",
    accept_multiple_files=True,
    label_visibility="collapsed",
)

if uploaded_files:
    st.caption(f"{len(uploaded_files)} file(s) selected")

if uploaded_files and st.button("🚀 Analyze & generate review"):
    papers = []
    progress = st.progress(0)
    status = st.empty()

    # --- STEP 1: Extraction ---
    for i, file in enumerate(uploaded_files):
        status.info(f"Reading and analyzing: {file.name} ...")
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(file.read())
            tmp_path = tmp.name

        try:
            text = extract_text_from_pdf(tmp_path)

            if len(text.strip()) < 100:
                raise ValueError("Extracted text is too short. The PDF might be a scanned image.")

            paper = analyze_paper(text)
            papers.append(paper)

        except Exception as e:
            st.error(f"❌ Failed on {file.name}: {str(e)}")
        finally:
            os.unlink(tmp_path)

        progress.progress((i + 1) / (len(uploaded_files) + 2))

        if i < len(uploaded_files) - 1:
            time.sleep(3)

    if not papers:
        st.error("No papers were successfully analyzed. Please check the errors above.")
        st.stop()

    st.success(f"Successfully analyzed {len(papers)} out of {len(uploaded_files)} papers.")

    # --- DISPLAY EXTRACTED INFO ---
    section_title("Paper analysis", "A structured breakdown of each uploaded paper.")

    for idx, p in enumerate(papers):
        with st.expander(f"Paper {idx + 1}: {p.title}", expanded=True):
            st.markdown(
                f"""
<div class="paper-head">
    <span class="paper-badge">Paper {idx + 1}</span>
    <span class="paper-title">{esc(p.title)}</span>
</div>
<div class="meta-grid">
    <div class="meta-item"><div class="meta-label">Authors</div><div class="meta-value">{esc(p.authors)}</div></div>
    <div class="meta-item"><div class="meta-label">Year</div><div class="meta-value">{esc(p.publication_year)}</div></div>
    <div class="meta-item"><div class="meta-label">Venue</div><div class="meta-value">{esc(p.publication_venue)}</div></div>
    <div class="meta-item"><div class="meta-label">Technologies used</div><div class="meta-value">{esc(p.technologies_used)}</div></div>
</div>
""",
                unsafe_allow_html=True,
            )

            colA, colB = st.columns(2, gap="medium")
            with colA:
                st.markdown(
                    text_block("Objective", p.objective)
                    + text_block("Methodology", p.methodology)
                    + text_block("Dataset", p.dataset),
                    unsafe_allow_html=True,
                )
            with colB:
                st.markdown(text_block("Key findings", p.key_findings), unsafe_allow_html=True)

            colX, colY = st.columns(2, gap="medium")
            with colX:
                st.markdown(
                    f'<div class="pro"><div class="block-label">Advantages</div>'
                    f'<div class="block-text">{esc(p.advantages, "Not explicitly reported")}</div></div>',
                    unsafe_allow_html=True,
                )
            with colY:
                st.markdown(
                    f'<div class="con"><div class="block-label">Limitations</div>'
                    f'<div class="block-text">{esc(p.limitations, "Not explicitly reported")}</div></div>',
                    unsafe_allow_html=True,
                )

    # --- STEP 2: Grouping ---
    status.info("Grouping papers into themes...")
    progress.progress((len(uploaded_files) + 1) / (len(uploaded_files) + 2))

    time.sleep(2)

    try:
        groups = group_papers(papers)
    except Exception as e:
        st.error(f"Grouping failed: {e}")
        st.stop()

    # --- STEP 3: Generating Review ---
    status.info("Generating literature review...")
    progress.progress(1.0)

    section_title("Literature review draft", "One section per theme. Review and edit before using.")

    review_tabs = st.tabs(list(groups.keys()))
    full_review = ""

    for idx, (theme, indices) in enumerate(groups.items()):
        theme_papers = [papers[i] for i in indices if i < len(papers)]
        if not theme_papers:
            continue

        time.sleep(2)

        section = generate_section(theme, theme_papers)

        with review_tabs[idx]:
            st.markdown(
                f'<div class="review-body">{escape(str(section)).replace(chr(10), "<br>")}</div>',
                unsafe_allow_html=True,
            )
            refs = "".join(
                f"<div>• {esc(p.authors)} ({esc(p.publication_year, 'Year not reported')}). {esc(p.title)}.</div>"
                for p in theme_papers
            )
            st.markdown(
                f'<div class="ref-list"><strong>References used in this section</strong>{refs}</div>',
                unsafe_allow_html=True,
            )

        full_review += f"## {theme}\n{section}\n\n"

    status.success("Complete! Your draft is ready.")

    st.download_button(
        label="📥 Download full draft (.txt)",
        data=full_review,
        file_name="review_draft.txt",
        mime="text/plain",
    )