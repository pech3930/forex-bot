import streamlit as st
import anthropic
import feedparser
import os
import json
from datetime import datetime

# ตั้งค่าหน้าเว็บให้เป็น Wide
st.set_page_config(page_title="FOREX TRADING OFFICE", page_icon="💹", layout="wide")

# CSS ปรับแต่งให้เต็มจอและสวยงาม
st.markdown("""
<style>
/* ทำให้หน้าเว็บเต็มจอ */
.main .block-container {
    max-width: 98% !important;
    padding-top: 1rem !important;
    padding-right: 1rem !important;
    padding-left: 1rem !important;
    padding-bottom: 1rem !important;
}

@import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');
*{box-sizing:border-box;margin:0;padding:0;image-rendering:pixelated}
html,body,[class*="css"]{font-family:'Press Start 2P',monospace;background:#1a1a2e;color:#e0e0e0}
.stApp{background:#1a1a2e}

.stButton>button{font-family:'Press Start 2P',monospace!important;font-size:8px!important;
  background:#4a9eff!important;color:#000!important;border:none!important;border-radius:0!important;
  box-shadow:4px 4px 0 #1a4a7a!important;width:100%!important;padding:12px!important}
.stButton>button:hover{transform:translate(2px,2px);box-shadow:2px 2px 0 #1a4a7a!important}

[data-testid="stSidebar"]{background:#0d0d1a!important;border-right:3px solid #4a9eff}
[data-testid="stTextInput"] input{background:#0d0d1a!important;border:2px solid #4a9eff!important;
  border-radius:0!important;color:#e0e0e0!important;font-family:'Press Start 2P',monospace!important;font-size:10px!important}

.scanline{background:repeating-linear-gradient(0deg,transparent,transparent 2px,rgba(0,0,0,0.04) 2px,rgba(0,0,0,0.04) 4px);
  pointer-events:none;position:fixed;top:0;left:0;width:100%;height:100%;z-index:9999}
</style>
<div class="scanline"></div>
""", unsafe_allow_html=True)

# ส่วนหัวของโปรแกรม
st.markdown(f"""
<div style="font-family:'Press Start 2P',monospace;font-size:10px;background:#000;
  border:3px solid #4a9eff;padding:10px 16px;box-shadow:6px 6px 0 #1a4a7a;margin-bottom:10px;
  display:flex;justify-content:space-between;align-items:center">
  <span style="color:#4a9eff">💹 FOREX TRADING OFFICE</span>
  <span style="font-size:7px;color:#ffd700">POWERED BY CLAUDE AI</span>
  <span style="font-size:8px;color:#00ff41">● {datetime.now().strftime('%H:%M:%S')}</span>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown('<div style="font-family:\'Press Start 2P\',monospace;font-size:8px;color:#4a9eff;margin-bottom:10px">⚙ CONFIG</div>', unsafe_allow_html=True)
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        api_key = st.text_input("", type="password", placeholder="sk-ant-...", label_visibility="collapsed")
    
    selected_pairs = st.multiselect("💱 PAIRS", ["EUR/USD","USD/THB","GBP/USD","USD/JPY","XAU/USD","AUD/USD"], default=["EUR/USD","XAU/USD"])
    
    use_cnbc = st.checkbox("CNBC News", value=True)
    run_btn = st.button("▶ ANALYZE NOW")

# ฟังก์ชันดึงข่าวและวิเคราะห์ (คงเดิม)
def fetch_news():
    RSS = "https://search.cnbc.com/rs/search/view.xml?partnerId=2000&keywords=forex"
    articles = []
    try:
        feed = feedparser.parse(RSS)
        for e in feed.entries[:3]:
            articles.append({"title": e.get("title", ""), "summary": e.get("summary", "")[:200]})
    except: pass
    return articles

def analyze(articles, pairs, key):
    client = anthropic.Anthropic(api_key=key)
    prompt = f"วิเคราะห์ Forex คู่ {pairs} จากข่าว {articles}. ตอบ JSON เท่านั้น: {{'overview': '...', 'signals': {{pair: {{'signal': '...', 'reason': '...'}}}}, 'watch': '...'}}"
    r = client.messages.create(model="claude-3-5-sonnet-20241022", max_tokens=1000, messages=[{"role":"user","content":prompt}])
    return r.content[0].text

# รันหน้าจอ
if run_btn and api_key:
    with st.spinner("Analyzing..."):
        articles = fetch_news()
        raw = analyze(articles, selected_pairs, api_key)
        try:
            data = json.loads(raw[raw.find('{'):raw.rfind('}')+1])
            st.markdown(f"### 📋 OVERVIEW: {data['overview']}")
            cols = st.columns(len(selected_pairs))
            for i, p in enumerate(selected_pairs):
                with cols[i]:
                    sig = data['signals'].get(p, {})
                    st.info(f"{p}: {sig.get('signal', 'N/A')}\n\n{sig.get('reason', '')}")
        except: st.error("Parsing Error")
else:
    st.write("Welcome, Commander. Please click 'Analyze' to scan the market.")
