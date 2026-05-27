import streamlit as st
import anthropic
import feedparser
from datetime import datetime

# ============================================================
# ตั้งค่าหน้าตา
# ============================================================
st.set_page_config(
    page_title="Forex News Bot",
    page_icon="💱",
    layout="wide",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=Sarabun:wght@300;400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Sarabun', sans-serif;
}
.stApp {
    background: #0a0e17;
    color: #c8d4e8;
}
.header-box {
    background: #0d1220;
    border: 1px solid #1e2d45;
    border-radius: 10px;
    padding: 20px 28px;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    gap: 16px;
}
.title-text {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 22px;
    font-weight: 600;
    color: #7dd3fc;
    margin: 0;
}
.subtitle-text {
    font-size: 13px;
    color: #4a7fa5;
    margin: 0;
}
.card {
    background: #111827;
    border: 1px solid #1e2d45;
    border-radius: 10px;
    padding: 20px;
    margin-bottom: 14px;
}
.pair-badge {
    display: inline-block;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 12px;
    font-weight: 600;
    padding: 3px 10px;
    border-radius: 4px;
    margin-right: 8px;
}
.bullish  { background: #0d2e1e; color: #34d399; border: 1px solid #1a4a30; }
.bearish  { background: #2d1a1a; color: #f87171; border: 1px solid #4a2020; }
.neutral  { background: #2a2410; color: #fbbf24; border: 1px solid #4a3e18; }
.signal-row {
    display: flex;
    align-items: center;
    padding: 10px 0;
    border-bottom: 1px solid #1e2d45;
    font-size: 14px;
    gap: 12px;
}
.signal-row:last-child { border-bottom: none; }
.section-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 10px;
    letter-spacing: 0.12em;
    color: #2e4a6a;
    margin-bottom: 8px;
}
.stButton > button {
    background: #1e3a5a;
    color: #7dd3fc;
    border: 1px solid #2e5a8a;
    border-radius: 6px;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 13px;
    padding: 10px 28px;
    width: 100%;
    transition: all 0.15s;
}
.stButton > button:hover {
    background: #2e4a7a;
    border-color: #3b82f6;
}
[data-testid="stSelectbox"] > div,
[data-testid="stMultiSelect"] > div {
    background: #111827;
    border-color: #1e2d45;
}
.stTextInput > div > input {
    background: #111827;
    color: #c8d4e8;
    border-color: #1e2d45;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 13px;
}
.warning-box {
    background: #2a1e0a;
    border: 1px solid #4a3010;
    border-radius: 8px;
    padding: 10px 16px;
    font-size: 12px;
    color: #fbbf24;
    margin-top: 16px;
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# Header
# ============================================================
st.markdown("""
<div class="header-box">
  <div>
    <p class="title-text">💱 FOREX NEWS BOT</p>
    <p class="subtitle-text">วิเคราะห์ข่าวค่าเงินด้วย Claude AI · ไม่ใช่คำแนะนำการลงทุน</p>
  </div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# Sidebar — ตั้งค่า
# ============================================================
with st.sidebar:
    st.markdown('<p class="section-label">🔑 API KEY</p>', unsafe_allow_html=True)
    api_key = st.text_input("Anthropic API Key", type="password", placeholder="sk-ant-...")

    st.markdown("---")
    st.markdown('<p class="section-label">💱 คู่สกุลเงินที่สนใจ</p>', unsafe_allow_html=True)
    selected_pairs = st.multiselect(
        "เลือกคู่",
        ["EUR/USD", "USD/THB", "GBP/USD", "USD/JPY", "XAU/USD", "AUD/USD"],
        default=["EUR/USD", "USD/THB", "USD/JPY"],
    )

    st.markdown("---")
    st.markdown('<p class="section-label">📡 แหล่งข่าว</p>', unsafe_allow_html=True)
    use_reuters = st.checkbox("Reuters", value=True)
    use_investing = st.checkbox("Investing.com", value=True)

    st.markdown("---")
    run_btn = st.button("⚡ วิเคราะห์ตอนนี้")

# ============================================================
# RSS_FEEDS
# ============================================================
RSS_FEEDS = {}
if use_reuters:
    RSS_FEEDS["Reuters"] = "https://feeds.reuters.com/reuters/businessNews"
if use_investing:
    RSS_FEEDS["Investing.com"] = "https://www.investing.com/rss/news_25.rss"

# ============================================================
# ฟังก์ชัน
# ============================================================
def fetch_news():
    articles = []
    for source, url in RSS_FEEDS.items():
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:8]:
                articles.append({
                    "source":  source,
                    "title":   entry.get("title", ""),
                    "summary": entry.get("summary", "")[:300],
                    "link":    entry.get("link", ""),
                })
        except:
            pass
    return articles

def analyze(articles, pairs, key):
    client = anthropic.Anthropic(api_key=key)
    news_text = "\n\n".join(f"[{a['source']}] {a['title']}\n{a['summary']}" for a in articles)
    prompt = f"""คุณคือนักวิเคราะห์ Forex
วิเคราะห์ข่าวและสรุปผลกระทบต่อ: {", ".join(pairs)}

ข่าว:
{news_text}

ตอบในรูปแบบนี้ (ใช้ภาษาไทย):
OVERVIEW: <สรุปภาพรวม 2-3 ประโยค>

PAIRS:
{chr(10).join(f"{p}: <BULLISH/BEARISH/NEUTRAL> | <เหตุผลสั้น 1 ประโยค>" for p in pairs)}

WATCH: <ข่าวที่ต้องติดตาม>"""

    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=800,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text

def parse_result(text, pairs):
    lines = text.strip().split("\n")
    overview, pair_signals, watch = "", {}, ""
    section = ""
    for line in lines:
        if line.startswith("OVERVIEW:"):
            overview = line.replace("OVERVIEW:", "").strip()
        elif line.startswith("WATCH:"):
            watch = line.replace("WATCH:", "").strip()
        elif line.startswith("PAIRS:"):
            section = "pairs"
        elif section == "pairs" and "|" in line:
            for p in pairs:
                if p in line:
                    parts = line.split("|")
                    signal_part = parts[0].split(":")[-1].strip()
                    reason = parts[1].strip() if len(parts) > 1 else ""
                    if "BULLISH" in signal_part.upper():
                        pair_signals[p] = ("BULLISH", reason)
                    elif "BEARISH" in signal_part.upper():
                        pair_signals[p] = ("BEARISH", reason)
                    else:
                        pair_signals[p] = ("NEUTRAL", reason)
    return overview, pair_signals, watch

# ============================================================
# Main — แสดงผล
# ============================================================
if run_btn:
    if not api_key:
        st.error("กรุณาใส่ Anthropic API Key ในแถบซ้าย")
    elif not selected_pairs:
        st.error("กรุณาเลือกคู่สกุลเงินอย่างน้อย 1 คู่")
    elif not RSS_FEEDS:
        st.error("กรุณาเลือกแหล่งข่าวอย่างน้อย 1 แหล่ง")
    else:
        col1, col2 = st.columns([3, 2])

        with col1:
            with st.spinner("📡 กำลังดึงข่าว..."):
                articles = fetch_news()

            if not articles:
                st.error("❌ ดึงข่าวไม่ได้ ลองใหม่อีกครั้ง")
            else:
                with st.spinner(f"🧠 Claude กำลังวิเคราะห์ {len(articles)} ข่าว..."):
                    raw = analyze(articles, selected_pairs, api_key)
                    overview, pair_signals, watch = parse_result(raw, selected_pairs)

                # ภาพรวม
                st.markdown('<p class="section-label">📊 สรุปภาพรวม</p>', unsafe_allow_html=True)
                st.markdown(f'<div class="card">{overview}</div>', unsafe_allow_html=True)

                # สัญญาณแต่ละคู่
                st.markdown('<p class="section-label">💱 ผลกระทบต่อแต่ละคู่</p>', unsafe_allow_html=True)
                cards_html = '<div class="card">'
                for p in selected_pairs:
                    sig, reason = pair_signals.get(p, ("NEUTRAL", "ไม่มีข้อมูล"))
                    cls = sig.lower()
                    arrow = "▲" if sig == "BULLISH" else ("▼" if sig == "BEARISH" else "◆")
                    cards_html += f"""
                    <div class="signal-row">
                      <span class="pair-badge">{p}</span>
                      <span class="pair-badge {cls}">{arrow} {sig}</span>
                      <span style="color:#8a9bb5;font-size:13px">{reason}</span>
                    </div>"""
                cards_html += "</div>"
                st.markdown(cards_html, unsafe_allow_html=True)

                # ติดตามต่อ
                if watch:
                    st.markdown('<p class="section-label">📌 ต้องติดตามต่อ</p>', unsafe_allow_html=True)
                    st.markdown(f'<div class="card">{watch}</div>', unsafe_allow_html=True)

                st.markdown('<div class="warning-box">⚠️ ข้อมูลนี้เป็นการสรุปข่าวเท่านั้น ไม่ใช่คำแนะนำการลงทุน</div>', unsafe_allow_html=True)

        with col2:
            st.markdown('<p class="section-label">📰 ข่าวที่ใช้วิเคราะห์</p>', unsafe_allow_html=True)
            for a in articles[:8]:
                st.markdown(f"""
                <div class="card" style="padding:12px 16px;margin-bottom:8px">
                  <span style="font-size:10px;color:#2e4a6a;font-family:'IBM Plex Mono',monospace">{a['source']}</span><br>
                  <span style="font-size:13px;color:#c8d4e8">{a['title']}</span>
                </div>""", unsafe_allow_html=True)

        st.caption(f"อัพเดทล่าสุด: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

else:
    # หน้าแรกก่อนกด Run
    st.markdown("""
    <div class="card" style="text-align:center;padding:40px">
      <p style="font-size:40px;margin-bottom:12px">💱</p>
      <p style="color:#4a7fa5;font-size:15px">ใส่ API Key และเลือกคู่สกุลเงินในแถบซ้าย<br>แล้วกดปุ่ม <strong style="color:#7dd3fc">⚡ วิเคราะห์ตอนนี้</strong></p>
    </div>
    """, unsafe_allow_html=True)
