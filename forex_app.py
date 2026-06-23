import streamlit as st
import anthropic
import feedparser
import json
import shelve
import re
import numpy as np
import yfinance as yf
from datetime import datetime, date

st.set_page_config(page_title="FOREX TRADING OFFICE", page_icon="💹", layout="wide")

# ── Persistent history storage ──
def load_history():
    try:
        with shelve.open("/tmp/forex_history") as db:
            return db.get("history", [])
    except:
        return []

def save_history(history):
    try:
        with shelve.open("/tmp/forex_history") as db:
            db["history"] = history
    except:
        pass

if "history" not in st.session_state:
    st.session_state.history = load_history()

# ── Yahoo Finance symbol map ──
YAHOO_SYMBOLS = {
    "EUR/USD": "EURUSD=X", "USD/THB": "USDTHB=X", "GBP/USD": "GBPUSD=X",
    "USD/JPY": "USDJPY=X", "XAU/USD": "GC=F", "AUD/USD": "AUDUSD=X",
    "EUR/JPY": "EURJPY=X",
}

# ── Technical Indicators ──
def calc_rsi(closes, period=14):
    if len(closes) < period + 1:
        return 50.0
    deltas = np.diff(closes)
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)
    avg_gain = np.mean(gains[-period:])
    avg_loss = np.mean(losses[-period:])
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return round(100 - (100 / (1 + rs)), 1)

def calc_macd(closes):
    if len(closes) < 26:
        return 0, 0, "NEUTRAL"
    ema12 = float(np.mean(closes[-12:]))
    ema26 = float(np.mean(closes[-26:]))
    macd_line = round(ema12 - ema26, 5)
    signal_line = round(float(np.mean(closes[-9:])) - ema26, 5)
    if macd_line > signal_line:
        cross = "BULLISH"
    elif macd_line < signal_line:
        cross = "BEARISH"
    else:
        cross = "NEUTRAL"
    return macd_line, signal_line, cross

def calc_ma(closes, period):
    if len(closes) < period:
        return 0
    return round(float(np.mean(closes[-period:])), 5)

@st.cache_data(ttl=60)
def fetch_live_prices(pairs):
    prices = {}
    for p in pairs:
        sym = YAHOO_SYMBOLS.get(p)
        if not sym:
            continue
        try:
            t = yf.Ticker(sym)
            h = t.history(period="1d", interval="1m")
            if not h.empty:
                price = float(h["Close"].iloc[-1])
                prev = float(h["Close"].iloc[0])
                change = price - prev
                pct = (change / prev) * 100 if prev else 0
                prices[p] = {"price": price, "change": change, "pct": pct}
        except:
            prices[p] = {"price": 0, "change": 0, "pct": 0}
    return prices

