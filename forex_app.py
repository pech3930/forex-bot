import streamlit as st
import anthropic
import feedparser
import os
import json
from datetime import datetime

st.set_page_config(page_title="FOREX TRADING OFFICE", page_icon="💹", layout="wide")

# (CSS คงเดิมไว้ที่ด้านบนสุดเหมือนเดิม)
st.markdown("""
<style>
.main .block-container { max-width: 95% !important; padding: 1rem !important; }
@import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');
</style>
""", unsafe_allow_html=True)

# ฟังก์ชันแสดงผล canvas
def display_canvas(agents, container):
    canvas_html = render_canvas(agents, "https://raw.githubusercontent.com/pech3930/forex-bot/main/Astronaut.png")
    container.components.v1.html(canvas_html, height=540, scrolling=False)

# ส่วนหลัก
container = st.container()

# Sidebar Config
with st.sidebar:
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        api_key = st.text_input("🔑 API KEY", type="password")
    
    selected_pairs = st.multiselect("💱 PAIRS", ["EUR/USD","USD/THB","GBP/USD","USD/JPY","XAU/USD"], default=["EUR/USD","XAU/USD"])
    run_btn = st.button("▶ ANALYZE NOW")

# โลจิกการทำงาน
if run_btn:
    if not api_key:
        st.error("กรุณาใส่ API KEY")
    else:
        # 1. แสดงสถานะกำลังทำงาน
        status = container.empty()
        status.info("กำลังวิเคราะห์ตลาด...")
        
        # 2. ทำการดึงข่าวและวิเคราะห์
        try:
            articles = fetch_news()
            raw_data = analyze(articles, selected_pairs, api_key)
            overview, signals, watch = parse_result(raw_data, selected_pairs)
            
            # 3. แสดงผลหน้าห้อง
            final_agents = build_agents(selected_pairs, signals)
            display_canvas(final_agents, container)
            
            # 4. แสดงผลลัพธ์ข้อความ
            st.success("วิเคราะห์เสร็จสิ้น!")
            st.write(f"**Overview:** {overview}")
        except Exception as e:
            st.error(f"เกิดข้อผิดพลาด: {str(e)}")
else:
    # หน้าแรกปกติ
    default_agents = build_agents(["EUR/USD", "XAU/USD"], {})
    display_canvas(default_agents, container)
