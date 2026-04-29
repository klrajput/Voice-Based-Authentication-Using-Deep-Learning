# ============================================================
#  streamlit_app.py  —  Voice-Based Secure File Locker v2.1
#  ONLY file changed. All other project files unchanged.
# ============================================================
import os
import json
import base64
import shutil
import datetime
import uuid
import hashlib
import streamlit as st

from audio.preprocess        import preprocess_audio
from features.extract_features import extract_features
from learning.continual_learning import save_multiple_embeddings
from model.profile_manager   import load_profile, reset_profile
from model.verify_voice      import verify_voice
from security.antispoof      import detect_spoof
from security.encryption     import encrypt_file, decrypt_file

# SAFE NAVIGATION
def navigate(page_name):
    st.session_state["__nav_target"] = page_name
    st.rerun()

# ── SAFE NAVIGATION HELPER ─────────────────────────


# ── PATHS ────────────────────────────────────────────────────
USER_DATA   = "data/profile/single_user.json"
LOCK_FOLDER = "data/locked_file"
LOG_FILE    = "data/profile/activity_log.json"


# ════════════════════════════════════════════════════════════
#  STYLES  — forces dark theme even in Streamlit light mode
# ════════════════════════════════════════════════════════════
def apply_styles():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@400;500;600;700&family=Share+Tech+Mono&display=swap');

    /* ── CSS VARS ── */
    :root {
        --c: #00f5ff; --b: #0066ff; --p: #7b2fff;
        --pk: #ff2d78; --g: #00ff88; --am: #ffaa00;
        --d0: #010814; --d1: #050e1f; --d2: #0a1628;
        --br: rgba(0,245,255,0.17); --t: #cce8ff; --m: #4a7fa5;
        --fh: 'Orbitron', monospace;
        --fb: 'Rajdhani', sans-serif;
        --fm: 'Share Tech Mono', monospace;
    }

    /* ── FORCE DARK everywhere (light-mode safe) ── */
    html, body,
    .stApp,
    [data-testid="stAppViewContainer"],
    [data-testid="stAppViewBlockContainer"],
    section[data-testid="stMain"],
    .main,
    [data-testid="stHeader"],
    [data-testid="stToolbar"],
    [data-testid="stDecoration"],
    [data-testid="collapsedControl"],
    div[class*="appview"],
    div[class*="main"] {
        background: #010814 !important;
        background-color: #010814 !important;
        color: #cce8ff !important;
    }

    /* Top header bar */
    [data-testid="stHeader"] {
        background: linear-gradient(90deg,#010814,#050e1f) !important;
        border-bottom: 1px solid rgba(0,245,255,0.10) !important;
    }
    /* Three-dot menu & toolbar icons */
    [data-testid="stToolbar"] *,
    [data-testid="stHeader"] button,
    [data-testid="stHeader"] svg {
        color: #4a7fa5 !important;
        fill: #4a7fa5 !important;
        stroke: #4a7fa5 !important;
    }

    /* ── ANIMATED BACKGROUND ── */
    [data-testid="stAppViewContainer"]::before {
        content:''; position:fixed; inset:0;
        background:
            radial-gradient(ellipse 80% 55% at 20% 10%,rgba(0,102,255,0.12) 0%,transparent 60%),
            radial-gradient(ellipse 60% 50% at 80% 80%,rgba(123,47,255,0.12) 0%,transparent 60%);
        pointer-events:none; z-index:0;
    }
    [data-testid="stAppViewContainer"]::after {
        content:''; position:fixed; inset:0;
        background-image:
            linear-gradient(rgba(0,245,255,0.022) 1px,transparent 1px),
            linear-gradient(90deg,rgba(0,245,255,0.022) 1px,transparent 1px);
        background-size:56px 56px;
        animation:gridScroll 20s linear infinite;
        pointer-events:none; z-index:0;
    }
    @keyframes gridScroll { to { background-position:0 56px; } }

    /* ── SIDEBAR ── */
    [data-testid="stSidebar"],
    [data-testid="stSidebar"] > div,
    [data-testid="stSidebar"] > div > div,
    [data-testid="stSidebar"] section {
        background: #010e1f !important;
        background-color: #010e1f !important;
    }
    [data-testid="stSidebar"] {
        border-right: 1px solid rgba(0,245,255,0.14) !important;
    }
    /* Sidebar scan line */
    [data-testid="stSidebar"] > div::before {
        content:''; position:absolute; top:0; left:0; right:0; height:2px;
        background:linear-gradient(90deg,transparent,#00f5ff,#7b2fff,transparent);
        animation:scanLine 3s ease-in-out infinite; z-index:10;
    }
    @keyframes scanLine { 0%,100%{opacity:.35} 50%{opacity:1} }

    /* Radio label "Go to" */
    [data-testid="stSidebar"] .stRadio > label {
        font-family: var(--fh) !important;
        font-size: 0.55rem !important;
        letter-spacing: 2.5px !important;
        color: var(--m) !important;
        text-transform: uppercase !important;
    }
    /* Radio option labels */
    [data-testid="stSidebar"] .stRadio [role="radiogroup"] > label {
        font-family: var(--fb) !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        color: #8aaccc !important;
        padding: 7px 10px !important;
        border-radius: 8px !important;
        transition: all 0.2s !important;
        letter-spacing: 0.3px !important;
        display: flex !important;
        align-items: center !important;
    }
    [data-testid="stSidebar"] .stRadio [role="radiogroup"] > label:hover {
        color: var(--c) !important;
        background: rgba(0,245,255,0.06) !important;
    }
    /* Radio circle */
    [data-testid="stSidebar"] .stRadio [role="radio"] {
        border-color: var(--m) !important;
        background: transparent !important;
    }
    [data-testid="stSidebar"] .stRadio [aria-checked="true"] {
        border-color: var(--c) !important;
        background: rgba(0,245,255,0.15) !important;
    }

    /* ── MAIN BLOCK ── */
    .main .block-container,
    section[data-testid="stMain"] .block-container {
        padding: 1.5rem 2rem 4rem !important;
        max-width: 1000px !important;
        position: relative; z-index: 1;
    }

    /* ── HEADINGS ── */
    h1 {
        font-family: var(--fh) !important;
        font-size: clamp(1.05rem,3vw,1.7rem) !important;
        font-weight: 900 !important;
        letter-spacing: 1.5px !important;
        background: linear-gradient(135deg,#00f5ff 0%,#fff 50%,#7b2fff 100%) !important;
        -webkit-background-clip: text !important;
        -webkit-text-fill-color: transparent !important;
        background-clip: text !important;
        filter: drop-shadow(0 0 10px rgba(0,245,255,0.4)) !important;
        margin-bottom: 2px !important;
    }
    h2, h3 {
        font-family: var(--fh) !important;
        color: var(--c) !important;
        -webkit-text-fill-color: var(--c) !important;
        letter-spacing: 1px !important;
    }

    /* ── CARD ── */
    .sv-card {
        background: rgba(0,245,255,0.04);
        border: 1px solid var(--br); border-radius: 16px;
        padding: 24px 26px; margin-bottom: 18px;
        position: relative; overflow: hidden;
        box-shadow: 0 8px 32px rgba(0,0,0,0.45), inset 0 1px 0 rgba(255,255,255,0.06);
    }
    .sv-card::before {
        content:''; position:absolute; top:0; left:10%; right:10%; height:1px;
        background:linear-gradient(90deg,transparent,rgba(0,245,255,0.5),transparent);
    }
    .sv-card::after {
        content:''; position:absolute; top:0; left:-100%; width:50%; height:100%;
        background:linear-gradient(90deg,transparent,rgba(0,245,255,0.05),transparent);
        animation:cardSheen 7s ease-in-out infinite;
    }
    @keyframes cardSheen {
        0%{left:-100%;opacity:0} 40%{opacity:1}
        65%{left:160%;opacity:0} 100%{left:160%;opacity:0}
    }
    .sv-card-head {
        font-family: var(--fh); font-size:.62rem; font-weight:700;
        letter-spacing:2.5px; text-transform:uppercase;
        color:var(--c); margin-bottom:14px;
        display:flex; align-items:center; gap:10px;
    }
    .sv-card-head::after {
        content:''; flex:1; height:1px;
        background:linear-gradient(90deg,var(--br),transparent);
    }

    /* ── PROFILE HEADER ── */
    .prof-hdr {
        display:flex; align-items:center; gap:16px;
        padding:16px 20px;
        background:rgba(0,245,255,0.04);
        border:1px solid var(--br); border-radius:14px;
        margin-bottom:16px;
    }
    .prof-name {
        font-family:var(--fh); font-size:.9rem; font-weight:700;
        color:#cce8ff; letter-spacing:1px;
    }
    .prof-role {
        font-family:var(--fm); font-size:.5rem; color:var(--m);
        letter-spacing:1.5px; margin-top:4px;
    }

    /* ── AVATAR ── */
    .sv-avatar {
        width:70px; height:70px; border-radius:50%;
        background:linear-gradient(135deg,rgba(0,102,255,0.3),rgba(123,47,255,0.4));
        border:2px solid rgba(0,245,255,0.4);
        display:flex; align-items:center; justify-content:center;
        font-family:var(--fh); font-size:1.1rem; font-weight:700; color:var(--c);
        box-shadow:0 0 20px rgba(0,245,255,0.25); flex-shrink:0; overflow:hidden;
    }
    .sv-avatar img { width:100%; height:100%; object-fit:cover; border-radius:50%; }

    /* ── BADGES ── */
    .sv-badge {
        display:inline-flex; align-items:center; gap:7px;
        background:rgba(0,245,255,0.07);
        border:1px solid rgba(0,245,255,0.22); border-radius:40px;
        padding:5px 14px; font-family:var(--fm);
        font-size:.58rem; color:var(--c); letter-spacing:.8px;
    }
    .sv-badge-g { background:rgba(0,255,136,0.07); border-color:rgba(0,255,136,0.22); color:var(--g); }
    .sv-badge-am{ background:rgba(255,170,0,0.07); border-color:rgba(255,170,0,0.22); color:var(--am); }
    .sv-dot {
        width:7px; height:7px; border-radius:50%;
        background:var(--c); box-shadow:0 0 6px var(--c);
        animation:dotP 1.5s ease-in-out infinite; flex-shrink:0;
    }
    .sv-dot-g { background:var(--g); box-shadow:0 0 6px var(--g); }
    @keyframes dotP { 0%,100%{transform:scale(1)} 50%{transform:scale(1.5);opacity:.6} }

    /* ── STAT GRID ── */
    .sv-sg { display:grid; grid-template-columns:repeat(3,1fr); gap:10px; margin:12px 0; }
    .sv-sg2 { display:grid; grid-template-columns:repeat(2,1fr); gap:10px; margin:12px 0; }
    .sv-stat {
        background:rgba(0,245,255,0.05); border:1px solid rgba(0,245,255,0.1);
        border-radius:10px; padding:12px; text-align:center;
    }
    .sv-stat-l { font-family:var(--fh); font-size:.4rem; letter-spacing:2px; text-transform:uppercase; color:var(--m); margin-bottom:6px; }
    .sv-stat-i { font-size:1.3rem; display:block; margin-bottom:3px; }
    .sv-stat-v { font-family:var(--fb); font-size:.88rem; color:var(--c); font-weight:600; }

    /* ── SECURITY RING ── */
    .sv-rw { display:flex; align-items:center; justify-content:center; width:100px; height:100px; margin:0 auto 16px; position:relative; }
    .sv-ro {
        position:absolute; inset:0; border-radius:50%;
        border:2px solid transparent;
        background:linear-gradient(#050e1f,#050e1f) padding-box,
                    linear-gradient(135deg,#00f5ff,#7b2fff) border-box;
        animation:rRot 4s linear infinite;
    }
    .sv-ri { position:absolute; inset:10px; border-radius:50%; border:1px solid rgba(0,245,255,0.2); animation:rRot 3s linear infinite reverse; }
    .sv-ric { font-size:2.6rem; z-index:1; filter:drop-shadow(0 0 12px rgba(0,245,255,0.7)); }
    @keyframes rRot { to { transform:rotate(360deg); } }

    /* ── WAVEFORM ── */
    .sv-wv {
        display:flex; align-items:center; justify-content:center;
        gap:3px; height:48px;
        background:rgba(0,245,255,0.03);
        border:1px solid rgba(0,245,255,0.08);
        border-radius:10px; padding:0 12px; margin:10px 0;
    }
    .sv-wb {
        width:4px; border-radius:3px;
        background:linear-gradient(180deg,#00f5ff,#7b2fff);
        box-shadow:0 0 6px rgba(0,245,255,0.4);
        animation:wvA 1.2s ease-in-out infinite;
    }
    .sv-wb:nth-child(1){animation-delay:.00s} .sv-wb:nth-child(2){animation-delay:.09s}
    .sv-wb:nth-child(3){animation-delay:.18s} .sv-wb:nth-child(4){animation-delay:.27s}
    .sv-wb:nth-child(5){animation-delay:.18s} .sv-wb:nth-child(6){animation-delay:.09s}
    .sv-wb:nth-child(7){animation-delay:.00s} .sv-wb:nth-child(8){animation-delay:.12s}
    .sv-wb:nth-child(9){animation-delay:.21s} .sv-wb:nth-child(10){animation-delay:.12s}
    .sv-wb:nth-child(11){animation-delay:.03s} .sv-wb:nth-child(12){animation-delay:.15s}
    @keyframes wvA { 0%,100%{height:5px;opacity:.3} 50%{height:40px;opacity:1} }

    /* ── ACTIVITY FEED ── */
    .sv-fi {
        display:flex; align-items:center; gap:12px;
        padding:9px 12px;
        background:rgba(0,20,50,0.4);
        border:1px solid rgba(0,245,255,0.08);
        border-radius:9px; margin-bottom:7px;
    }
    .sv-fi-ico { font-size:1rem; flex-shrink:0; }
    .sv-fi-txt { font-family:var(--fb); font-size:.85rem; color:#cce8ff; flex:1; }
    .sv-fi-t   { font-family:var(--fm); font-size:.5rem; color:var(--m); white-space:nowrap; }

    /* ── STEP BLOCK ── */
    .sv-sb {
        background:rgba(0,245,255,0.03);
        border:1px solid rgba(0,245,255,0.1);
        border-radius:10px; padding:14px 16px; margin-bottom:12px;
    }
    .sv-sl {
        font-family:var(--fh); font-size:.46rem;
        letter-spacing:2px; text-transform:uppercase;
        color:var(--m); margin-bottom:8px;
    }

    /* ── STEPS TRACKER ── */
    .sv-steps { display:flex; align-items:center; margin:10px 0 16px; overflow-x:auto; }
    .sv-step-item { display:flex; flex-direction:column; align-items:center; gap:5px; min-width:58px; }
    .sv-step-c {
        width:30px; height:30px; border-radius:50%;
        border:1.5px solid rgba(0,245,255,0.18);
        display:flex; align-items:center; justify-content:center;
        font-family:var(--fh); font-size:.52rem; font-weight:700;
        color:var(--m); background:#0a1628; transition:all .4s;
    }
    .sv-step-c.a { border-color:var(--c); color:var(--c); background:rgba(0,245,255,0.1); box-shadow:0 0 14px rgba(0,245,255,0.3); animation:stepP 2s ease-in-out infinite; }
    .sv-step-c.d { border-color:var(--p); background:rgba(123,47,255,0.2); color:var(--p); }
    @keyframes stepP { 0%,100%{box-shadow:0 0 8px rgba(0,245,255,0.3)} 50%{box-shadow:0 0 22px rgba(0,245,255,0.7)} }
    .sv-step-lbl { font-family:var(--fb); font-size:.52rem; color:var(--m); text-align:center; white-space:nowrap; }
    .sv-step-line { flex:1; height:1px; background:var(--br); min-width:14px; align-self:flex-start; margin-top:15px; }

    /* ── SCORE ROW ── */
    .sv-sr { display:flex; align-items:center; gap:10px; margin:8px 0; }
    .sv-sv { font-family:var(--fm); font-size:.78rem; color:var(--c); min-width:52px; }
    .sv-pb-w { flex:1; background:rgba(0,20,50,0.6); border-radius:4px; height:6px; overflow:hidden; }
    .sv-pb { height:100%; border-radius:4px; background:linear-gradient(90deg,#00f5ff,#7b2fff); box-shadow:0 0 10px rgba(0,245,255,0.45); }

    /* ── DANGER ZONE ── */
    .sv-danger-box {
        background:rgba(255,45,120,0.07);
        border:1px solid rgba(255,45,120,0.25);
        border-radius:11px; padding:14px; margin-bottom:14px; text-align:center;
    }
    .sv-danger-title { font-family:var(--fh); font-size:.68rem; color:#ff2d78; letter-spacing:2px; margin-bottom:6px; }
    .sv-danger-body  { font-family:var(--fb); font-size:.88rem; color:#ff9999; line-height:1.5; }

    /* ── BUTTONS ── */
    .stButton > button {
        font-family: var(--fh) !important;
        font-size: .68rem !important; font-weight: 700 !important;
        letter-spacing: 2px !important; text-transform: uppercase !important;
        background: linear-gradient(135deg,rgba(0,102,255,.22),rgba(123,47,255,.22)) !important;
        color: #00f5ff !important;
        border: 1px solid #00f5ff !important;
        border-radius: 9px !important; padding: .6rem 1.5rem !important;
        transition: all .3s cubic-bezier(.23,1,.32,1) !important;
        box-shadow: 0 0 14px rgba(0,245,255,.14) !important;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg,rgba(0,245,255,.18),rgba(123,47,255,.28)) !important;
        box-shadow: 0 0 28px rgba(0,245,255,.38),0 6px 18px rgba(0,0,0,.4) !important;
        transform: translateY(-2px) !important;
        color: #fff !important;
    }
    .stButton > button:active { transform: translateY(0) !important; }

    /* Danger button wrapper */
    .sv-dbtn .stButton > button {
        background: rgba(255,45,120,.08) !important;
        border-color: #ff2d78 !important; color: #ff2d78 !important;
    }
    .sv-dbtn .stButton > button:hover { box-shadow:0 0 28px rgba(255,45,120,.35) !important; color:#fff !important; }

    /* ── TEXT INPUTS ── */
    .stTextInput > div > div > input {
        background: rgba(0,20,50,.7) !important;
        border: 1px solid rgba(0,245,255,.2) !important;
        border-radius: 9px !important; color: #cce8ff !important;
        font-family: var(--fb) !important; font-size: 1rem !important;
        padding: .6rem 1rem !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #00f5ff !important;
        box-shadow: 0 0 0 2px rgba(0,245,255,.12) !important;
        outline: none !important;
    }
    .stTextInput > div > div > input::placeholder { color: #4a7fa5 !important; }
    .stTextInput label {
        font-family: var(--fh) !important; font-size: .58rem !important;
        letter-spacing: 2px !important; text-transform: uppercase !important;
        color: #4a7fa5 !important;
    }

    /* ── FILE UPLOADER ── */
    [data-testid="stFileUploader"] {
        background: rgba(0,20,50,.45) !important;
        border: 2px dashed rgba(0,245,255,.22) !important;
        border-radius: 12px !important;
    }
    [data-testid="stFileUploader"] * { color: #4a7fa5 !important; }
    [data-testid="stFileUploader"] section { background: transparent !important; }

    /* ── PROGRESS BAR ── */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg,#00f5ff,#7b2fff) !important;
        box-shadow: 0 0 12px rgba(0,245,255,.5) !important;
    }
    .stProgress > div > div { background: rgba(0,20,50,.6) !important; }

    /* ── ALERTS ── */
    [data-testid="stAlert"] {
        border-radius: 11px !important;
        font-family: var(--fb) !important;
        font-size: .95rem !important;
    }

    /* ── DOWNLOAD BUTTON ── */
    .stDownloadButton > button {
        background: linear-gradient(135deg,rgba(0,245,255,.1),rgba(0,102,255,.15)) !important;
        border: 1px solid rgba(0,245,255,.35) !important; color: #00f5ff !important;
        font-family: var(--fh) !important; font-size: .62rem !important;
        border-radius: 8px !important;
    }

    /* ── EXPANDER ── */
    details summary {
        font-family: var(--fh) !important; font-size:.62rem !important;
        letter-spacing:2px !important; text-transform:uppercase !important;
        color: #00f5ff !important; background: rgba(0,245,255,.04) !important;
        border: 1px solid rgba(0,245,255,.15) !important;
        border-radius: 9px !important; padding:10px 14px !important;
    }
    details[open] summary { border-radius:9px 9px 0 0 !important; }
    details > div {
        background: rgba(0,10,30,.7) !important;
        border: 1px solid rgba(0,245,255,.1) !important;
        border-top: none !important; border-radius:0 0 9px 9px !important;
        padding:14px !important;
    }

    /* ── SCROLLBAR ── */
    ::-webkit-scrollbar { width:5px; height:5px; }
    ::-webkit-scrollbar-track { background:#050e1f; }
    ::-webkit-scrollbar-thumb { background:linear-gradient(180deg,#00f5ff,#7b2fff); border-radius:3px; }

    /* ── MOBILE ── */
    @media(max-width:768px) {
        .main .block-container { padding:1rem 1rem 3rem !important; }
        .sv-card { padding:16px 12px !important; }
        .sv-sg  { grid-template-columns:repeat(2,1fr) !important; }
        .prof-hdr { flex-direction:column; text-align:center; }
        h1 { font-size:1rem !important; }
    }
    </style>
    """, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
#  HTML COMPONENT HELPERS
# ════════════════════════════════════════════════════════════

def wv():
    """Animated waveform bars."""
    h = [10,18,30,42,36,26,40,44,34,20,38,28]
    bars = "".join(f'<div class="sv-wb" style="height:{x}px"></div>' for x in h)
    return f'<div class="sv-wv">{bars}</div>'

def ring(icon):
    return (f'<div class="sv-rw"><div class="sv-ro"></div>'
            f'<div class="sv-ri"></div><span class="sv-ric">{icon}</span></div>')

def card_open(icon="", title=""):
    head = f'<div class="sv-card-head">{icon}&nbsp;{title}</div>' if title else ""
    st.markdown(f'<div class="sv-card">{head}', unsafe_allow_html=True)

def card_close():
    st.markdown('</div>', unsafe_allow_html=True)

def sl(text):
    """Section label inside a step block."""
    st.markdown(f'<div class="sv-sl">{text}</div>', unsafe_allow_html=True)

def steps(current, labels):
    items = ""
    for i, lbl in enumerate(labels):
        if i > 0:
            items += '<div class="sv-step-line"></div>'
        cls = "d" if i < current else ("a" if i == current else "")
        num = "✓" if i < current else str(i+1)
        items += (f'<div class="sv-step-item">'
                  f'<div class="sv-step-c {cls}">{num}</div>'
                  f'<div class="sv-step-lbl">{lbl}</div></div>')
    st.markdown(f'<div class="sv-steps">{items}</div>', unsafe_allow_html=True)

def score_bar(score):
    pct = min(max(score, 0.0), 1.0) * 100
    col = "#00ff88" if score > 0.75 else ("#ffaa00" if score > 0.5 else "#ff2d78")
    st.markdown(
        f'<div class="sv-sr">'
        f'<div class="sv-pb-w"><div class="sv-pb" style="width:{pct}%;background:linear-gradient(90deg,{col},{col}88)"></div></div>'
        f'<div class="sv-sv">{score:.4f}</div></div>',
        unsafe_allow_html=True)

def badge(text, v="cyan"):
    cls = {"g":"sv-badge sv-badge-g", "am":"sv-badge sv-badge-am"}.get(v,"sv-badge")
    dot_cls = "sv-dot sv-dot-g" if v=="g" else "sv-dot"
    st.markdown(
        f'<div style="margin-bottom:8px">'
        f'<span class="{cls}"><div class="{dot_cls}"></div>{text}</span></div>',
        unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
#  DATA  HELPERS
# ════════════════════════════════════════════════════════════

def save_user(data: dict):
    os.makedirs(os.path.dirname(USER_DATA), exist_ok=True)
    with open(USER_DATA, "w") as f:
        json.dump(data, f)

def load_user():
    if not os.path.exists(USER_DATA):
        return None
    with open(USER_DATA) as f:
        return json.load(f)

def log_act(icon, text):
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    entries = []
    if os.path.exists(LOG_FILE):
        try:
            entries = json.load(open(LOG_FILE))
        except Exception:
            entries = []
    now = datetime.datetime.now().strftime("%d %b %H:%M")
    entries.insert(0, {"icon": icon, "text": text, "time": now})
    with open(LOG_FILE, "w") as f:
        json.dump(entries[:30], f)

def get_log():
    if not os.path.exists(LOG_FILE):
        return []
    try:
        return json.load(open(LOG_FILE))
    except Exception:
        return []

def locked_count():
    if not os.path.exists(LOCK_FOLDER):
        return 0
    return len([x for x in os.listdir(LOCK_FOLDER) if x.endswith(".enc")])


def capture_audio_bytes(key, label):
    audio = st.audio_input(label, key=key)
    if audio is None:
        return None
    return audio.getvalue()


def audio_fingerprint(audio_bytes):
    if not audio_bytes:
        return None
    return hashlib.sha256(audio_bytes).hexdigest()


def save_audio_bytes(audio_bytes):
    os.makedirs("data/raw_audio", exist_ok=True)
    filename = os.path.join("data/raw_audio", f"{uuid.uuid4()}.wav")
    with open(filename, "wb") as f:
        f.write(audio_bytes)
    return filename


# ════════════════════════════════════════════════════════════
#  VOICE  AUTH  CORE
# ════════════════════════════════════════════════════════════

def run_voice(audio_bytes):
    """Process one voice sample, returns (success: bool, score: float)."""
    st.markdown(wv(), unsafe_allow_html=True)
    if not audio_bytes:
        st.error("Please record your voice using the recorder above.")
        return False, 0.0
    raw   = save_audio_bytes(audio_bytes)
    proc  = preprocess_audio(raw)
    if detect_spoof(proc):
        log_act("⚠️", "Spoof attempt blocked — liveness check failed")
        st.error("⚠️ Anti-spoof triggered — liveness check failed")
        return False, 0.0
    emb = extract_features(proc)
    result, score = verify_voice(emb)
    return result, score


# ════════════════════════════════════════════════════════════
#  PAGE  ①  REGISTER
# ════════════════════════════════════════════════════════════

def page_register():
    card_open("👤", "New User Registration")
    st.markdown(ring("👤"), unsafe_allow_html=True)
    steps(0, ["Identity","Phrase","Voice","Done"])

    if load_user() is not None:
        st.info("This app supports a single user. Please log in.")
        card_close()
        navigate("🔑 Login")
        return

    col1, col2 = st.columns(2)
    with col1:
        name   = st.text_input("Full Name",     placeholder="Enter your name…",          key="reg_name")
    with col2:
        phrase = st.text_input("Unlock Phrase", placeholder="Choose a secret phrase…",   key="reg_phrase")

    photo_f = st.file_uploader("Profile Photo  (optional)", type=["png","jpg","jpeg"], key="reg_photo")

    s1 = capture_audio_bytes("reg_audio_1", "Voice Sample 1")
    s2 = capture_audio_bytes("reg_audio_2", "Voice Sample 2")
    s3 = capture_audio_bytes("reg_audio_3", "Voice Sample 3")
    s4 = capture_audio_bytes("reg_audio_4", "Voice Sample 4")
    s5 = capture_audio_bytes("reg_audio_5", "Voice Sample 5")

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    if st.button("⚡  Begin Voice Registration", key="btn_reg"):
        if not name.strip() or not phrase.strip():
            st.error("Please fill in both Name and Unlock Phrase")
        elif not all([s1, s2, s3, s4, s5]):
            st.error("Please record all 5 voice samples before continuing")
        else:
            st.info("🎤 Recording 5 voice samples. Speak your unlock phrase each time.")
            embeddings = []
            prog = st.progress(0)
            for i, audio_bytes in enumerate([s1, s2, s3, s4, s5]):
                st.warning(f"🎙️  Sample {i+1}/5 — processing")
                st.markdown(wv(), unsafe_allow_html=True)
                raw  = save_audio_bytes(audio_bytes)
                proc = preprocess_audio(raw)
                emb  = extract_features(proc)
                embeddings.append(emb)
                prog.progress((i+1)/5)
            save_multiple_embeddings(embeddings)

            photo_b64 = None
            if photo_f:
                photo_b64 = base64.b64encode(photo_f.read()).decode()

            save_user({
                "name":       name.strip(),
                "phrase":     phrase.strip(),
                "registered": str(datetime.date.today()),
                "photo":      photo_b64
            })
            log_act("✅", f"User '{name.strip()}' registered successfully")
            steps(4, ["Identity","Phrase","Voice","Done"])
            st.success("✅ Registration complete! Please log in to continue.")
            navigate("🔑 Login")

    card_close()


# ════════════════════════════════════════════════════════════
#  PAGE  ②  LOGIN
# ════════════════════════════════════════════════════════════

def page_login():
    user = load_user()
    card_open("🔑", "Voice Authentication — Login")
    st.markdown(ring("🎙️"), unsafe_allow_html=True)

    st.markdown(
        f'<div style="text-align:center;margin-bottom:14px">'
        f'<span class="sv-badge"><div class="sv-dot"></div>Registered: {user["name"]}</span></div>',
        unsafe_allow_html=True)

    # ─ Step 1: Voice ─────────────────────────────────
    st.markdown('<div class="sv-sb">', unsafe_allow_html=True)
    sl("Step 1 — Voice Biometric Scan")
    audio_bytes = capture_audio_bytes("login_audio", "Record Voice Sample")
    audio_hash = audio_fingerprint(audio_bytes)
    if audio_hash and st.session_state.get("lv_hash") != audio_hash:
        with st.spinner("Scanning…"):
            ok, sc = run_voice(audio_bytes)
        st.session_state["lv_ok"] = ok
        st.session_state["lv_sc"] = sc
        st.session_state["lv_hash"] = audio_hash

    sc = st.session_state.get("lv_sc", 0.0)
    score_bar(sc)
    if sc > 0:
        msg = ("✓ Voice matched" if st.session_state.get("lv_ok") else "✗ Voice not matched — try again")
        col = "#00ff88" if st.session_state.get("lv_ok") else "#ff2d78"
        st.markdown(f'<div style="font-family:var(--fm);font-size:.62rem;color:{col};margin-top:4px">{msg}</div>',
                    unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ─ Step 2: Phrase ────────────────────────────────
    st.markdown('<div class="sv-sb">', unsafe_allow_html=True)
    sl("Step 2 — Phrase Verification")
    phrase_in = st.text_input("Type your unlock phrase",
                               placeholder="Enter your secret phrase…",
                               type="password", key="login_phrase")
    st.markdown('</div>', unsafe_allow_html=True)

    col_a, col_b = st.columns([2,1])
    with col_a:
        if st.button("✅  Confirm & Login", key="btn_login_confirm"):
            voice_ok  = st.session_state.get("lv_ok", False)
            phrase_ok = phrase_in.strip().lower() == user["phrase"].strip().lower()
            if voice_ok and phrase_ok:
                st.session_state.update({
                    "logged_in": True,
                    "lv_ok": False, "lv_sc": 0.0,
                })
                log_act("✅", f"Login OK — score {sc:.4f}")
                st.success("✅ Identity confirmed — welcome!")
                navigate("🏠 Dashboard")
            elif not voice_ok:
                st.error("❌ Record your voice first (Step 1)")
            else:
                log_act("❌", "Login failed — incorrect phrase")
                st.error("❌ Phrase mismatch — please try again")
    with col_b:
        if st.button("📝  Register", key="btn_go_reg"):
            navigate("👤 Register")

    card_close()


# ════════════════════════════════════════════════════════════
#  PAGE  ③  DASHBOARD  (Profile)
# ════════════════════════════════════════════════════════════

def page_dashboard():
    user = load_user()
    if user is None:
        st.error("No profile found.")
        return

    name    = user["name"]
    reg     = user.get("registered", "—")
    photo   = user.get("photo")
    locked  = locked_count()
    initials = "".join(w[0].upper() for w in name.split()[:2])

    av_html = (f'<div class="sv-avatar"><img src="data:image/png;base64,{photo}" /></div>'
               if photo else f'<div class="sv-avatar">{initials}</div>')

    # ── Profile header ──────────────────────────────
    st.markdown(f"""
    <div class="prof-hdr">
        {av_html}
        <div style="flex:1">
            <div class="prof-name">{name}</div>
            <div class="prof-role">VOICE AUTH USER &nbsp;·&nbsp; REGISTERED {reg.upper()}</div>
            <div style="margin-top:8px">
                <span class="sv-badge sv-badge-g"><div class="sv-dot sv-dot-g"></div>Session Active</span>
            </div>
        </div>
        <div style="display:flex;flex-direction:column;gap:7px;align-items:flex-end">
            <span class="sv-badge" style="font-size:.46rem">🔐 AES-256</span>
            <span class="sv-badge sv-badge-am">🛡️ Anti-Spoof ON</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Two-column cards ─────────────────────────────
    c1, c2 = st.columns(2, gap="medium")

    with c1:
        card_open("🛡️", "Security Status")
        st.markdown("""
        <div class="sv-sg">
          <div class="sv-stat"><div class="sv-stat-l">Voice Model</div><span class="sv-stat-i">🎙️</span><div class="sv-stat-v">READY</div></div>
          <div class="sv-stat"><div class="sv-stat-l">Encryption</div><span class="sv-stat-i">🔐</span><div class="sv-stat-v">AES-256</div></div>
          <div class="sv-stat"><div class="sv-stat-l">Anti-Spoof</div><span class="sv-stat-i">🛡️</span><div class="sv-stat-v">ACTIVE</div></div>
        </div>
        """, unsafe_allow_html=True)
        last = st.session_state.get("last_score", 0.0)
        if last > 0:
            sl("Last auth score")
            score_bar(last)
        card_close()

    with c2:
        card_open("📦", "Vault Summary")
        st.markdown(f"""
        <div class="sv-sg2">
          <div class="sv-stat">
            <div class="sv-stat-l">Locked Files</div><span class="sv-stat-i">🔒</span>
            <div class="sv-stat-v" style="font-size:1.3rem">{locked}</div>
          </div>
          <div class="sv-stat">
            <div class="sv-stat-l">Voice Samples</div><span class="sv-stat-i">🎤</span>
            <div class="sv-stat-v" style="font-size:1.3rem;color:#7b2fff">5</div>
          </div>
        </div>
        """, unsafe_allow_html=True)
        ca, cb = st.columns(2)
        with ca:
            if st.button("🔒 Lock", key="d_lock"):
                navigate("🔒 Lock File")
                st.rerun()
        with cb:
            if st.button("🔓 Unlock", key="d_unlock"):
                navigate("🔓 Unlock File")
                st.rerun()
        card_close()

    # ── Activity feed ────────────────────────────────
    card_open("📋", "Recent Activity")
    log = get_log()
    if not log:
        st.markdown('<div class="sv-fi"><span class="sv-fi-ico">💤</span><div class="sv-fi-txt" style="color:#4a7fa5">No activity yet</div></div>',
                    unsafe_allow_html=True)
    else:
        for e in log[:6]:
            st.markdown(
                f'<div class="sv-fi"><span class="sv-fi-ico">{e["icon"]}</span>'
                f'<div class="sv-fi-txt">{e["text"]}</div>'
                f'<div class="sv-fi-t">{e["time"]}</div></div>',
                unsafe_allow_html=True)
    card_close()

    # ── Quick action row ─────────────────────────────
    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
    qa1, qa2, qa3 = st.columns(3, gap="small")
    with qa1:
        if st.button("✏️  Edit Profile", key="d_edit"):
            navigate("✏️ Edit Profile")
            st.rerun()
    with qa2:
        st.markdown('<div class="sv-dbtn">', unsafe_allow_html=True)
        if st.button("🔄  Reset Profile", key="d_reset"):
            navigate("🔄 Reset Profile")
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with qa3:
        st.markdown('<div class="sv-dbtn">', unsafe_allow_html=True)
        if st.button("🚪  Logout", key="d_logout"):
            log_act("🚪", f"{name} logged out")
            st.session_state.update({
                "logged_in": False,
                "lv_ok": False, "lv_sc": 0.0,
            })
            navigate("🔑 Login")
        st.markdown('</div>', unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
#  PAGE  ④  EDIT PROFILE
# ════════════════════════════════════════════════════════════

def page_edit_profile():
    user = load_user()
    if user is None:
        st.error("No profile found.")
        return

    card_open("✏️", "Edit Profile")
    st.markdown(ring("✏️"), unsafe_allow_html=True)

    # Current avatar
    photo = user.get("photo")
    if photo:
        st.markdown(
            f'<div style="text-align:center;margin-bottom:14px">'
            f'<div class="sv-avatar" style="width:80px;height:80px;margin:0 auto">'
            f'<img src="data:image/png;base64,{photo}" /></div></div>',
            unsafe_allow_html=True)

    new_photo = st.file_uploader("Update Profile Photo", type=["png","jpg","jpeg"], key="edit_photo")

    col1, col2 = st.columns(2)
    with col1:
        new_name   = st.text_input("Full Name",     value=user["name"],   key="edit_name")
    with col2:
        new_phrase = st.text_input("Unlock Phrase", value=user["phrase"], key="edit_phrase")

    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    cs, cb = st.columns(2)
    with cs:
        if st.button("💾  Save Changes", key="btn_save"):
            if not new_name.strip() or not new_phrase.strip():
                st.error("Name and phrase cannot be empty")
            else:
                updated = {**user, "name": new_name.strip(), "phrase": new_phrase.strip()}
                if new_photo:
                    updated["photo"] = base64.b64encode(new_photo.read()).decode()
                save_user(updated)
                log_act("✏️", "Profile updated — name/phrase changed")
                st.success("✅ Profile saved!")
    with cb:
        if st.button("← Dashboard", key="btn_back"):
            navigate("🏠 Dashboard")

    # Re-record voice
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    with st.expander("🎤  Re-record Voice Samples"):
        st.warning("This replaces your existing voice model with 5 new recordings.")
        r1 = capture_audio_bytes("rerec_audio_1", "Voice Sample 1")
        r2 = capture_audio_bytes("rerec_audio_2", "Voice Sample 2")
        r3 = capture_audio_bytes("rerec_audio_3", "Voice Sample 3")
        r4 = capture_audio_bytes("rerec_audio_4", "Voice Sample 4")
        r5 = capture_audio_bytes("rerec_audio_5", "Voice Sample 5")
        if st.button("🔴  Start Voice Re-recording", key="btn_rerecord"):
            if not all([r1, r2, r3, r4, r5]):
                st.error("Please record all 5 voice samples before continuing")
                card_close()
                return
            embeddings = []
            prog = st.progress(0)
            for i, audio_bytes in enumerate([r1, r2, r3, r4, r5]):
                st.info(f"🎙️ Recording {i+1}/5 — processing")
                st.markdown(wv(), unsafe_allow_html=True)
                raw  = save_audio_bytes(audio_bytes)
                proc = preprocess_audio(raw)
                emb  = extract_features(proc)
                embeddings.append(emb)
                prog.progress((i+1)/5)
            save_multiple_embeddings(embeddings)
            log_act("🎤", "Voice samples re-recorded")
            st.success("✅ Voice model updated!")

    card_close()


# ════════════════════════════════════════════════════════════
#  PAGE  ⑤  RESET PROFILE  (voice-auth gated)
# ════════════════════════════════════════════════════════════

def page_reset():
    user = load_user()
    card_open("🔄", "Reset Profile — Voice Auth Required")
    st.markdown(ring("⚠️"), unsafe_allow_html=True)

    st.markdown("""
    <div class="sv-danger-box">
        <div class="sv-danger-title">⚠️  DESTRUCTIVE ACTION</div>
        <div class="sv-danger-body">
            Permanently deletes your voice model, all locked files, and account data.<br>
            Voice authentication + phrase confirmation required to proceed.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ─ Voice auth ─────────────────────────────────────
    st.markdown('<div class="sv-sb">', unsafe_allow_html=True)
    sl("Step 1 — Verify Your Identity")
    audio_bytes = capture_audio_bytes("reset_audio", "Record Voice Sample")
    audio_hash = audio_fingerprint(audio_bytes)
    if audio_hash and st.session_state.get("rv_hash") != audio_hash:
        with st.spinner("Verifying…"):
            ok, sc = run_voice(audio_bytes)
        st.session_state["rv_ok"] = ok
        st.session_state["rv_sc"] = sc
        st.session_state["rv_hash"] = audio_hash

    r_sc = st.session_state.get("rv_sc", 0.0)
    score_bar(r_sc)
    if r_sc > 0:
        ok_txt = "✓ Identity verified" if st.session_state.get("rv_ok") else "✗ Voice not matched"
        ok_col = "#00ff88" if st.session_state.get("rv_ok") else "#ff2d78"
        st.markdown(f'<div style="font-family:var(--fm);font-size:.62rem;color:{ok_col};margin-top:4px">{ok_txt}</div>',
                    unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # ─ Phrase confirm ─────────────────────────────────
    st.markdown('<div class="sv-sb">', unsafe_allow_html=True)
    sl("Step 2 — Type Unlock Phrase to Confirm")
    phrase_c = st.text_input("Unlock Phrase", type="password", key="reset_phrase")
    st.markdown('</div>', unsafe_allow_html=True)

    ca, cb = st.columns(2)
    with ca:
        st.markdown('<div class="sv-dbtn">', unsafe_allow_html=True)
        if st.button("🗑️  DELETE & Reset Everything", key="btn_do_reset"):
            voice_ok  = st.session_state.get("rv_ok", False)
            phrase_ok = phrase_c.strip().lower() == user["phrase"].strip().lower() if user else False
            if voice_ok and phrase_ok:
                reset_profile()
                for path in [USER_DATA, LOG_FILE]:
                    if os.path.exists(path):
                        os.remove(path)
                if os.path.exists(LOCK_FOLDER):
                    shutil.rmtree(LOCK_FOLDER, ignore_errors=True)
                for k in ["logged_in","lv_ok","lv_sc","rv_ok","rv_sc","last_score"]:
                    st.session_state[k] = False if "ok" in k or k=="logged_in" else 0.0
                navigate("👤 Register")
                st.success("✅ Profile reset. Please re-register.")
                
            elif not voice_ok:
                st.error("❌ Voice authentication required before reset")
            else:
                st.error("❌ Phrase mismatch — reset blocked")
        st.markdown('</div>', unsafe_allow_html=True)
    with cb:
        if st.button("← Cancel", key="btn_cancel_reset"):
            navigate("🏠 Dashboard")

    card_close()


# ════════════════════════════════════════════════════════════
#  PAGE  ⑥  LOCK FILE
# ════════════════════════════════════════════════════════════

def page_lock():
    user = load_user()
    card_open("🔒", "Encrypt & Lock File")
    st.markdown(ring("🔒"), unsafe_allow_html=True)

    if user is None:
        st.error("⚠️ No user profile — please register first")
        card_close()
        return

    badge("Vault Ready · Upload to Encrypt")

    file_up = st.file_uploader(
        "Select file to encrypt",
        key="lock_upload",
        help="Your file will be AES-256 encrypted and stored securely in the vault."
    )
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    if st.button("🔐  Encrypt & Lock File", key="btn_lock"):
        if not file_up:
            st.error("Please upload a file first")
        else:
            with st.spinner("Encrypting with AES-256…"):
                os.makedirs(LOCK_FOLDER, exist_ok=True)
                tmp = os.path.join(LOCK_FOLDER, file_up.name)
                enc = tmp + ".enc"
                with open(tmp, "wb") as f:
                    f.write(file_up.getbuffer())
                encrypt_file(tmp, enc)
                os.remove(tmp)
            log_act("🔒", f"{file_up.name} encrypted and locked")
            st.success(f"🔒 {file_up.name} encrypted and stored in vault!")

    # Show current vault contents
    if os.path.exists(LOCK_FOLDER):
        files = [x for x in os.listdir(LOCK_FOLDER) if x.endswith(".enc")]
        if files:
            st.markdown(
                f'<div style="margin-top:14px"><div class="sv-sl">Vault Contents ({len(files)} file(s))</div>',
                unsafe_allow_html=True)
            for fname in files:
                st.markdown(
                    f'<div class="sv-fi"><span class="sv-fi-ico">🔒</span>'
                    f'<div class="sv-fi-txt">{fname.replace(".enc","")}</div>'
                    f'<div class="sv-fi-t">ENCRYPTED</div></div>',
                    unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    card_close()


# ════════════════════════════════════════════════════════════
#  PAGE  ⑦  UNLOCK FILE
# ════════════════════════════════════════════════════════════

def page_unlock():
    user = load_user()
    card_open("🔓", "Biometric Authentication — Unlock Files")
    st.markdown(ring("🎙️"), unsafe_allow_html=True)

    if user is None:
        st.error("⚠️ No user profile found")
        card_close()
        return

    # ─ Step 1: Voice ─────────────────────────────────
    st.markdown('<div class="sv-sb">', unsafe_allow_html=True)
    sl("Step 1 — Voice Biometric Scan")
    audio_bytes = capture_audio_bytes("unlock_audio", "Record Voice Sample")
    audio_hash = audio_fingerprint(audio_bytes)
    if audio_hash and st.session_state.get("uv_hash") != audio_hash:
        with st.spinner("Verifying biometric…"):
            ok, sc = run_voice(audio_bytes)
        st.session_state["uv_ok"] = ok
        st.session_state["uv_sc"] = sc
        st.session_state["uv_hash"] = audio_hash
        st.session_state["last_score"] = sc

    u_sc = st.session_state.get("uv_sc", 0.0)
    score_bar(u_sc)
    st.markdown('</div>', unsafe_allow_html=True)

    # ─ Step 2: Phrase ─────────────────────────────────
    st.markdown('<div class="sv-sb">', unsafe_allow_html=True)
    sl("Step 2 — Phrase Verification")
    u_phrase = st.text_input("Enter unlock phrase", type="password", key="unlock_phrase_in")
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("🔓  Confirm & Decrypt Files", key="btn_unlock_confirm"):
        voice_ok  = st.session_state.get("uv_ok", False)
        phrase_ok = u_phrase.strip().lower() == user["phrase"].strip().lower() if u_phrase else False

        if voice_ok and phrase_ok:
            log_act("🔓", f"Vault unlocked (score: {u_sc:.4f})")
            st.success("✅ Identity confirmed — vault opened!")

            if not os.path.exists(LOCK_FOLDER):
                st.info("📭 No files in vault")
            else:
                files = [x for x in os.listdir(LOCK_FOLDER) if x.endswith(".enc")]
                if not files:
                    st.info("📭 Vault is empty")
                else:
                    st.markdown(
                        f'<div class="sv-sl" style="margin:14px 0 8px">'
                        f'{len(files)} file(s) ready to download</div>',
                        unsafe_allow_html=True)
                    for fname in files:
                        enc = os.path.join(LOCK_FOLDER, fname)
                        dec = os.path.join(LOCK_FOLDER, "unlocked_" + fname.replace(".enc",""))
                        decrypt_file(enc, dec)
                        with open(dec, "rb") as fh:
                            st.download_button(
                                f"⬇️  {fname.replace('.enc','')}",
                                fh,
                                file_name=fname.replace(".enc",""),
                                key=f"dl_{fname}"
                            )
        elif not st.session_state.get("uv_ok", False):
            st.error("❌ Record your voice first (Step 1)")
        else:
            log_act("❌", "Unlock failed — phrase mismatch")
            st.error("❌ Phrase mismatch — access denied")

    card_close()


# ════════════════════════════════════════════════════════════
#  MAIN
# ════════════════════════════════════════════════════════════

def main():
    st.set_page_config(
        page_title="Voice Locker · SecureVault",
        page_icon="🔐",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    apply_styles()

    # ── Init session state defaults ──────────────────
    defaults = {
        "logged_in": False,
        "lv_ok": False, "lv_sc": 0.0,   # login voice
        "uv_ok": False, "uv_sc": 0.0,   # unlock voice
        "rv_ok": False, "rv_sc": 0.0,   # reset voice
        "last_score": 0.0,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

    user      = load_user()
    logged_in = st.session_state["logged_in"]

    # ── Build nav options ────────────────────────────
    if user is None:
        nav = ["👤 Register"]
        default = "👤 Register"
    elif not logged_in:
        nav = ["🔑 Login"]
        default = "🔑 Login"
    else:
        nav = ["🏠 Dashboard","🔒 Lock File","🔓 Unlock File","✏️ Edit Profile","🔄 Reset Profile"]
        default = "🏠 Dashboard"

    # SAFE NAV HANDLER
    if "__nav_target" in st.session_state:
        st.session_state["nav_radio"] = st.session_state["__nav_target"]
        del st.session_state["__nav_target"]

    # Guard: if stored page not in current nav, reset to default
    # ── SAFE NAVIGATION HANDLER (RUNS BEFORE WIDGET) ──
    if "__nav_target" in st.session_state:
        st.session_state["nav_radio"] = st.session_state["__nav_target"]
        del st.session_state["__nav_target"]

    # SAFE NAV HANDLER
    if "__nav_target" in st.session_state:
        st.session_state["nav_radio"] = st.session_state["__nav_target"]
        del st.session_state["__nav_target"]

    # Guard: if stored page not in current nav, reset to default
    if "nav_radio" not in st.session_state or st.session_state["nav_radio"] not in nav:
        st.session_state["nav_radio"] = default

    # ── SIDEBAR ──────────────────────────────────────
    with st.sidebar:
        # Logo block
        st.markdown("""
        <div style="padding:16px 0 18px;text-align:center;
                    border-bottom:1px solid rgba(0,245,255,0.12);margin-bottom:12px">
            <div style="font-size:2.4rem;margin-bottom:5px;
                        filter:drop-shadow(0 0 14px rgba(0,245,255,0.7))">🔐</div>
            <div style="font-family:'Orbitron',monospace;font-size:.6rem;
                        letter-spacing:3px;color:#00f5ff;text-transform:uppercase">SecureVault</div>
            <div style="font-family:'Share Tech Mono',monospace;font-size:.47rem;
                        color:#4a7fa5;letter-spacing:2px;margin-top:3px">v2.1 · Voice Auth</div>
        </div>
        """, unsafe_allow_html=True)

        # Navigation radio — key links it to session state
        st.title("🔒 Navigation")
        st.radio("Go to", nav, key="nav_radio", label_visibility="collapsed")

        # Status pill
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
        if logged_in and user:
            st.markdown(f"""
            <div style="padding:10px 12px;background:rgba(0,255,136,0.07);
                        border:1px solid rgba(0,255,136,0.2);border-radius:9px;margin-bottom:10px">
                <div style="font-family:'Share Tech Mono',monospace;font-size:.5rem;
                            color:#00ff88;letter-spacing:1px;margin-bottom:3px">● LOGGED IN</div>
                <div style="font-family:'Orbitron',monospace;font-size:.58rem;
                            color:#cce8ff">{user["name"]}</div>
            </div>
            """, unsafe_allow_html=True)
        elif user:
            st.markdown("""
            <div style="padding:10px 12px;background:rgba(255,170,0,0.07);
                        border:1px solid rgba(255,170,0,0.2);border-radius:9px;margin-bottom:10px">
                <div style="font-family:'Share Tech Mono',monospace;font-size:.5rem;
                            color:#ffaa00;letter-spacing:1px;margin-bottom:3px">● REGISTERED</div>
                <div style="font-family:'Rajdhani',sans-serif;font-size:.78rem;color:#4a7fa5">
                    Login required</div>
            </div>
            """, unsafe_allow_html=True)

        # Footer — normal flow, NOT absolute positioned (fixes text overlap bug)
        st.markdown("""
        <div style="margin-top:18px;padding-top:12px;
                    border-top:1px solid rgba(0,245,255,0.1);
                    font-family:'Share Tech Mono',monospace;font-size:.44rem;
                    color:#4a7fa5;letter-spacing:.8px;line-height:2.2;text-align:center">
            ENCRYPTED · AES-256<br>VOICE BIOMETRIC AUTH<br>ANTI-SPOOF ENABLED
        </div>
        """, unsafe_allow_html=True)

    # ── PAGE TITLE ────────────────────────────────────
    st.title("🎙️ Voice-Based Secure File Locker")
    st.markdown("""
    <div style="font-family:'Share Tech Mono',monospace;font-size:.56rem;color:#4a7fa5;
                letter-spacing:3.5px;text-transform:uppercase;margin-bottom:1.4rem">
        Biometric Security · AES-256 Encryption · Anti-Spoofing
    </div>
    """, unsafe_allow_html=True)

    # ── ROUTER ────────────────────────────────────────
    page = st.session_state["nav_radio"]

    if   page == "👤 Register":      page_register()
    elif page == "🔑 Login":          page_login()
    elif page == "🏠 Dashboard":      page_dashboard()
    elif page == "🔒 Lock File":      page_lock()
    elif page == "🔓 Unlock File":    page_unlock()
    elif page == "✏️ Edit Profile":   page_edit_profile()
    elif page == "🔄 Reset Profile":  page_reset()


if __name__ == "__main__":
    main()