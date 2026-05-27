import streamlit as st
import anthropic
import feedparser
import os
from datetime import datetime

# --- CONFIG ---
st.set_page_config(page_title="FOREX TRADING OFFICE", page_icon="💹", layout="wide")

# CSS สวยงาม
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');
.stApp {background:#1a1a2e; color:#e0e0e0; font-family:'Press Start 2P',monospace;}
.stButton>button {background:#4a9eff!important; color:#000!important; width:100%!important; font-family:'Press Start 2P',monospace!important;}
</style>
""", unsafe_allow_html=True)

# --- FUNCTIONS ---
def analyze(articles, pairs, key):
    client = anthropic.Anthropic(api_key=key)
    news_text = "\n\n".join(f"[{a['source']}] {a['title']}" for a in articles)
    prompt = f"วิเคราะห์ Forex สำหรับคู่ {', '.join(pairs)} จากข่าวเหล่านี้:\n{news_text}\nตอบแบบ JSON: {{'overview': '...', 'signals': {{'คู่เงิน': 'BULLISH/BEARISH/NEUTRAL', 'reason': '...'}}, 'watch': '...'}}"
    
    # ใช้โมเดลที่ถูกต้อง
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text

# --- UI ---
st.title("💹 FOREX TRADING OFFICE")
api_key = st.sidebar.text_input("Enter Anthropic API Key", type="password")
pairs = st.sidebar.multiselect("Select Pairs", ["EUR/USD", "USD/THB", "USD/JPY", "GBP/USD", "XAU/USD"], default=["EUR/USD"])

if st.sidebar.button("▶ ANALYZE NOW"):
    if not api_key:
        st.error("กรุณากรอก API Key ใน Sidebar")
    else:
        try:
            with st.spinner("Analyzing market..."):
                # สมมติสถานะเริ่มต้น
                articles = [{"source": "Test", "title": "Market is volatile"}] # แทนที่ด้วย fetch_news()
                result = analyze(articles, pairs, api_key)
                st.json(result)
                st.success("วิเคราะห์เสร็จสิ้น")
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาดในการเชื่อมต่อ API: {e}")
            st.write("ตรวจสอบให้แน่ใจว่า API Key ของคุณถูกต้องและยังมี Credits")

else:
    st.write("พร้อมใช้งานแล้ว... กรุณากดปุ่ม Analyze Now")
