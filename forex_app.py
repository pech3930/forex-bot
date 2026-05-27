import streamlit as st
import anthropic
import feedparser
import os
import json
from datetime import datetime

st.set_page_config(page_title="FOREX TRADING OFFICE", page_icon="💹", layout="wide")

st.markdown("""
<style>
/* 1. พื้นหลังแบบ Dark Ambient ให้ความรู้สึกเหมือนหน้าจอคอนโซล */
.stApp {
    background: radial-gradient(circle at center, #1b2735 0%, #090a0f 100%);
    background-attachment: fixed;
}

/* 2. ตั้งค่าฟอนต์ */
@import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');
* {box-sizing:border-box; image-rendering:pixelated}
html, body, [class*="css"] {
    font-family: 'Press Start 2P', monospace;
    color: #e0e0e0;
}

/* 3. กล่องข้อมูลแบบ Glassmorphism */
[data-testid="stVerticalBlock"] {
    background: rgba(10, 15, 25, 0.7);
    border: 1px solid rgba(74, 158, 255, 0.3);
    padding: 20px;
    border-radius: 5px;
}

/* 4. สไตล์ปุ่มกด */
.stButton>button {
    font-family: 'Press Start 2P', monospace !important;
    background: linear-gradient(90deg, #4a9eff, #1a4a7a) !important;
    color: white !important;
    border: none !important;
    padding: 15px !important;
    transition: 0.3s;
}
.stButton>button:hover {
    background: #00ff41 !important;
    box-shadow: 0 0 15px #00ff41;
}

/* 5. สไตล์ Sidebar */
[data-testid="stSidebar"] {
    background: rgba(0, 0, 0, 0.9) !important;
    border-right: 2px solid #4a9eff;
}

/* 6. Scanline Effect */
.scanline {
    background: linear-gradient(to bottom, rgba(200,200,200,0) 50%, rgba(0,0,0,0.1) 50%);
    background-size: 100% 4px;
    pointer-events: none;
    position: fixed;
    top: 0; left: 0; width: 100%; height: 100%;
    z-index: 9999;
}
</style>
<div class="scanline"></div>
""", unsafe_allow_html=True)

# --- ส่วนการทำงาน ---

with st.sidebar:
    st.markdown('### ⚙ CONFIG')
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        api_key = st.text_input("🔑 ANTHROPIC API KEY", type="password")
    
    st.markdown('### 💱 PAIRS')
    selected_pairs = st.multiselect("", ["EUR/USD","USD/THB","GBP/USD","USD/JPY","XAU/USD"], default=["EUR/USD","XAU/USD"])
    
    st.markdown('### 📡 SOURCES')
    use_cnbc = st.checkbox("CNBC News", value=True)
    run_btn = st.button("▶ ANALYZE NOW")

def fetch_news():
    RSS = "https://search.cnbc.com/rs/search/view.xml?partnerId=2000&keywords=forex"
    articles = []
    try:
        feed = feedparser.parse(RSS)
        for e in feed.entries[:5]:
            articles.append({"title": e.get("title", ""), "summary": e.get("summary", "")[:200]})
    except: pass
    return articles

def analyze(articles, pairs, key):
    client = anthropic.Anthropic(api_key=key)
    prompt = f"วิเคราะห์ข่าว: {articles} ต่อคู่เงิน {pairs} ตอบเป็น JSON เท่านั้น {'overview':..., 'signals':{คู่เงิน: {'signal':'BULLISH/BEARISH', 'reason':...}}, 'watch':...}"
    
    # แก้ไขชื่อโมเดลเป็นรุ่นล่าสุดที่ถูกต้อง
    r = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )
    return r.content[0].text

# --- การเรนเดอร์หน้าจอ ---
if run_btn and api_key:
    with st.spinner("Analyzing Market..."):
        articles = fetch_news()
        raw_result = analyze(articles, selected_pairs, api_key)
        
        # จัดการข้อมูล JSON
        try:
            data = json.loads(raw_result[raw_result.find('{'):raw_result.rfind('}')+1])
            st.success("Analysis Complete!")
            st.write(f"**Overview:** {data['overview']}")
            
            for pair, info in data['signals'].items():
                st.info(f"{pair}: {info['signal']} - {info['reason']}")
        except:
            st.error("Error parsing AI response. Please try again.")
else:
    st.markdown("# 💹 FOREX TRADING OFFICE")
    st.write("Welcome back, Commander. Please configure your settings and hit 'Analyze' to begin.")