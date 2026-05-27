import streamlit as st
import anthropic
import feedparser
from datetime import datetime

st.set_page_config(page_title="FOREX TRADER BOT", page_icon="💹", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&family=VT323:wght@400&display=swap');

* { image-rendering: pixelated; }
html, body, [class*="css"] {
    font-family: 'VT323', monospace;
    background-color: #1a1a2e;
    color: #e0e0e0;
}
.stApp { background-color: #1a1a2e; }

.pixel-box {
    border: 3px solid #4a9eff;
    box-shadow: 4px 4px 0px #1a4a7a;
    background: #16213e;
    padding: 12px;
    margin-bottom: 12px;
    position: relative;
}
.title-bar {
    font-family: 'Press Start 2P', monospace;
    font-size: 9px;
    background: #4a9eff;
    color: #000;
    padding: 5px 10px;
    margin: -12px -12px 10px -12px;
    letter-spacing: 0.05em;
}
.pixel-green  { color: #00ff41; text-shadow: 0 0 8px #00ff41; }
.pixel-red    { color: #ff3131; text-shadow: 0 0 8px #ff3131; }
.pixel-yellow { color: #ffd700; text-shadow: 0 0 8px #ffd700; }
.pixel-blue   { color: #4a9eff; }

.agent-box {
    border: 2px solid #333;
    background: #0d0d1a;
    padding: 6px 8px;
    margin: 3px 0;
    font-size: 15px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.agent-box.active { border-color: #00ff41; box-shadow: 0 0 6px #00ff41; }

.blink { animation: blink 1s step-start infinite; }
@keyframes blink { 50% { opacity: 0; } }

.scanline {
    background: repeating-linear-gradient(0deg,transparent,transparent 2px,rgba(0,0,0,0.06) 2px,rgba(0,0,0,0.06) 4px);
    pointer-events: none;
    position: fixed;
    top:0;left:0;width:100%;height:100%;
    z-index: 9999;
}

.news-item {
    border-left: 3px solid #4a9eff;
    padding: 4px 8px;
    margin: 4px 0;
    font-size: 14px;
    color: #aaa;
    background: #0d0d1a;
}

.signal-row {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 6px 0;
    border-bottom: 1px dashed #333;
    font-size: 16px;
}

.badge {
    font-family: 'Press Start 2P', monospace;
    font-size: 7px;
    padding: 3px 6px;
    border: 2px solid;
}
.badge-bull { color:#00ff41; border-color:#00ff41; background:#001a00; }
.badge-bear { color:#ff3131; border-color:#ff3131; background:#1a0000; }
.badge-neut { color:#ffd700; border-color:#ffd700; background:#1a1400; }

.console-line { font-size:14px; color:#00ff41; padding:2px 0; }
.console-line.err  { color:#ff3131; }
.console-line.warn { color:#ffd700; }

.stButton > button {
    font-family: 'Press Start 2P', monospace !important;
    font-size: 8px !important;
    background: #4a9eff !important;
    color: #000 !important;
    border: none !important;
    border-radius: 0 !important;
    box-shadow: 4px 4px 0px #1a4a7a !important;
    width: 100% !important;
    padding: 12px !important;
}
.stButton > button:hover {
    transform: translate(2px,2px);
    box-shadow: 2px 2px 0 #1a4a7a !important;
    background: #6ab4ff !important;
}

[data-testid="stTextInput"] input {
    background: #0d0d1a !important;
    border: 2px solid #4a9eff !important;
    border-radius: 0 !important;
    color: #e0e0e0 !important;
    font-family: 'VT323', monospace !important;
    font-size: 18px !important;
}
[data-testid="stSidebar"] {
    background: #0d0d1a !important;
    border-right: 3px solid #4a9eff;
}
</style>
<div class="scanline"></div>
""", unsafe_allow_html=True)

# HEADER
st.markdown(f"""
<div style="font-family:'Press Start 2P',monospace;font-size:11px;
     background:#000;border:3px solid #4a9eff;padding:12px 18px;
     box-shadow:6px 6px 0 #1a4a7a;margin-bottom:16px;
     display:flex;justify-content:space-between;align-items:center;">
  <span style="color:#4a9eff">💹 FOREX TRADER BOT</span>
  <span style="font-size:7px;color:#ffd700">VER 1.0 · CLAUDE AI</span>
  <span style="font-size:8px;color:#00ff41">● ONLINE &nbsp; {datetime.now().strftime('%H:%M')}</span>
</div>
""", unsafe_allow_html=True)

# SIDEBAR
with st.sidebar:
    st.markdown('<div style="font-family:\'Press Start 2P\',monospace;font-size:8px;color:#4a9eff;margin-bottom:12px;">⚙ CONFIG</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-family:\'VT323\',monospace;font-size:18px;color:#ffd700;">🔑 API KEY</div>', unsafe_allow_html=True)
    import os
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if api_key:
        st.markdown('<div style="font-family:\'VT323\',monospace;font-size:16px;color:#00ff41">✓ KEY LOADED</div>', unsafe_allow_html=True)
    else:
        api_key = st.text_input("", type="password", placeholder="sk-ant-...", label_visibility="collapsed")
    st.markdown("---")
    st.markdown('<div style="font-family:\'VT323\',monospace;font-size:18px;color:#ffd700;">💱 PAIRS</div>', unsafe_allow_html=True)
    selected_pairs = st.multiselect("",
        ["EUR/USD","USD/THB","GBP/USD","USD/JPY","XAU/USD","AUD/USD"],
        default=["EUR/USD","USD/THB","USD/JPY"],
        label_visibility="collapsed")
    st.markdown("---")
    st.markdown('<div style="font-family:\'VT323\',monospace;font-size:18px;color:#ffd700;">📡 SOURCE</div>', unsafe_allow_html=True)
    use_reuters   = st.checkbox("Reuters",       value=True)
    use_investing = st.checkbox("Investing.com", value=True)
    st.markdown("---")
    st.markdown("""
    <div style="font-family:'Press Start 2P',monospace;font-size:7px;color:#4a9eff;margin-bottom:8px;">AI AGENTS</div>
    <div class="agent-box active">🤖 <span style="color:#00ff41">News Agent</span><span style="margin-left:auto;font-size:12px;color:#555">READY</span></div>
    <div class="agent-box active">🧠 <span style="color:#00ff41">Analysis Agent</span><span style="margin-left:auto;font-size:12px;color:#555">READY</span></div>
    <div class="agent-box">⚡ <span style="color:#888">Signal Agent</span><span style="margin-left:auto;font-size:12px;color:#555">IDLE</span></div>
    <br>
    """, unsafe_allow_html=True)
    run_btn = st.button("▶  ANALYZE NOW")

RSS = {}
if use_reuters:   RSS["Reuters"]       = "https://feeds.reuters.com/reuters/businessNews"
if use_investing: RSS["Investing.com"] = "https://www.investing.com/rss/news_25.rss"

def fetch_news():
    articles = []
    for src, url in RSS.items():
        try:
            feed = feedparser.parse(url)
            for e in feed.entries[:8]:
                articles.append({"source":src,"title":e.get("title",""),"summary":e.get("summary","")[:300]})
        except: pass
    return articles

def analyze(articles, pairs, key):
    client = anthropic.Anthropic(api_key=key)
    news_text = "\n\n".join(f"[{a['source']}] {a['title']}\n{a['summary']}" for a in articles)
    prompt = f"""คุณคือนักวิเคราะห์ Forex วิเคราะห์ข่าวและสรุปผลกระทบต่อ: {", ".join(pairs)}
ข่าว:\n{news_text}
ตอบในรูปแบบ (ภาษาไทย):
OVERVIEW: <สรุป 2-3 ประโยค>
PAIRS:
{chr(10).join(f"{p}: <BULLISH/BEARISH/NEUTRAL> | <เหตุผล 1 ประโยค>" for p in pairs)}
WATCH: <ข่าวที่ต้องติดตาม>"""
    r = client.messages.create(model="claude-opus-4-5", max_tokens=800,
        messages=[{"role":"user","content":prompt}])
    return r.content[0].text

def parse_result(text, pairs):
    overview, signals, watch, section = "", {}, "", ""
    for line in text.strip().split("\n"):
        if   line.startswith("OVERVIEW:"): overview = line.replace("OVERVIEW:","").strip()
        elif line.startswith("WATCH:"):    watch    = line.replace("WATCH:","").strip()
        elif line.startswith("PAIRS:"):    section  = "pairs"
        elif section=="pairs" and "|" in line:
            for p in pairs:
                if p in line:
                    parts = line.split("|")
                    sig   = parts[0].split(":")[-1].strip().upper()
                    reason= parts[1].strip() if len(parts)>1 else ""
                    if   "BULLISH" in sig: signals[p]=("BULLISH",reason)
                    elif "BEARISH" in sig: signals[p]=("BEARISH",reason)
                    else:                  signals[p]=("NEUTRAL",reason)
    return overview, signals, watch

# IDLE SCREEN
if not run_btn:
    c1,c2,c3 = st.columns(3)
    with c1:
        st.markdown("""
        <div class="pixel-box">
        <div class="title-bar">📊 MARKET STATUS</div>
        <div class="signal-row"><span class="pixel-blue" style="font-family:'Press Start 2P',monospace;font-size:8px">EUR/USD</span><span class="badge badge-neut">◆ NEUTRAL</span></div>
        <div class="signal-row"><span class="pixel-blue" style="font-family:'Press Start 2P',monospace;font-size:8px">USD/THB</span><span class="badge badge-neut">◆ NEUTRAL</span></div>
        <div class="signal-row"><span class="pixel-blue" style="font-family:'Press Start 2P',monospace;font-size:8px">USD/JPY</span><span class="badge badge-neut">◆ NEUTRAL</span></div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="pixel-box" style="text-align:center">
        <div class="title-bar">🕐 SYSTEM CLOCK</div>
        <div style="font-family:'Press Start 2P',monospace;font-size:14px;color:#00ff41;padding:10px 0">
          {datetime.now().strftime('%H:%M:%S')}
        </div>
        <div style="font-family:'Press Start 2P',monospace;font-size:7px;color:#555">
          {datetime.now().strftime('%d / %m / %Y')}
        </div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown("""
        <div class="pixel-box">
        <div class="title-bar">💾 SYSTEM LOG</div>
        <div class="console-line">> BOOT COMPLETE</div>
        <div class="console-line">> AGENTS LOADED</div>
        <div class="console-line warn">> AWAITING INPUT...</div>
        <div class="console-line blink">█</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align:center;padding:50px;font-family:'Press Start 2P',monospace;font-size:8px;color:#333;letter-spacing:0.1em">
      INSERT API KEY AND PRESS ANALYZE NOW
    </div>""", unsafe_allow_html=True)

# RUNNING
else:
    if not api_key:
        st.markdown('<div class="pixel-box"><div class="title-bar">❌ ERROR</div><div class="console-line err">> NO API KEY DETECTED</div></div>', unsafe_allow_html=True)
    elif not selected_pairs:
        st.markdown('<div class="pixel-box"><div class="title-bar">❌ ERROR</div><div class="console-line err">> NO PAIRS SELECTED</div></div>', unsafe_allow_html=True)
    else:
        cl, cr = st.columns([3,2])
        with cl:
            log = st.empty()
            log.markdown("""<div class="pixel-box"><div class="title-bar">💾 CONSOLE</div>
            <div class="console-line">> FETCHING NEWS FEED...</div>
            <div class="console-line blink">█</div></div>""", unsafe_allow_html=True)

            articles = fetch_news()

            log.markdown(f"""<div class="pixel-box"><div class="title-bar">💾 CONSOLE</div>
            <div class="console-line">> NEWS: {len(articles)} ITEMS LOADED ✓</div>
            <div class="console-line warn">> CLAUDE AI ANALYZING...</div>
            <div class="console-line blink">█</div></div>""", unsafe_allow_html=True)

            if not articles:
                st.markdown('<div class="console-line err">> ERROR: FEED UNAVAILABLE</div>', unsafe_allow_html=True)
            else:
                raw = analyze(articles, selected_pairs, api_key)
                overview, signals, watch = parse_result(raw, selected_pairs)

                log.markdown(f"""<div class="pixel-box"><div class="title-bar">💾 CONSOLE</div>
                <div class="console-line">> NEWS: {len(articles)} ITEMS ✓</div>
                <div class="console-line">> AI ANALYSIS: DONE ✓</div>
                <div class="console-line">> SIGNALS READY ✓</div></div>""", unsafe_allow_html=True)

                st.markdown(f"""
                <div class="pixel-box">
                <div class="title-bar">📋 MARKET OVERVIEW</div>
                <div style="font-size:17px;line-height:1.7;color:#ccc">{overview}</div>
                </div>""", unsafe_allow_html=True)

                sh = '<div class="pixel-box"><div class="title-bar">📡 SIGNAL BOARD</div>'
                for p in selected_pairs:
                    sig, reason = signals.get(p,("NEUTRAL","ไม่มีข้อมูล"))
                    if   sig=="BULLISH": badge='<span class="badge badge-bull">▲ BULLISH</span>'; c="#00ff41"
                    elif sig=="BEARISH": badge='<span class="badge badge-bear">▼ BEARISH</span>'; c="#ff3131"
                    else:                badge='<span class="badge badge-neut">◆ NEUTRAL</span>'; c="#ffd700"
                    sh += f'<div class="signal-row"><span style="font-family:\'Press Start 2P\',monospace;font-size:8px;color:{c};min-width:90px">{p}</span>{badge}<span style="color:#888;font-size:15px">{reason}</span></div>'
                sh += "</div>"
                st.markdown(sh, unsafe_allow_html=True)

                if watch:
                    st.markdown(f"""
                    <div class="pixel-box">
                    <div class="title-bar">⚠ WATCH LIST</div>
                    <div style="font-size:16px;color:#ffd700">{watch}</div>
                    </div>""", unsafe_allow_html=True)

                st.markdown("""
                <div style="border:2px dashed #ff3131;padding:8px 12px;
                font-family:'Press Start 2P',monospace;font-size:7px;color:#ff3131;margin-top:8px">
                ⚠ NOT FINANCIAL ADVICE · FOR EDUCATIONAL PURPOSES ONLY
                </div>""", unsafe_allow_html=True)

        with cr:
            nh = '<div class="pixel-box"><div class="title-bar">📰 LIVE NEWS FEED</div>'
            for a in articles[:10]:
                sc = "#4a9eff" if a['source']=="Reuters" else "#ff9f43"
                nh += f'<div class="news-item"><span style="font-size:11px;color:{sc}">[{a["source"]}]</span><br>{a["title"]}</div>'
            nh += "</div>"
            st.markdown(nh, unsafe_allow_html=True)

            st.markdown(f"""
            <div class="pixel-box" style="text-align:center">
            <div class="title-bar">🕐 UPDATED</div>
            <div style="font-family:'Press Start 2P',monospace;font-size:10px;color:#00ff41">
              {datetime.now().strftime('%H:%M:%S')}
            </div>
            </div>""", unsafe_allow_html=True)
