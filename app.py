import streamlit as st
import requests
from bs4 import BeautifulSoup
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
import json
import os
from datetime import datetime
import pandas as pd

st.set_page_config(page_title="PitchSpy", page_icon="🔍", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&display=swap');
html, body, [class*="css"] { font-family: 'DM Mono', monospace; background-color: #0a0a0a; color: #e8e8e0; }
.main { background-color: #0a0a0a; }
h1, h2, h3 { font-family: 'Syne', sans-serif !important; font-weight: 800; }
.hero-title { font-family: 'Syne', sans-serif; font-size: 3.2rem; font-weight: 800; letter-spacing: -0.03em; line-height: 1.1; color: #e8e8e0; margin-bottom: 0.2rem; }
.hero-sub { font-family: 'DM Mono', monospace; font-size: 0.85rem; color: #5a5a52; letter-spacing: 0.08em; text-transform: uppercase; margin-bottom: 2.5rem; }
.accent { color: #c8f135; }
.card { background: #111110; border: 1px solid #222220; border-radius: 12px; padding: 1.5rem 1.8rem; margin-bottom: 1rem; }
.card-label { font-family: 'DM Mono', monospace; font-size: 0.7rem; letter-spacing: 0.12em; text-transform: uppercase; color: #c8f135; margin-bottom: 0.5rem; }
.card-content { font-size: 0.95rem; color: #d0d0c8; line-height: 1.7; }
.score-badge { display: inline-block; padding: 0.25rem 0.9rem; border-radius: 999px; font-family: 'Syne', sans-serif; font-weight: 700; font-size: 0.85rem; letter-spacing: 0.04em; }
.hot { background: #c8f135; color: #0a0a0a; }
.warm { background: #f1a935; color: #0a0a0a; }
.cold { background: #3555f1; color: #ffffff; }
.divider { border: none; border-top: 1px solid #1e1e1c; margin: 2rem 0; }
.url-heading { font-family: 'Syne', sans-serif; font-size: 1.1rem; font-weight: 700; color: #c8f135; margin: 1.5rem 0 0.5rem 0; }
.error-box { background: #1a0a0a; border: 1px solid #f1353530; border-radius: 10px; padding: 1rem 1.2rem; margin-bottom: 0.5rem; color: #f17070; font-size: 0.88rem; }
.warn-box { background: #2e1f0a; border: 1px solid #f1a93550; border-radius: 10px; padding: 1rem 1.2rem; margin-bottom: 0.5rem; color: #f1a935; font-size: 0.88rem; }
.chat-msg-user { background: #1a1a18; border: 1px solid #2a2a28; border-radius: 10px; padding: 0.8rem 1.2rem; margin-bottom: 0.5rem; color: #e8e8e0; font-size: 0.9rem; }
.chat-msg-ai { background: #111110; border: 1px solid #c8f13530; border-radius: 10px; padding: 0.8rem 1.2rem; margin-bottom: 0.5rem; color: #d0d0c8; font-size: 0.9rem; line-height: 1.7; }
.pitch-section { background: #111110; border: 1px solid #222220; border-radius: 12px; padding: 1.8rem; margin-bottom: 1.2rem; }
.pitch-title { font-family: 'Syne', sans-serif; font-size: 1rem; font-weight: 700; color: #c8f135; margin-bottom: 1rem; letter-spacing: 0.05em; text-transform: uppercase; }
.pitch-content { font-size: 0.95rem; color: #d0d0c8; line-height: 1.8; }
.verdict-go { background: #1a2e0a; border: 1px solid #c8f135; border-radius: 12px; padding: 1.5rem 1.8rem; margin-bottom: 1rem; }
.verdict-risky { background: #2e1f0a; border: 1px solid #f1a935; border-radius: 12px; padding: 1.5rem 1.8rem; margin-bottom: 1rem; }
.verdict-nogo { background: #1a0a0a; border: 1px solid #f13535; border-radius: 12px; padding: 1.5rem 1.8rem; margin-bottom: 1rem; }
.stTextInput > div > div > input { background: #111110 !important; border: 1px solid #2a2a28 !important; border-radius: 8px !important; color: #e8e8e0 !important; font-family: 'DM Mono', monospace !important; font-size: 0.9rem !important; padding: 0.75rem 1rem !important; }
.stTextInput > div > div > input:focus { border-color: #c8f135 !important; box-shadow: 0 0 0 2px rgba(200,241,53,0.15) !important; }
.stTextArea > div > div > textarea { background: #111110 !important; border: 1px solid #2a2a28 !important; border-radius: 8px !important; color: #e8e8e0 !important; font-family: 'DM Mono', monospace !important; font-size: 0.9rem !important; }
/* All buttons default - accent green */
.stButton > button { background: #c8f135 !important; color: #0a0a0a !important; font-family: 'Syne', sans-serif !important; font-weight: 700 !important; font-size: 0.95rem !important; border: none !important; border-radius: 8px !important; padding: 0.65rem 2rem !important; letter-spacing: 0.03em !important; width: 100% !important; }
.stButton > button:hover { opacity: 0.85 !important; }
/* About and Contact - muted green small buttons */
[data-testid="stButton"] button[data-testid="baseButton-secondary"],
button[kind="secondary"] { background: #2d4a1e !important; color: #c8f135 !important; font-family: 'DM Mono', monospace !important; font-weight: 500 !important; font-size: 0.75rem !important; border: 1px solid #3d6a2e !important; border-radius: 6px !important; padding: 0.3rem 0.9rem !important; width: auto !important; letter-spacing: 0.05em !important; }
.stSpinner > div { border-top-color: #c8f135 !important; }
footer { display: none; }
#MainMenu { display: none; }
</style>
""", unsafe_allow_html=True)

# ── Config ────────────────────────────────────────────────────────────────────
# FIX 1: Validate API key on startup so we catch it early
# If the key is missing or still default, we warn the user immediately
# instead of crashing later when they try to analyze something
GROQ_API_KEY = st.secrets["GROQ_API_KEY"]
HISTORY_FILE = "history.json"

def is_valid_api_key(key):
    # A real Groq key starts with "gsk_" and is longer than 20 chars
    return key and key.startswith("gsk_") and len(key) > 20

# ── Scraper ───────────────────────────────────────────────────────────────────
# FIX 4: Auto-fix URLs missing https://
# If user types "notion.so" instead of "https://notion.so"
# we fix it automatically instead of showing an error
def normalize_url(url: str) -> str:
    url = url.strip()
    if url and not url.startswith("http"):
        url = "https://" + url
    return url

def scrape_website(url: str) -> str:
    headers = {"User-Agent": "Mozilla/5.0 (compatible; PitchSpy/1.0)"}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "head"]):
            tag.decompose()
        text = " ".join(soup.get_text(separator=" ").split())
        # FIX 5: Check if scraped content is too short
        # Some sites block scrapers and return empty or tiny pages
        # We catch this and show a friendly message instead of
        # sending garbage to the AI
        if len(text) < 100:
            return "ERROR: Site returned too little content — it may be blocking scrapers."
        return text[:4000]
    except requests.exceptions.ConnectionError:
        return "ERROR: Could not connect — check your internet connection."
    except requests.exceptions.Timeout:
        return "ERROR: Request timed out — the site took too long to respond."
    except requests.exceptions.HTTPError as e:
        return f"ERROR: Site returned an error ({e.response.status_code})."
    except Exception as e:
        return f"ERROR: {e}"

# ── Analysis ──────────────────────────────────────────────────────────────────
PROMPT = PromptTemplate(
    input_variables=["content"],
    template="""
You are a sharp, objective startup analyst. Analyze this competitor website content carefully.

Return EXACTLY this structure (no extra text, no markdown):

SUMMARY: [2-3 sentence plain-English summary of what this company does]
TARGET_CUSTOMER: [1 sentence describing who they sell to]
PRICING: [Their pricing model, or "Not detectable"]
GAP: [1-2 sentences on a real weakness or opportunity to exploit]
POSITIONING: [One punchy line: "For [audience] who [problem], unlike [competitor] we [advantage]."]
THREAT_LEVEL: [Carefully assess: HOT = well-funded, large user base, dominant market position. WARM = growing but has weaknesses. COLD = niche, outdated, or limited reach. Return ONE word only.]

Be honest and objective. Not every competitor is HOT. Most are WARM or COLD.

Website content:
{content}
"""
)

def analyze(content: str) -> dict:
    # FIX 6: Wrap AI calls in try/except
    # If the API key is wrong, rate limit is hit, or Groq is down,
    # we return an empty dict with an error key instead of crashing
    try:
        llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=GROQ_API_KEY, max_tokens=600)
        chain = PROMPT | llm
        raw = chain.invoke({"content": content}).content
        result = {}
        for line in raw.strip().splitlines():
            if ":" in line:
                key, _, val = line.partition(":")
                result[key.strip()] = val.strip()
        # FIX 7: Check if AI returned expected fields
        # Sometimes the AI returns an unexpected format
        # We check for at least SUMMARY — if missing, something went wrong
        if "SUMMARY" not in result:
            return {"_error": "AI returned an unexpected response. Please try again."}
        return result
    except Exception as e:
        return {"_error": f"AI error: {str(e)}"}

def ask_followup(question: str, analyses: list) -> str:
    # FIX 8: Validate question isn't too short or vague
    try:
        context = "\n\n".join([
            f"Competitor: {a['url']}\n" + "\n".join([f"{k}: {v}" for k, v in a['data'].items()])
            for a in analyses
        ])
        llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=GROQ_API_KEY, max_tokens=500)
        prompt = f"""You are a startup advisor. A founder has analyzed these competitors:

{context}

The founder asks: {question}

Give a sharp, direct answer in 2-4 sentences. Be specific and actionable."""
        return llm.invoke(prompt).content
    except Exception as e:
        return f"Sorry, something went wrong: {str(e)}"

def generate_pitch_slide(analyses: list, startup_description: str) -> dict:
    try:
        context = "\n\n".join([
            f"Competitor: {a['url']}\n" + "\n".join([f"{k}: {v}" for k, v in a['data'].items()])
            for a in analyses
        ])
        llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=GROQ_API_KEY, max_tokens=1000)
        prompt = f"""You are a world-class startup pitch coach.

Founder's startup: {startup_description}

Competitor analysis:
{context}

Generate the "Market & Competition" slide. Return EXACTLY this structure (no markdown):

MARKET_SUMMARY: [2-3 sentences on the competitive landscape and opportunity]
POSITIONING_MAP: [Describe a 2x2 map. Format: "X-axis: [label]. Y-axis: [label]. We are: [position]. Competitors: [positions]"]
WHY_US: [2-3 sentences on the gap and why this startup wins]
ADVANTAGES: [Write exactly 3 advantages separated by | like this: Fast and simple to use | Built for solo founders | AI-powered with no setup required]
INVESTOR_ONELINER: [Unlike X and Y, we are the only tool that does Z]
VERDICT: [Assess honestly: GO = clear market gap exists and founder can win. NOGO = market is too crowded or no real gap. RISKY = gap exists but execution will be hard. Return ONE word only: GO, RISKY, or NOGO]
VERDICT_REASON: [1-2 sentences explaining the verdict honestly]
"""
        raw = llm.invoke(prompt).content

        # Better parser — handles multi-line values properly
        result = {}
        lines = raw.strip().splitlines()
        current_key = None
        current_val = []
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            # Check if this line starts a new key (ALL_CAPS_WITH_UNDERSCORE:)
            parts = stripped.split(":")
            potential_key = parts[0].strip()
            if potential_key.isupper() and len(parts) >= 2:
                if current_key:
                    result[current_key] = " ".join(current_val).strip()
                current_key = potential_key
                current_val = [":".join(parts[1:]).strip()]
            elif current_key:
                current_val.append(stripped)
        if current_key:
            result[current_key] = " ".join(current_val).strip()

        # Convert ADVANTAGES from pipe-separated to bullet points for display
        if "ADVANTAGES" in result:
            advantages = result["ADVANTAGES"]
            if "|" in advantages:
                items = [a.strip() for a in advantages.split("|")]
                result["ADVANTAGES"] = "\n".join([f"• {item}" for item in items if item])

        return result
    except Exception as e:
        return {"_error": str(e)}

def validate_demand(idea: str) -> dict:
    try:
        llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=GROQ_API_KEY, max_tokens=800)
        prompt = f"""You are a startup demand analyst with deep knowledge of markets, Reddit communities, Google Trends, and startup ecosystems.

Analyze the real market demand for this idea: {idea[:300]}

Return EXACTLY this format (no markdown):
DEMAND_SCORE: [1-10, be realistic]
EVIDENCE: [2 sentences - mention specific communities, forums, or known pain points that signal demand]
SOURCES: [2-3 specific places where this demand is visible e.g. Reddit r/entrepreneur, ProductHunt, specific forums]
VERDICT: [STRONG, MODERATE, or WEAK]
VERDICT_REASON: [1 sentence]
RISK: [1 sentence]
OPPORTUNITY: [1 sentence]
WHO_PAYS: [1 sentence]"""
        raw = llm.invoke(prompt).content
        result = {}
        for line in raw.strip().splitlines():
            if ":" in line:
                key, _, val = line.partition(":")
                result[key.strip()] = val.strip()
        if "DEMAND_SCORE" not in result:
            return {"_error": "AI returned unexpected response. Please try again."}
        return result
    except Exception as e:
        return {"_error": f"Error: {str(e)}"}

# ── Render helpers ────────────────────────────────────────────────────────────
def render_result(url, data):
    # FIX 10: Check for _error key before rendering
    if "_error" in data:
        st.markdown(f'<div class="error-box">⚠️ {data["_error"]}</div>', unsafe_allow_html=True)
        return
    st.markdown(f'<div class="url-heading">🔗 {url}</div>', unsafe_allow_html=True)
    level = data.get("THREAT_LEVEL", "WARM").upper()
    badge_class = "hot" if level == "HOT" else ("cold" if level == "COLD" else "warm")
    st.markdown(f'<span class="score-badge {badge_class}">⚡ {level} COMPETITOR</span>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    for label, key in [("What they do", "SUMMARY"), ("Their customer", "TARGET_CUSTOMER"),
                        ("Pricing model", "PRICING"), ("Gap you can exploit", "GAP"),
                        ("Your positioning", "POSITIONING")]:
        st.markdown(f'<div class="card"><div class="card-label">{label}</div><div class="card-content">{data.get(key, "—")}</div></div>', unsafe_allow_html=True)

def render_comparison_table(analyses):
    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown('<div class="card-label" style="font-size:0.8rem; margin-bottom:1rem;">⚡ COMPARISON TABLE</div>', unsafe_allow_html=True)
    rows = []
    for a in analyses:
        d = a["data"]
        if "_error" in d:
            continue
        level = d.get("THREAT_LEVEL", "WARM").upper()
        emoji = "🔴" if level == "HOT" else ("🟡" if level == "WARM" else "🔵")
        rows.append({
            "URL": a["url"].replace("https://", "").replace("www.", ""),
            "Threat": f"{emoji} {level}",
            "Target Customer": d.get("TARGET_CUSTOMER", "—"),
            "Pricing": d.get("PRICING", "—"),
            "Gap": d.get("GAP", "—"),
        })
    if rows:
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True, hide_index=True)

def render_pitch_slide(pitch):
    if "_error" in pitch:
        st.markdown(f'<div class="error-box">⚠️ {pitch["_error"]}</div>', unsafe_allow_html=True)
        return
    verdict = pitch.get("VERDICT", "RISKY").upper()
    verdict_class = "verdict-go" if verdict == "GO" else ("verdict-nogo" if verdict == "NOGO" else "verdict-risky")
    verdict_emoji = "🟢" if verdict == "GO" else ("🔴" if verdict == "NOGO" else "🟡")
    verdict_label = "GO FOR IT" if verdict == "GO" else ("NO-GO" if verdict == "NOGO" else "RISKY — PROCEED CAREFULLY")
    st.markdown(f'<div class="{verdict_class}"><div class="pitch-title">{verdict_emoji} VERDICT: {verdict_label}</div><div class="pitch-content">{pitch.get("VERDICT_REASON", "—")}</div></div>', unsafe_allow_html=True)
    for title, key in [("📊 Market Summary", "MARKET_SUMMARY"), ("🗺️ Positioning Map", "POSITIONING_MAP"),
                        ("💡 Why You Win", "WHY_US"), ("⚡ Competitive Advantages", "ADVANTAGES"),
                        ("🎯 Investor One-Liner", "INVESTOR_ONELINER")]:
        content_text = pitch.get(key, "—").replace("\n", "<br>")
        st.markdown(f'<div class="pitch-section"><div class="pitch-title">{title}</div><div class="pitch-content">{content_text}</div></div>', unsafe_allow_html=True)

def render_demand(data: dict):
    if "_error" in data:
        st.markdown(f'<div class="error-box">⚠️ {data["_error"]}</div>', unsafe_allow_html=True)
        return
    score = data.get("DEMAND_SCORE", "5")
    try:
        score_int = min(10, max(1, int(score)))  # clamp between 1-10
    except:
        score_int = 5
    verdict = data.get("VERDICT", "MODERATE").upper()
    if verdict == "STRONG":
        verdict_color, verdict_bg, verdict_border, verdict_emoji = "#c8f135", "#1a2e0a", "#c8f135", "🟢"
    elif verdict == "WEAK":
        verdict_color, verdict_bg, verdict_border, verdict_emoji = "#f13535", "#1a0a0a", "#f13535", "🔴"
    else:
        verdict_color, verdict_bg, verdict_border, verdict_emoji = "#f1a935", "#2e1f0a", "#f1a935", "🟡"
    st.markdown(f"""
    <div style="background:#111110; border:1px solid #222220; border-radius:12px; padding:1.5rem 1.8rem; margin-bottom:1rem; text-align:center;">
        <div style="font-family:'DM Mono',monospace; font-size:0.7rem; letter-spacing:0.12em; text-transform:uppercase; color:#5a5a52; margin-bottom:0.5rem;">DEMAND SCORE</div>
        <div style="font-family:'Syne',sans-serif; font-size:4rem; font-weight:800; color:{verdict_color};">{score_int}<span style="font-size:2rem; color:#5a5a52;">/10</span></div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown(f"""
    <div style="background:{verdict_bg}; border:1px solid {verdict_border}; border-radius:12px; padding:1.2rem 1.8rem; margin-bottom:1rem;">
        <div style="font-family:'Syne',sans-serif; font-size:0.9rem; font-weight:700; color:{verdict_color}; margin-bottom:0.4rem;">{verdict_emoji} {verdict} DEMAND</div>
        <div style="font-size:0.9rem; color:#d0d0c8;">{data.get("VERDICT_REASON", "—")}</div>
    </div>
    """, unsafe_allow_html=True)
    for label, key in [("📊 Evidence of Demand", "EVIDENCE"), ("🔗 Sources Found", "SOURCES"),
                        ("💰 Who Will Pay", "WHO_PAYS"), ("🚀 Opportunity", "OPPORTUNITY"),
                        ("⚠️ Biggest Risk", "RISK")]:
        st.markdown(f'<div class="card"><div class="card-label">{label}</div><div class="card-content">{data.get(key, "—")}</div></div>', unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
if "analyses" not in st.session_state:
    st.session_state.analyses = []
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "pitch" not in st.session_state:
    st.session_state.pitch = None
if "demand" not in st.session_state:
    st.session_state.demand = None
if "history" not in st.session_state:
    st.session_state.history = []  # session-only history — clears when browser closes
if "show_about" not in st.session_state:
    st.session_state.show_about = False
if "show_contact" not in st.session_state:
    st.session_state.show_contact = False

def save_to_history(url, data):
    # Now saves to session state only — private to each user's browser tab
    st.session_state.history.insert(0, {
        "url": url,
        "data": data,
        "time": datetime.now().strftime("%d %b %Y, %H:%M")
    })
    st.session_state.history = st.session_state.history[:20]

# ── UI ────────────────────────────────────────────────────────────────────────
col_title, col_btns = st.columns([5, 1])
with col_title:
    st.markdown('<div class="hero-title">Pitch<span class="accent">Spy</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">Competitor intelligence · in 10 seconds</div>', unsafe_allow_html=True)
with col_btns:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("About", key="about_btn", type="secondary"):
        st.session_state.show_about = not st.session_state.show_about
        st.session_state.show_contact = False
    if st.button("Contact", key="contact_btn", type="secondary"):
        st.session_state.show_contact = not st.session_state.show_contact
        st.session_state.show_about = False

if st.session_state.show_about:
    st.markdown("""
    <div class="card" style="margin-bottom:1.5rem;">
        <div class="card-label">About PitchSpy</div>
        <div class="card-content">
            <b style="color:#e8e8e0;">PitchSpy</b> is an AI-powered competitor intelligence tool built for early-stage founders.<br><br>
            Paste any competitor's website URL and get instant analysis — what they do, who they sell to, their pricing model, gaps you can exploit, and a ready-made positioning line.<br><br>
            <b style="color:#c8f135;">Features:</b><br>
            • Analyze multiple competitors at once<br>
            • Side-by-side comparison table<br>
            • Demand Validator — check if your idea has real market demand<br>
            • Pitch Slide Generator — auto-generate your investor competition slide<br>
            • Follow-up chat — ask questions about your competitors<br><br>
            Built with Python, Streamlit, LangChain, and Groq (Llama 3.3).
        </div>
    </div>
    """, unsafe_allow_html=True)

if st.session_state.show_contact:
    st.markdown("""
    <div class="card" style="margin-bottom:1.5rem;">
        <div class="card-label">Contact</div>
        <div class="card-content">
            📧 ishanmandalworks@gmail.com
        </div>
    </div>
    """, unsafe_allow_html=True)

# API key warning
if not is_valid_api_key(GROQ_API_KEY):
    st.markdown('<div class="warn-box">⚠️ Groq API key not set. Open app.py and replace <b>your_groq_key_here</b> with your real key from console.groq.com</div>', unsafe_allow_html=True)

tab1, tab2, tab3, tab4 = st.tabs(["🔍 Analyze & Chat", "🔥 Demand Validator", "📊 Pitch Slide", "🕘 History"])

with tab1:
    urls_input = st.text_area(
        "Competitor URLs (one per line)",
        placeholder="https://notion.so\nhttps://linear.app\nhttps://todoist.com",
        height=120
    )
    if st.button("Analyze Competitors →"):
        if not is_valid_api_key(GROQ_API_KEY):
            st.markdown('<div class="error-box">⚠️ Please set your Groq API key in app.py first.</div>', unsafe_allow_html=True)
        elif not urls_input.strip():
            st.markdown('<div class="error-box">⚠️ Please enter at least one URL.</div>', unsafe_allow_html=True)
        else:
            urls = [u.strip() for u in urls_input.strip().splitlines() if u.strip()]
            st.session_state.analyses = []
            st.session_state.chat_history = []
            st.session_state.pitch = None
            for url in urls:
                url = normalize_url(url)  # FIX 4: auto-add https://
                # Check if it looks like a real URL
                if "." not in url or len(url) < 8:
                    st.markdown(f'<div class="error-box">⚠️ "{url}" does not look like a valid website URL. Try something like https://notion.so</div>', unsafe_allow_html=True)
                    continue
                with st.spinner(f"Analyzing {url}..."):
                    content = scrape_website(url)
                    if content.startswith("ERROR"):
                        st.markdown(f'<div class="error-box">⚠️ Could not reach <b>{url}</b> — {content.replace("ERROR: ", "")}</div>', unsafe_allow_html=True)
                        continue
                    data = analyze(content)
                if data and "_error" not in data:
                    st.session_state.analyses.append({"url": url, "data": data})
                    save_to_history(url, data)
                elif data and "_error" in data:
                    st.markdown(f'<div class="error-box">⚠️ {data["_error"]}</div>', unsafe_allow_html=True)

    if st.session_state.analyses:
        for a in st.session_state.analyses:
            st.markdown('<hr class="divider">', unsafe_allow_html=True)
            render_result(a["url"], a["data"])
        if len(st.session_state.analyses) > 1:
            render_comparison_table(st.session_state.analyses)

        st.markdown('<hr class="divider">', unsafe_allow_html=True)
        st.markdown('<div class="card-label" style="font-size:0.8rem; margin-bottom:1rem;">💬 ASK A FOLLOW-UP QUESTION</div>', unsafe_allow_html=True)

        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                st.markdown(f'<div class="chat-msg-user">🧑 {msg["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-msg-ai">🤖 {msg["content"]}</div>', unsafe_allow_html=True)

        question = st.text_input("Your question", placeholder="Which competitor has the weakest pricing? Who should I worry about most?")
        if st.button("Ask →"):
            if len(question.strip()) < 5:
                st.markdown('<div class="warn-box">⚠️ Please type a proper question.</div>', unsafe_allow_html=True)
            else:
                with st.spinner("Thinking..."):
                    answer = ask_followup(question, st.session_state.analyses)
                st.session_state.chat_history.append({"role": "user", "content": question})
                st.session_state.chat_history.append({"role": "ai", "content": answer})
                st.rerun()

with tab2:
    st.markdown('<div style="color:#5a5a52; font-size:0.8rem; margin-bottom:1.5rem;">TYPE YOUR STARTUP IDEA AND WE\'LL TELL YOU IF THERE\'S REAL DEMAND BEFORE YOU BUILD.</div>', unsafe_allow_html=True)
    idea_input = st.text_area(
        "Your startup idea",
        placeholder="e.g. An AI tool that helps teachers create quiz questions automatically from their lecture notes.",
        height=100
    )
    if st.button("Validate Demand →"):
        if not is_valid_api_key(GROQ_API_KEY):
            st.markdown('<div class="error-box">⚠️ Please set your Groq API key in app.py first.</div>', unsafe_allow_html=True)
        elif len(idea_input.strip()) < 10:
            # FIX 9 in action: reject too short or vague ideas
            st.markdown('<div class="warn-box">⚠️ Please describe your idea in more detail — at least a sentence.</div>', unsafe_allow_html=True)
        else:
            with st.spinner("Analyzing market demand..."):
                st.session_state.demand = validate_demand(idea_input)
    if st.session_state.demand:
        st.markdown('<hr class="divider">', unsafe_allow_html=True)
        render_demand(st.session_state.demand)

with tab3:
    startup_desc = st.text_area(
        "Describe your startup",
        placeholder="e.g. We are building an AI tool that helps solo founders automate competitor research and generate pitch decks in seconds.",
        height=100
    )
    if st.session_state.analyses:
        st.markdown('<div style="color:#5a5a52; font-size:0.8rem; margin-bottom:0.5rem;">✓ Using competitor data from your analysis</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="color:#5a5a52; font-size:0.8rem; margin-bottom:0.5rem;">Tip: Run a competitor analysis first for a more accurate slide — or generate directly below.</div>', unsafe_allow_html=True)
    if st.button("Generate Pitch Slide →"):
        if len(startup_desc.strip()) < 10:
            st.markdown('<div class="warn-box">⚠️ Please describe your startup in more detail.</div>', unsafe_allow_html=True)
        else:
            with st.spinner("Generating your investor pitch slide..."):
                st.session_state.pitch = generate_pitch_slide(st.session_state.analyses, startup_desc)
    if st.session_state.pitch:
        st.markdown('<hr class="divider">', unsafe_allow_html=True)
        render_pitch_slide(st.session_state.pitch)

with tab4:
    history = st.session_state.history
    if not history:
        st.markdown('<div style="color:#5a5a52; margin-top:1rem;">No analyses yet in this session. Run your first one!</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div style="color:#5a5a52; font-size:0.8rem; margin-bottom:1rem;">LAST {len(history)} ANALYSES THIS SESSION</div>', unsafe_allow_html=True)
        for item in history:
            with st.expander(f"🔗 {item['url']}  ·  {item['time']}"):
                render_result(item["url"], item["data"])