@st.cache_data(ttl=120)
def fetch_technical_data(pairs):
    tech = {}
    for p in pairs:
        sym = YAHOO_SYMBOLS.get(p)
        if not sym:
            continue
        try:
            t = yf.Ticker(sym)
            tf_data = {}
            for tf_label, tf_period, tf_interval in [("1H", "5d", "1h"), ("4H", "30d", "1h"), ("1D", "90d", "1d")]:
                h = t.history(period=tf_period, interval=tf_interval)
                if h.empty:
                    continue
                closes = h["Close"].values
                if tf_label == "4H":
                    closes = closes[::4] if len(closes) > 4 else closes
                current = float(closes[-1])
                rsi = calc_rsi(closes)
                macd_line, signal_line, macd_cross = calc_macd(closes)
                ma20 = calc_ma(closes, 20)
                ma50 = calc_ma(closes, 50)
                if current > ma20 and rsi < 70:
                    trend = "BULLISH"
                elif current < ma20 and rsi > 30:
                    trend = "BEARISH"
                else:
                    trend = "NEUTRAL"
                tf_data[tf_label] = {"rsi": rsi, "macd": macd_line, "macd_signal": signal_line,
                    "macd_cross": macd_cross, "ma20": ma20, "ma50": ma50, "trend": trend, "price": current}
            tech[p] = tf_data
        except:
            tech[p] = {}
    return tech

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');
*{box-sizing:border-box;margin:0;padding:0;image-rendering:pixelated}
html,body,[class*="css"]{font-family:'Press Start 2P',monospace;background:#0a0a14;color:#e0e0e0}
.stApp{background:#0a0a14}
.block-container{padding:0.5rem 1rem!important}
.stButton>button{font-family:'Press Start 2P',monospace!important;font-size:8px!important;
  background:#4a9eff!important;color:#000!important;border:none!important;border-radius:0!important;
  box-shadow:4px 4px 0 #1a4a7a!important;width:100%!important;padding:12px!important}
.stButton>button:hover{transform:translate(2px,2px);box-shadow:2px 2px 0 #1a4a7a!important}
[data-testid="stSidebar"]{background:#0d0d1a!important;border-right:3px solid #4a9eff}
iframe{border:none!important}
.news-panel{background:#0d0d1a;border:3px solid #4a9eff;padding:12px;height:700px;overflow-y:auto;box-shadow:4px 4px 0 #1a4a7a}
.news-panel::-webkit-scrollbar{width:8px}
.news-panel::-webkit-scrollbar-track{background:#0a0a14}
.news-panel::-webkit-scrollbar-thumb{background:#4a9eff}
.news-title{font-family:'Press Start 2P',monospace;font-size:12px;color:#4a9eff;margin-bottom:10px;letter-spacing:1px;border-bottom:2px solid #4a9eff;padding-bottom:6px}
.news-card{background:#1a1a2e;border:2px solid #2a3f6a;padding:8px;margin-bottom:10px}
.news-card-title{font-family:'Press Start 2P',monospace;font-size:15px;margin-bottom:6px;letter-spacing:1px}
.news-card-body{font-family:'Press Start 2P',monospace;font-size:20px;color:#ccc;line-height:2.5}
.ticker-wrap{width:100%;background:#000;border-top:2px solid #4a9eff;border-bottom:2px solid #4a9eff;overflow:hidden;padding:6px 0;margin-bottom:10px}
.ticker-track{display:inline-flex;gap:40px;animation:ticker 30s linear infinite;white-space:nowrap}
@keyframes ticker{from{transform:translateX(0)}to{transform:translateX(-50%)}}
.ticker-item{font-family:'Press Start 2P',monospace;font-size:11px;display:inline-flex;align-items:center;gap:8px}
</style>
""", unsafe_allow_html=True)

def render_ticker(prices):
    if not prices:
        return '<div class="ticker-wrap"><span style="font-family:\'Press Start 2P\',monospace;font-size:11px;color:#555;padding:0 20px">กำลังโหลดราคา...</span></div>'
    items = ""
    for p, v in prices.items():
        col = "#00ff41" if v["change"] >= 0 else "#ff3131"
        arrow = "▲" if v["change"] >= 0 else "▼"
        dec = 5 if "JPY" not in p and "THB" not in p else 3
        price_str = f"{v['price']:.{dec}f}"
        pct_str = f"{v['pct']:+.2f}%"
        items += f'<span class="ticker-item"><span style="color:#888">{p}</span><span style="color:#fff">{price_str}</span><span style="color:{col}">{arrow}{pct_str}</span></span>'
    return f'<div class="ticker-wrap"><div class="ticker-track">{items}{items}</div></div>'

st.markdown(f"""
<div style="font-family:'Press Start 2P',monospace;font-size:10px;background:#000;
  border:3px solid #4a9eff;padding:10px 16px;box-shadow:6px 6px 0 #1a4a7a;margin-bottom:6px;
  display:flex;justify-content:space-between;align-items:center">
  <span style="color:#4a9eff">💹 FOREX TRADING OFFICE</span>
  <span style="font-size:7px;color:#ffd700">POWERED BY CLAUDE AI</span>
  <span style="font-size:8px;color:#00ff41">● {datetime.now().strftime('%H:%M:%S')}</span>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown('<div style="font-family:\'Press Start 2P\',monospace;font-size:8px;color:#4a9eff;margin-bottom:10px">⚙ CONFIG</div>', unsafe_allow_html=True)
    try:
        api_key = st.secrets["ANTHROPIC_API_KEY"].strip()
    except Exception:
        api_key = ""
    if api_key:
        st.markdown('<div style="font-family:\'Press Start 2P\',monospace;font-size:7px;color:#00ff41;margin-bottom:8px">✓ KEY LOADED</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="font-size:14px;color:#ffd700;font-family:monospace">🔑 API KEY</div>', unsafe_allow_html=True)
        api_key = st.text_input("", type="password", placeholder="sk-ant-...", label_visibility="collapsed")
    st.markdown("---")
    st.markdown('<div style="font-family:\'Press Start 2P\',monospace;font-size:7px;color:#ffd700;margin-bottom:6px">💱 PAIRS</div>', unsafe_allow_html=True)
    selected_pairs = st.multiselect("",
        ["EUR/USD","USD/THB","GBP/USD","USD/JPY","XAU/USD","AUD/USD","EUR/JPY"],
        default=["EUR/USD","USD/THB","USD/JPY","GBP/USD","XAU/USD"],
        label_visibility="collapsed")
    st.markdown("---")
    st.markdown('<div style="font-family:\'Press Start 2P\',monospace;font-size:7px;color:#ffd700;margin-bottom:6px">📡 SOURCE</div>', unsafe_allow_html=True)
    use_reuters = st.checkbox("Reuters", value=True)
    use_investing = st.checkbox("Investing.com", value=True)
    st.markdown("---")
    st.markdown("""
    <div style="font-family:'Press Start 2P',monospace;font-size:7px;color:#4a9eff;margin-bottom:6px">AI AGENTS</div>
    <div style="border:2px solid #00ff41;background:#001a00;padding:5px 7px;margin:3px 0;font-size:10px">🤖 <span style="color:#00ff41">News Agent</span></div>
    <div style="border:2px solid #00ff41;background:#001a00;padding:5px 7px;margin:3px 0;font-size:10px">🧠 <span style="color:#00ff41">Analysis Agent</span></div>
    <div style="border:2px solid #00ff41;background:#001a00;padding:5px 7px;margin:3px 0;font-size:10px">📊 <span style="color:#00ff41">Technical Agent</span></div>
    <div style="border:2px solid #333;background:#0d0d1a;padding:5px 7px;margin:3px 0;font-size:10px">⚡ <span style="color:#555">Signal Agent</span></div>
    <br>""", unsafe_allow_html=True)
    run_btn = st.button("▶  ANALYZE NOW")

RSS = {}
if use_reuters: RSS["Reuters"] = "https://feeds.reuters.com/reuters/businessNews"
if use_investing: RSS["Investing.com"] = "https://www.investing.com/rss/news_25.rss"

def fetch_news():
    articles = []
    for src, url in RSS.items():
        try:
            feed = feedparser.parse(url)
            for e in feed.entries[:8]:
                raw_sum = e.get("summary", "") or e.get("description", "") or ""
                clean_sum = re.sub(r'<[^>]+>', '', raw_sum).strip()[:300]
                articles.append({"source": src, "title": e.get("title", ""), "summary": clean_sum})
        except:
            pass
    return articles

def build_tech_prompt(tech_data, pairs):
    lines = []
    for p in pairs:
        td = tech_data.get(p, {})
        if not td:
            continue
        parts = [f"\n[{p} Technical Data]"]
        for tf in ["1H", "4H", "1D"]:
            d = td.get(tf)
            if not d:
                continue
            parts.append(f"  {tf}: RSI={d['rsi']}, MACD cross={d['macd_cross']}, MA20={d['ma20']}, MA50={d['ma50']}, Trend={d['trend']}")
        lines.append("\n".join(parts))
    return "\n".join(lines)

def analyze(articles, pairs, key, tech_data):
    client = anthropic.Anthropic(api_key=key)
    news_text = "\n\n".join(f"[{a['source']}] {a['title']}\n{a['summary']}" for a in articles)
    tech_text = build_tech_prompt(tech_data, pairs)
    prompt = f"""คุณคือผู้เชี่ยวชาญด้านการวิเคราะห์ตลาด Forex ทั้ง Fundamental และ Technical
วิเคราะห์ข่าวสารและข้อมูล Technical Indicators แล้วประเมินผลกระทบต่อ: {", ".join(pairs)}

ข่าวสาร:
{news_text}

ข้อมูล Technical Indicators (RSI, MACD, MA20, MA50) แบบ Multi-timeframe (1H, 4H, 1D):
{tech_text}

กฎการวิเคราะห์:
- RSI > 70 = Overbought, RSI < 30 = Oversold
- MACD cross BULLISH = แนวโน้มขึ้น, BEARISH = แนวโน้มลง
- ราคาเหนือ MA20 = ขาขึ้นระยะสั้น, ใต้ MA20 = ขาลงระยะสั้น
- ถ้า 1H, 4H, 1D trend ตรงกัน = สัญญาณแรง

ตอบกลับในรูปแบบ JSON เท่านั้น:
{{
  "overview": "<สรุปภาพรวม Fundamental + Technical 3-4 ประโยคภาษาไทย>",
  "signals": {{
    {", ".join(f'"{p}": {{"signal": "<BULLISH/BEARISH/NEUTRAL>", "confidence": <1-10>, "reason": "<เหตุผลรวม Fundamental + Technical 2-3 ประโยคภาษาไทย>", "tf_trend": "<1H:BULL/BEAR/NEUT | 4H:BULL/BEAR/NEUT | 1D:BULL/BEAR/NEUT>"}}' for p in pairs)}
  }},
  "watch": "<ประเด็นที่ต้องติดตาม 2-3 ประโยคภาษาไทย>"
}}"""
    r = client.messages.create(model="claude-haiku-4-5-20251001", max_tokens=2000,
        messages=[{"role": "user", "content": prompt}])
    return r.content[0].text

def parse_result(text, pairs):
    try:
        s = text.find('{')
        e = text.rfind('}') + 1
        data = json.loads(text[s:e])
        overview = data.get("overview", "วิเคราะห์สำเร็จ")
        watch = data.get("watch", "ติดตามข่าวต่อไป")
        signals = {}
        for p in pairs:
            d = data.get("signals", {}).get(p, {"signal": "NEUTRAL", "reason": "รอสัญญาณ", "confidence": 5, "tf_trend": ""})
            sig = d.get("signal", "NEUTRAL").upper()
            signals[p] = (sig, d.get("reason", ""), d.get("confidence", 5), d.get("tf_trend", ""))
        return overview, signals, watch
    except:
        return "วิเคราะห์สำเร็จ", {p: ("NEUTRAL", "กำลังประมวลผล", 5, "") for p in pairs}, "ติดตามข่าวต่อไป"

def build_agents(pairs, signals):
    tints = ['#44aaff', '#ffaa44', '#aa88ff', '#44ffaa', '#ffdd44', '#ff88aa']
    desk_positions = [(0.34, 0.65), (0.51, 0.54), (0.80, 0.72), (0.62, 0.90), (0.67, 0.57), (0.79, 0.63)]
    agents = []
    for i, p in enumerate(pairs):
        sig_data = signals.get(p, ("NEUTRAL", "Analyzing...", 5, ""))
        sig = sig_data[0]
        msgs = {"BULLISH": [p + "!", "▲ BUY!", "Bullish!", "UP!"],
                "BEARISH": [p + "!", "▼ SELL!", "Bearish!", "DOWN!"],
                "NEUTRAL": [p, "◆ WAIT", "Watch", "..."]}.get(sig, ["..."])
        dx, dy = desk_positions[i % len(desk_positions)]
        agents.append({"pair": p, "signal": sig, "reason": sig_data[1], "px": dx, "py": dy,
                       "minX": dx - 0.03, "maxX": dx + 0.03, "tint": tints[i % len(tints)],
                       "msgs": msgs, "fr": i * 20, "walking": True, "dir": 1 if i % 2 == 0 else -1})
    return agents

def render_canvas(agents, bg_url, sprite_url):
    agents_json = str(agents).replace("True", "true").replace("False", "false").replace("'", '"')
    return f"""
<style>
html,body{{margin:0;padding:0;overflow:hidden;background:#0a0a14}}
.scene{{position:relative;width:100%;height:700px;background:#0a0a14;display:flex;align-items:center;justify-content:center}}
.bg{{width:100%;height:100%;background:url('{bg_url}') center/contain no-repeat}}
canvas{{position:absolute;top:0;left:0;width:100%;height:100%}}
</style>
<div class="scene"><div class="bg"></div><canvas id="fc"></canvas></div>
<script>
const SPRITE_URL="{sprite_url}";const AGENTS={agents_json};
const cv=document.getElementById('fc'),ctx=cv.getContext('2d');
ctx.imageSmoothingEnabled=false;
function resize(){{const s=document.querySelector('.scene');cv.width=s.offsetWidth;cv.height=s.offsetHeight;}}
setTimeout(resize,200);window.addEventListener('resize',resize);
const bgImg=new Image();bgImg.src="{bg_url}";
let bgX=0,bgY=0,bgW=0,bgH=0;
function calcBgBounds(){{if(!bgImg.width)return;const r=bgImg.width/bgImg.height,sw=cv.width,sh=cv.height,sr=sw/sh;if(sr>r){{bgH=sh;bgW=sh*r;}}else{{bgW=sw;bgH=sw/r;}}bgX=(sw-bgW)/2;bgY=(sh-bgH)/2;}}
const spr=new Image();spr.crossOrigin='anonymous';spr.src=SPRITE_URL;
let sprOK=false,FW=0,FH=0;
spr.onload=()=>{{sprOK=true;FW=Math.round(spr.width/12);FH=spr.height;}};
const WALK=[8,9,10,11],STAND=8,S=3;let tick=0;
function drawSprite(x,y,f,d){{if(!sprOK)return;const dw=FW*S,dh=FH*S;ctx.save();if(d<0){{ctx.translate(x+dw,y);ctx.scale(-1,1);ctx.drawImage(spr,f*FW,0,FW,FH,0,0,dw,dh);}}else ctx.drawImage(spr,f*FW,0,FW,FH,x,y,dw,dh);ctx.restore();}}
function drawBubble(cx,cy,text,sig){{const col=sig==='BULLISH'?'#00ff41':sig==='BEARISH'?'#ff3131':'#ffd700';ctx.font='bold 9px "Press Start 2P",monospace';const tw=ctx.measureText(text).width,bw=tw+16,bh=22,bx=cx-bw/2,by=cy-bh-12;ctx.fillStyle='#fff';ctx.fillRect(bx-2,by-2,bw+4,bh+4);ctx.fillStyle='#000';ctx.fillRect(bx,by,bw,bh);ctx.fillStyle=col;ctx.fillRect(bx,by,bw,4);ctx.fillStyle='#fff';ctx.fillText(text,bx+8,by+16);ctx.fillStyle='#fff';ctx.beginPath();ctx.moveTo(cx-5,by+bh+2);ctx.lineTo(cx+5,by+bh+2);ctx.lineTo(cx,by+bh+11);ctx.fill();ctx.fillStyle='#000';ctx.beginPath();ctx.moveTo(cx-3,by+bh+2);ctx.lineTo(cx+3,by+bh+2);ctx.lineTo(cx,by+bh+9);ctx.fill();}}
function drawAgent(a){{if(!sprOK||!bgW)return;const dw=FW*S,dh=FH*S,x=bgX+a.px*bgW-dw/2,y=bgY+a.py*bgH-dh,f=a.walking?WALK[Math.floor(a.fr/6)%4]:STAND;ctx.fillStyle='rgba(0,0,0,0.4)';ctx.beginPath();ctx.ellipse(x+dw/2,y+dh,dw/2.2,5,0,0,Math.PI*2);ctx.fill();drawSprite(x,y,f,a.dir);const sc2=a.signal==='BULLISH'?'#00ff41':a.signal==='BEARISH'?'#ff3131':'#ffd700';ctx.fillStyle='rgba(0,0,0,0.85)';ctx.fillRect(x-2,y+dh+2,dw+4,14);ctx.fillStyle=sc2;ctx.font='bold 8px "Press Start 2P",monospace';ctx.textAlign='center';ctx.fillText(a.pair,x+dw/2,y+dh+12);ctx.textAlign='left';const mi=Math.floor((tick+AGENTS.indexOf(a)*40)/100)%a.msgs.length;drawBubble(x+dw/2,y,a.msgs[mi],a.signal);}}
function updateAgents(){{AGENTS.forEach(a=>{{if(a.walking){{a.px+=a.dir*0.001;a.fr+=1;if(a.px>a.maxX){{a.px=a.maxX;a.dir=-1;}}if(a.px<a.minX){{a.px=a.minX;a.dir=1;}}}}if(Math.random()<0.004){{a.walking=false;setTimeout(()=>a.walking=true,1500+Math.random()*2500);}}}});}}
function loop(){{tick++;calcBgBounds();ctx.clearRect(0,0,cv.width,cv.height);updateAgents();[...AGENTS].sort((a,b)=>a.py-b.py).forEach(a=>drawAgent(a));const n=new Date(),ts=n.getHours().toString().padStart(2,'0')+':'+n.getMinutes().toString().padStart(2,'0')+':'+n.getSeconds().toString().padStart(2,'0');ctx.fillStyle='rgba(0,0,0,0.8)';ctx.fillRect(cv.width-105,8,98,20);ctx.strokeStyle='#4a9eff';ctx.lineWidth=1;ctx.strokeRect(cv.width-105,8,98,20);ctx.fillStyle='#00ff41';ctx.font='9px "Press Start 2P",monospace';ctx.fillText(ts,cv.width-98,22);requestAnimationFrame(loop);}}
loop();
</script>"""

# ── Accuracy & Leaderboard ──
def save_signal_history(signals, today_str):
    for p, sig_data in signals.items():
        sig = sig_data[0]
        exists = [h for h in st.session_state.history if h["date"] == today_str and h["pair"] == p]
        if not exists:
            st.session_state.history.append({"date": today_str, "pair": p, "signal": sig, "result": "pending"})
    save_history(st.session_state.history)

def render_accuracy_panel(prices):
    history = st.session_state.history
    for h in history:
        if h["result"] == "pending" and h["pair"] in prices:
            pv = prices[h["pair"]]
            if abs(pv["change"]) > 0.0001:
                if h["signal"] == "BULLISH" and pv["change"] > 0: h["result"] = "✅"
                elif h["signal"] == "BEARISH" and pv["change"] < 0: h["result"] = "✅"
                elif h["signal"] == "NEUTRAL": h["result"] = "➖"
                else: h["result"] = "❌"
    save_history(history)
    checked = [h for h in history if h["result"] in ["✅", "❌"]]
    correct = [h for h in checked if h["result"] == "✅"]
    acc = int(len(correct) / len(checked) * 100) if checked else 0
    acc_col = "#00ff41" if acc >= 60 else "#ffd700" if acc >= 40 else "#ff3131"
    total_txt = f"{len(correct)}/{len(checked)}" if checked else "0/0"
    pair_stats = {}
    for h in checked:
        p = h["pair"]
        if p not in pair_stats: pair_stats[p] = {"win": 0, "total": 0}
        pair_stats[p]["total"] += 1
        if h["result"] == "✅": pair_stats[p]["win"] += 1
    sorted_pairs = sorted(pair_stats.items(), key=lambda x: -x[1]["win"] / max(x[1]["total"], 1))
    rows = ""
    for rank, (p, s) in enumerate(sorted_pairs[:6], 1):
        pct = int(s["win"] / s["total"] * 100)
        pc = "#00ff41" if pct >= 60 else "#ffd700" if pct >= 40 else "#ff3131"
        medal = "🥇" if rank == 1 else "🥈" if rank == 2 else "🥉" if rank == 3 else f"#{rank}"
        rows += f'<div style="display:flex;justify-content:space-between;padding:5px 0;border-bottom:1px solid #2a3f6a"><span style="font-family:\'Press Start 2P\',monospace;font-size:12px">{medal} {p}</span><span style="font-family:\'Press Start 2P\',monospace;font-size:12px;color:{pc}">{pct}% ({s["win"]}/{s["total"]})</span></div>'
    if not rows:
        rows = '<div style="font-family:\'Press Start 2P\',monospace;font-size:11px;color:#555;padding:8px 0">กด ANALYZE เพื่อเริ่มเก็บข้อมูล</div>'
    return f'<div class="news-card" style="border-color:#aa88ff"><div class="news-card-title" style="color:#aa88ff">🎯 AI ACCURACY & LEADERBOARD</div><div style="display:flex;justify-content:space-between;align-items:center;padding:8px 0;margin-bottom:8px;border-bottom:2px solid #2a3f6a"><span style="font-family:\'Press Start 2P\',monospace;font-size:13px;color:#888">OVERALL ACC. ({total_txt})</span><span style="font-family:\'Press Start 2P\',monospace;font-size:20px;color:{acc_col}">{acc}%</span></div><div style="font-family:\'Press Start 2P\',monospace;font-size:12px;color:#4a9eff;margin-bottom:6px">🏆 LEADERBOARD</div>{rows}</div>'

def render_tech_badge(tf_label, trend):
    col = "#00ff41" if trend == "BULLISH" else "#ff3131" if trend == "BEARISH" else "#ffd700"
    arrow = "▲" if trend == "BULLISH" else "▼" if trend == "BEARISH" else "◆"
    short = "BULL" if trend == "BULLISH" else "BEAR" if trend == "BEARISH" else "NEUT"
    return f'<span style="font-family:\'Press Start 2P\',monospace;font-size:10px;color:{col};border:1px solid {col};padding:1px 4px;margin:0 2px">{tf_label}:{arrow}{short}</span>'

def render_news_panel(overview, signals, watch, prices, tech_data):
    signal_rows = ""
    for p, sig_data in signals.items():
        sig, reason = sig_data[0], sig_data[1]
        confidence = sig_data[2] if len(sig_data) > 2 else 5
        sc = "#00ff41" if sig == "BULLISH" else "#ff3131" if sig == "BEARISH" else "#ffd700"
        arrow = "▲" if sig == "BULLISH" else "▼" if sig == "BEARISH" else "◆"
        pv = prices.get(p, {})
        dec = 5 if "JPY" not in p and "THB" not in p else 3
        price_str = f'{pv["price"]:.{dec}f}' if pv.get("price") else "---"
        pc = "#00ff41" if pv.get("change", 0) >= 0 else "#ff3131"
        pa = "▲" if pv.get("change", 0) >= 0 else "▼"
        pct_str = f'{pv["pct"]:+.2f}%' if pv.get("pct") else ""
        conf_col = "#00ff41" if confidence >= 7 else "#ffd700" if confidence >= 4 else "#ff3131"
        conf_bar = f'<span style="font-family:\'Press Start 2P\',monospace;font-size:11px;color:{conf_col}">CONF: {"█" * confidence}{"░" * (10 - confidence)} {confidence}/10</span>'
        td = tech_data.get(p, {})
        tech_badges = ""
        tech_details = ""
        if td:
            for tf in ["1H", "4H", "1D"]:
                d = td.get(tf)
                if d:
                    tech_badges += render_tech_badge(tf, d["trend"])
            d1h = td.get("1H", {})
            if d1h:
                rsi = d1h.get("rsi", 50)
                rsi_col = "#ff3131" if rsi > 70 else "#00ff41" if rsi < 30 else "#ffd700"
                rsi_label = "OVERBOUGHT" if rsi > 70 else "OVERSOLD" if rsi < 30 else "NORMAL"
                macd_c = d1h.get("macd_cross", "NEUTRAL")
                macd_col = "#00ff41" if macd_c == "BULLISH" else "#ff3131" if macd_c == "BEARISH" else "#ffd700"
                tech_details = f'<div style="margin-top:5px;padding:4px 6px;background:#0d0d1a;border:1px solid #2a3f6a"><span style="font-family:\'Press Start 2P\',monospace;font-size:10px;color:{rsi_col}">RSI: {rsi} ({rsi_label})</span> <span style="font-family:\'Press Start 2P\',monospace;font-size:10px;color:{macd_col}">MACD: {macd_c}</span></div>'
        signal_rows += f'<div style="background:#1a1a2e;border-left:3px solid {sc};padding:8px 10px;margin:8px 0"><div style="display:flex;justify-content:space-between;align-items:center"><span style="font-family:\'Press Start 2P\',monospace;font-size:18px;color:#fff">{p}</span><div style="display:flex;gap:8px;align-items:center"><span style="font-family:\'Press Start 2P\',monospace;font-size:16px;color:{pc}">{pa}{price_str} <span style="font-size:13px">{pct_str}</span></span><span style="font-family:\'Press Start 2P\',monospace;font-size:16px;color:{sc};border:1px solid {sc};padding:2px 6px">{arrow} {sig}</span></div></div><div style="margin:5px 0">{conf_bar}</div><div style="margin:4px 0">{tech_badges}</div>{tech_details}<div style="font-family:\'Press Start 2P\',monospace;font-size:16px;color:#aaa;line-height:2.0;margin-top:8px">{reason}</div></div>'
    accuracy_html = render_accuracy_panel(prices)
    html = f'<div class="news-panel"><div class="news-title">📊 ANALYSIS DASHBOARD</div><div class="news-card" style="border-color:#4a9eff"><div class="news-card-title" style="color:#4a9eff">📋 OVERVIEW</div><div class="news-card-body">{overview}</div></div><div class="news-card" style="border-color:#00ff41"><div class="news-card-title" style="color:#00ff41">⚡ SIGNALS + TECHNICAL</div>{signal_rows}</div><div class="news-card" style="border-color:#ffd700"><div class="news-card-title" style="color:#ffd700">⚠ WATCH</div><div class="news-card-body">{watch}</div></div>{accuracy_html}<div style="border:2px dashed #ff3131;padding:6px 8px;font-family:\'Press Start 2P\',monospace;font-size:11px;color:#ff3131;margin-top:8px;line-height:1.7">⚠ NOT FINANCIAL ADVICE · FOR EDUCATIONAL PURPOSES ONLY</div></div>'
    return html

def render_news_feed(articles):
    if not articles:
        return ""
    rows = ""
    for i, a in enumerate(articles[:10]):
        src_col = "#4a9eff" if a["source"] == "Reuters" else "#ff8844"
        sum_text = a["summary"][:150] if a["summary"] else "No summary available"
        rows += f'<div style="background:#1a1a2e;border-left:3px solid {src_col};padding:8px 10px;margin:6px 0"><div style="display:flex;justify-content:space-between;align-items:center"><span style="font-family:\'Press Start 2P\',monospace;font-size:12px;color:#fff;line-height:1.8">{a["title"][:80]}</span><span style="font-family:\'Press Start 2P\',monospace;font-size:8px;color:{src_col};white-space:nowrap;margin-left:10px">{a["source"]}</span></div><div style="font-family:\'Press Start 2P\',monospace;font-size:10px;color:#888;line-height:1.7;margin-top:5px">{sum_text}</div></div>'
    return f'<div style="background:#0d0d1a;border:3px solid #4a9eff;padding:12px;margin-top:10px;box-shadow:4px 4px 0 #1a4a7a"><div style="font-family:\'Press Start 2P\',monospace;font-size:12px;color:#4a9eff;margin-bottom:10px;border-bottom:2px solid #4a9eff;padding-bottom:6px">📰 LIVE NEWS FEED</div>{rows}</div>'

BG_URL = "https://raw.githubusercontent.com/pech3930/forex-bot/main/office_bg.png"
SPRITE_URL = "https://raw.githubusercontent.com/pech3930/forex-bot/main/Astronaut.png"

pairs_for_ticker = selected_pairs if selected_pairs else ["EUR/USD", "USD/THB", "USD/JPY", "GBP/USD", "XAU/USD"]
live_prices = fetch_live_prices(pairs_for_ticker)
tech_data = fetch_technical_data(pairs_for_ticker)

st.markdown(render_ticker(live_prices), unsafe_allow_html=True)

if not run_btn:
    default_agents = build_agents(pairs_for_ticker, {})
    col_room, col_news = st.columns([2, 1])
    with col_room:
        st.components.v1.html(render_canvas(default_agents, BG_URL, SPRITE_URL), height=720, scrolling=False)
    with col_news:
        st.markdown(f'<div class="news-panel"><div class="news-title">📊 ANALYSIS DASHBOARD</div><div class="news-card" style="border-color:#4a9eff"><div class="news-card-title" style="color:#4a9eff">📋 STATUS</div><div class="news-card-body">กดปุ่ม ANALYZE NOW เพื่อเริ่มวิเคราะห์ตลาด</div></div><div class="news-card" style="border-color:#ffd700"><div class="news-card-title" style="color:#ffd700">💡 INFO</div><div class="news-card-body">AI จะวิเคราะห์ทั้ง Fundamental + Technical แบบ Multi-timeframe</div></div>{render_accuracy_panel(live_prices)}</div>', unsafe_allow_html=True)
    waiting_articles = fetch_news()
    st.markdown(render_news_feed(waiting_articles), unsafe_allow_html=True)
else:
    if not api_key:
        st.error("NO API KEY")
    elif not selected_pairs:
        st.error("SELECT PAIRS")
    else:
        with st.spinner("กำลังวิเคราะห์ Fundamental + Technical..."):
            articles = fetch_news()
            try:
                raw = analyze(articles, selected_pairs, api_key, tech_data)
                overview, signals, watch = parse_result(raw, selected_pairs)
                save_signal_history(signals, date.today().strftime("%Y-%m-%d"))
            except Exception as e:
                st.error(f"API Error: {type(e).__name__}: {e}")
                overview, signals, watch = "Error", {p: ("NEUTRAL", "API Error", 5, "") for p in selected_pairs}, "Check API Key"

        final = build_agents(selected_pairs, signals)
        col_room, col_news = st.columns([2, 1])
        with col_room:
            st.components.v1.html(render_canvas(final, BG_URL, SPRITE_URL), height=720, scrolling=False)
        with col_news:
            st.markdown(render_news_panel(overview, signals, watch, live_prices, tech_data), unsafe_allow_html=True)
        st.markdown(render_news_feed(articles), unsafe_allow_html=True)
