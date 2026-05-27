import streamlit as st
import anthropic
import feedparser
import os
import json
from datetime import datetime

# 1. การตั้งค่าหน้าจอ
st.set_page_config(page_title="FOREX TRADING OFFICE", page_icon="💹", layout="wide")

# 2. CSS สำหรับธีม Dark Ambient สไตล์ Console
st.markdown("""
<style>
/* พื้นหลังมืดไล่เฉดสี */
.stApp {
    background: radial-gradient(circle at center, #1b2735 0%, #090a0f 100%);
    background-attachment: fixed;
}

/* ฟอนต์และสีข้อความ */
@import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');
* {box-sizing:border-box; image-rendering:pixelated}
html, body, [class*="css"] {
    font-family: 'Press Start 2P', monospace;
    color: #e0e0e0;
}

/* กล่องเนื้อหาแบบ Glassmorphism */
[data-testid="stVerticalBlock"] {
    background: rgba(10, 15, 25, 0.7);
    border: 1px solid rgba(74, 158, 255, 0.3);
    padding: 20px;
    border-radius: 5px;
}

/* ปุ่มสไตล์นีออน */
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

/* Sidebar มืดสนิท */
[data-testid="stSidebar"] {
    background: rgba(0, 0, 0, 0.9) !important;
    border-right: 2px solid #4a9eff;
}

/* Scanline Effect */
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

# 3. ส่วนการทำงาน (Logic)
with st.sidebar:
    st.markdown('### ⚙ CONFIG')
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        api_key = st.text_input("🔑 API KEY", type="password")
    
    st.markdown('### 💱 PAIRS')
    selected_pairs = st.multiselect("", ["EUR/USD","USD/THB","GBP/USD","USD/JPY","XAU/USD"], default=["EUR/USD","XAU/USD"])
    
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
    prompt = f"วิเคราะห์ข่าว: {articles} ต่อคู่เงิน {pairs}. ตอบเป็น JSON format: {{'overview': '...', 'signals': {{'คู่เงิน': {{'signal': '...', 'reason': '...'}}}}, 'watch': '...'}}"
    
    # แก้ไขโมเดลให้ถูกต้อง
    r = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )
    return r.content[0].text

# 4. ส่วนการแสดงผล
if run_btn and api_key:
    with st.spinner("Analyzing Market..."):
        try:
            articles = fetch_news()
            raw_result = analyze(articles, selected_pairs, api_key)
            
            # ตัดเอาเฉพาะส่วนที่เป็น JSON
            json_text = raw_result[raw_result.find('{'):raw_result.rfind('}')+1]
            data = json.loads(json_text)
            
            st.markdown(f"### 📋 OVERVIEW\n{data['overview']}")
            
            for pair, info in data['signals'].items():
                st.info(f"**{pair}**: {info['signal']} - {info['reason']}")
            
            st.warning(f"**WATCH:** {data['watch']}")
        except Exception as e:
            st.error("Error processing request. Please check API Key.")
else:
    st.markdown("# 💹 FOREX TRADING OFFICE")
    st.write("Welcome, Commander. Please input your key and analyze the market.")
