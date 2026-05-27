import streamlit as st
import anthropic
import json

# ตั้งค่าหน้าจอ
st.set_page_config(layout="wide")

# 1. ฟังก์ชัน Render Canvas (ที่สร้างตัวละคร)
def render_canvas(agents, sprite_url):
    agents_json = str(agents).replace("True", "true").replace("False", "false").replace("'", '"')
    return f"""
    <canvas id="fc" style="width:100%; height:500px; background:#1a1a2e; image-rendering:pixelated"></canvas>
    <script>
    const AGENTS = {agents_json};
    const cv = document.getElementById('fc');
    const ctx = cv.getContext('2d');
    ctx.fillStyle = '#00ff41';
    ctx.font = '20px monospace';
    ctx.fillText("SYSTEM READY: " + AGENTS.length + " AGENTS ACTIVE", 50, 50);
    // ใส่ Logic วาดห้องและตัวละครของคุณที่นี่...
    </script>
    """

# 2. ฟังก์ชันวิเคราะห์
def analyze(pairs, key):
    client = anthropic.Anthropic(api_key=key)
    prompt = f"วิเคราะห์คู่เงิน {', '.join(pairs)}. ตอบ JSON เท่านั้น: {{'signals': {{'EUR/USD': 'BULLISH'}}}}"
    r = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )
    return r.content[0].text

# 3. UI หลัก
st.markdown("## 💹 FOREX TRADING OFFICE")
api_key = st.sidebar.text_input("API Key", type="password")
pairs = st.sidebar.multiselect("Pairs", ["EUR/USD", "XAU/USD"], default=["EUR/USD"])

# เก็บสถานะไว้ใน Session State เพื่อให้ตัวละครไม่หาย
if 'agents' not in st.session_state:
    st.session_state.agents = [{"pair": "EUR/USD", "signal": "NEUTRAL"}]

if st.sidebar.button("▶ ANALYZE NOW"):
    try:
        raw = analyze(pairs, api_key)
        data = json.loads(raw[raw.find('{'):raw.rfind('}')+1])
        st.session_state.agents = [{"pair": p, "signal": data['signals'].get(p, "NEUTRAL")} for p in pairs]
        st.success("Updated!")
    except Exception as e:
        st.error(f"Error: {e}")

# แสดงผล Canvas เสมอ
html_code = render_canvas(st.session_state.agents, "")
st.components.v1.html(html_code, height=520)
