import streamlit as st
import anthropic
import feedparser
import os
import json
from datetime import datetime

st.set_page_config(page_title="FOREX TRADING OFFICE", page_icon="💹", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');
*{box-sizing:border-box;margin:0;padding:0;image-rendering:pixelated}
html,body,[class*="css"]{font-family:'Press Start 2P',monospace;background:#1a1a2e;color:#e0e0e0}
.stApp{background:#1a1a2e}
.block-container{padding:0.5rem 1rem!important}
.stButton>button{font-family:'Press Start 2P',monospace!important;font-size:8px!important;
  background:#4a9eff!important;color:#000!important;border:none!important;border-radius:0!important;
  box-shadow:4px 4px 0 #1a4a7a!important;width:100%!important;padding:12px!important}
.stButton>button:hover{transform:translate(2px,2px);box-shadow:2px 2px 0 #1a4a7a!important}
[data-testid="stSidebar"]{background:#0d0d1a!important;border-right:3px solid #4a9eff}
iframe{border:none!important}
</style>
""", unsafe_allow_html=True)

st.markdown(f"""
<div style="font-family:'Press Start 2P',monospace;font-size:10px;background:#000;
  border:3px solid #4a9eff;padding:10px 16px;box-shadow:6px 6px 0 #1a4a7a;margin-bottom:10px;
  display:flex;justify-content:space-between;align-items:center">
  <span style="color:#4a9eff">💹 FOREX TRADING OFFICE</span>
  <span style="font-size:7px;color:#ffd700">POWERED BY CLAUDE AI</span>
  <span style="font-size:8px;color:#00ff41">● {datetime.now().strftime('%H:%M:%S')}</span>
</div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown('<div style="font-family:\'Press Start 2P\',monospace;font-size:8px;color:#4a9eff;margin-bottom:10px">⚙ CONFIG</div>', unsafe_allow_html=True)
    api_key = os.environ.get("ANTHROPIC_API_KEY","")
    if api_key:
        st.markdown('<div style="font-family:\'Press Start 2P\',monospace;font-size:7px;color:#00ff41;margin-bottom:8px">✓ KEY LOADED</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="font-size:14px;color:#ffd700;font-family:monospace">🔑 API KEY</div>', unsafe_allow_html=True)
        api_key = st.text_input("", type="password", placeholder="sk-ant-...", label_visibility="collapsed")
    st.markdown("---")
    st.markdown('<div style="font-family:\'Press Start 2P\',monospace;font-size:7px;color:#ffd700;margin-bottom:6px">💱 PAIRS</div>', unsafe_allow_html=True)
    selected_pairs = st.multiselect("",
        ["EUR/USD","USD/THB","GBP/USD","USD/JPY","XAU/USD","AUD/USD"],
        default=["EUR/USD","USD/THB","USD/JPY","GBP/USD","XAU/USD"],
        label_visibility="collapsed")
    st.markdown("---")
    st.markdown('<div style="font-family:\'Press Start 2P\',monospace;font-size:7px;color:#ffd700;margin-bottom:6px">📡 SOURCE</div>', unsafe_allow_html=True)
    use_reuters   = st.checkbox("Reuters",       value=True)
    use_investing = st.checkbox("Investing.com", value=True)
    st.markdown("---")
    st.markdown("""
    <div style="font-family:'Press Start 2P',monospace;font-size:7px;color:#4a9eff;margin-bottom:6px">AI AGENTS</div>
    <div style="border:2px solid #00ff41;background:#001a00;padding:5px 7px;margin:3px 0;font-size:10px">🤖 <span style="color:#00ff41">News Agent</span></div>
    <div style="border:2px solid #00ff41;background:#001a00;padding:5px 7px;margin:3px 0;font-size:10px">🧠 <span style="color:#00ff41">Analysis Agent</span></div>
    <div style="border:2px solid #333;background:#0d0d1a;padding:5px 7px;margin:3px 0;font-size:10px">⚡ <span style="color:#555">Signal Agent</span></div>
    <br>""", unsafe_allow_html=True)
    run_btn = st.button("▶  ANALYZE NOW")

RSS = {}
if use_reuters:   RSS["Reuters"]       = "https://feeds.reuters.com/reuters/businessNews"
if use_investing: RSS["Investing.com"] = "https://www.investing.com/rss/news_25.rss"

def fetch_news():
    articles=[]
    for src,url in RSS.items():
        try:
            feed=feedparser.parse(url)
            for e in feed.entries[:8]:
                articles.append({"source":src,"title":e.get("title",""),"summary":e.get("summary","")[:300]})
        except: pass
    return articles

def analyze(articles,pairs,key):
    client=anthropic.Anthropic(api_key=key)
    news_text="\n\n".join(f"[{a['source']}] {a['title']}\n{a['summary']}" for a in articles)
    prompt=f"""คุณคือผู้เชี่ยวชาญด้านการวิเคราะห์ตลาด Forex
วิเคราะห์ข่าวและประเมินผลกระทบต่อ: {", ".join(pairs)}
ข่าวสาร:\n{news_text}
ตอบกลับในรูปแบบ JSON เท่านั้น:
{{
  "overview": "<สรุป 2-3 ประโยคภาษาไทย>",
  "signals": {{
    {", ".join(f'"{p}": {{"signal": "<BULLISH/BEARISH/NEUTRAL>", "reason": "<เหตุผล 1 ประโยคภาษาไทย>"}}' for p in pairs)}
  }},
  "watch": "<ประเด็นที่ต้องติดตาม>"
}}"""
    r=client.messages.create(model="claude-3-5-sonnet-20241022",max_tokens=1000,
        messages=[{"role":"user","content":prompt}])
    return r.content[0].text

def parse_result(text,pairs):
    try:
        s=text.find('{'); e=text.rfind('}')+1
        data=json.loads(text[s:e])
        overview=data.get("overview","วิเคราะห์สำเร็จ")
        watch=data.get("watch","ติดตามข่าวต่อไป")
        signals={}
        for p in pairs:
            d=data.get("signals",{}).get(p,{"signal":"NEUTRAL","reason":"รอสัญญาณ"})
            sig=d.get("signal","NEUTRAL").upper()
            signals[p]=(sig,d.get("reason",""))
        return overview,signals,watch
    except:
        return "วิเคราะห์สำเร็จ",{p:("NEUTRAL","กำลังประมวลผล") for p in pairs},"ติดตามข่าวต่อไป"

def build_agents(pairs,signals):
    tints=['#44aaff','#ffaa44','#aa88ff','#44ffaa','#ffdd44','#ff88aa']
    # x positions across the room (in % of room width)
    positions_x=[0.2,0.4,0.6,0.8,0.3,0.7]
    y_pos=0.55  # walk on floor level
    agents=[]
    for i,p in enumerate(pairs):
        sig,reason=signals.get(p,("NEUTRAL","Analyzing..."))
        msgs={"BULLISH":[p+"!","▲ BUY!","Bullish!","UP!"],
              "BEARISH":[p+"!","▼ SELL!","Bearish!","DOWN!"],
              "NEUTRAL":[p,"◆ WAIT","Watch","..."]}.get(sig,["..."])
        agents.append({"pair":p,"signal":sig,"reason":reason,
                       "px":positions_x[i%len(positions_x)],"py":y_pos,
                       "tint":tints[i%len(tints)],"msgs":msgs,"fr":i*20,
                       "walking":True,"dir":1 if i%2==0 else -1})
    return agents

def render_canvas(agents, sprite_url):
    agents_json=str(agents).replace("True","true").replace("False","false").replace("'",'"')
    return f"""
<style>
html,body{{margin:0;padding:0;background:#1a1a2e;overflow:hidden}}
.scene{{position:relative;width:100%;height:600px;background:#2a1a0e;overflow:hidden}}
.room{{position:absolute;left:50%;top:0;transform:translateX(-50%);width:90%;max-width:1100px;height:100%}}
.floor{{position:absolute;left:0;right:0;top:30%;bottom:0;
  background:repeating-linear-gradient(90deg,#c8a870 0px,#c8a870 60px,#b89860 60px,#b89860 120px);
  border-top:6px solid #6b4a2a}}
.wall{{position:absolute;left:0;right:0;top:0;height:30%;
  background:linear-gradient(180deg,#3a2a1a 0%,#4a3528 100%)}}
.window{{position:absolute;top:8%;width:14%;height:18%;
  background:linear-gradient(180deg,#5a8acc 0%,#3a6aac 100%);
  border:4px solid #2a1a0e;box-shadow:inset 0 0 0 2px #87ceeb}}
.window::before,.window::after{{content:'';position:absolute;background:#2a1a0e}}
.window::before{{left:50%;top:0;bottom:0;width:3px;transform:translateX(-50%)}}
.window::after{{top:50%;left:0;right:0;height:3px;transform:translateY(-50%)}}
.w1{{left:8%}} .w2{{left:30%}} .w3{{left:52%}} .w4{{left:74%}}
.desk{{position:absolute;width:130px;height:60px;background:#8B5E3C;
  border:3px solid #5a3a1a;border-radius:4px}}
.desk::before{{content:'';position:absolute;left:8px;top:-32px;width:50px;height:36px;
  background:#1a1a2e;border:3px solid #333;border-radius:3px}}
.desk::after{{content:'';position:absolute;left:13px;top:-26px;width:40px;height:25px;
  background:#0a4a2e}}
.d1{{left:5%;bottom:8%}} .d2{{left:30%;bottom:8%}} .d3{{left:55%;bottom:8%}} .d4{{left:80%;bottom:8%}}
.plant{{position:absolute;width:30px;height:50px;bottom:8%}}
.plant::before{{content:'';position:absolute;bottom:0;left:5px;width:20px;height:20px;
  background:#8B4513;border:2px solid #5a3010;border-radius:3px}}
.plant::after{{content:'🌿';position:absolute;bottom:18px;left:0;font-size:30px;line-height:1}}
.p1{{left:1%}} .p2{{left:96%}} .p3{{left:22%}} .p4{{left:48%}} .p5{{left:72%}}
.board{{position:absolute;background:#f5f5ee;border:4px solid #6b4a2a;
  width:90px;height:60px;top:6%;color:#c0392b;font-family:monospace;font-size:8px;
  padding:4px;display:flex;flex-direction:column;justify-content:space-around}}
.b1{{left:18%}} .b2{{right:18%}}
.board div{{display:flex;align-items:center;gap:3px}}
.board span{{display:inline-block;width:30px;height:3px}}
canvas{{position:absolute;left:0;top:0;width:100%;height:100%;pointer-events:none}}
</style>
<div class="scene">
  <div class="room">
    <div class="wall"></div>
    <div class="window w1"></div>
    <div class="window w2"></div>
    <div class="window w3"></div>
    <div class="window w4"></div>
    <div class="floor"></div>
    <div class="board b1">
      <div>BUY <span style="background:#00c853"></span></div>
      <div>SELL <span style="background:#ff3131"></span></div>
      <div>HOLD <span style="background:#ffd700"></span></div>
    </div>
    <div class="board b2">
      <div style="color:#4a9eff;font-weight:bold">SIGNALS</div>
      <div>EUR <span style="background:#00c853"></span></div>
      <div>USD <span style="background:#ffd700"></span></div>
    </div>
    <div class="desk d1"></div>
    <div class="desk d2"></div>
    <div class="desk d3"></div>
    <div class="desk d4"></div>
    <div class="plant p1"></div>
    <div class="plant p2"></div>
    <div class="plant p3"></div>
    <div class="plant p4"></div>
    <div class="plant p5"></div>
    <canvas id="fc"></canvas>
  </div>
</div>

<script>
const SPRITE_URL="{sprite_url}";
const AGENTS={agents_json};
const cv=document.getElementById('fc');
const ctx=cv.getContext('2d');
ctx.imageSmoothingEnabled=false;

function resize(){{
  const room=document.querySelector('.room');
  cv.width=room.offsetWidth;
  cv.height=room.offsetHeight;
}}
setTimeout(resize,100);
window.addEventListener('resize',resize);

const spr=new Image();
spr.crossOrigin='anonymous';
spr.src=SPRITE_URL;
let sprOK=false, FW=0, FH=0;
spr.onload=()=>{{sprOK=true;FW=Math.round(spr.width/12);FH=spr.height;}};

const WALK=[8,9,10,11], STAND=8, S=3;
let tick=0;

function drawSprite(x,y,frame,dir,tint){{
  if(!sprOK) return;
  const dw=FW*S, dh=FH*S;
  ctx.save();
  if(dir<0){{ctx.translate(x+dw,y);ctx.scale(-1,1);ctx.drawImage(spr,frame*FW,0,FW,FH,0,0,dw,dh);}}
  else ctx.drawImage(spr,frame*FW,0,FW,FH,x,y,dw,dh);
  ctx.globalCompositeOperation='multiply';
  ctx.globalAlpha=0.22;
  ctx.fillStyle=tint;
  ctx.fillRect(dir<0?0:x,y,dw,dh);
  ctx.globalCompositeOperation='source-over';
  ctx.globalAlpha=1;
  ctx.restore();
}}

function drawBubble(cx,cy,text,sig){{
  const col=sig==='BULLISH'?'#00c853':sig==='BEARISH'?'#ff3131':'#ffd700';
  ctx.font='bold 10px "Press Start 2P",monospace';
  const tw=ctx.measureText(text).width;
  const bw=tw+18,bh=22,bx=cx-bw/2,by=cy-bh-14;
  ctx.fillStyle='#fff';ctx.fillRect(bx-3,by-3,bw+6,bh+6);
  ctx.fillStyle='#000';ctx.fillRect(bx,by,bw,bh);
  ctx.fillStyle=col;ctx.fillRect(bx,by,bw,4);
  ctx.fillStyle='#fff';
  ctx.fillText(text,bx+9,by+16);
  ctx.fillStyle='#fff';ctx.beginPath();ctx.moveTo(cx-5,by+bh+3);ctx.lineTo(cx+5,by+bh+3);ctx.lineTo(cx,by+bh+12);ctx.fill();
  ctx.fillStyle='#000';ctx.beginPath();ctx.moveTo(cx-3,by+bh+3);ctx.lineTo(cx+3,by+bh+3);ctx.lineTo(cx,by+bh+10);ctx.fill();
}}

function drawAgent(a){{
  if(!sprOK) return;
  const dw=FW*S, dh=FH*S;
  const x=a.px*cv.width - dw/2;
  const y=a.py*cv.height - dh/2;
  const frame=a.walking?WALK[Math.floor(a.fr/6)%4]:STAND;
  // shadow
  ctx.fillStyle='rgba(0,0,0,0.3)';
  ctx.beginPath();ctx.ellipse(x+dw/2,y+dh,dw/2.5,5,0,0,Math.PI*2);ctx.fill();
  drawSprite(x,y,frame,a.dir,a.tint);
  // pair label
  const sc=a.signal==='BULLISH'?'#00c853':a.signal==='BEARISH'?'#ff3131':'#ffd700';
  ctx.fillStyle='rgba(0,0,0,0.9)';ctx.fillRect(x,y+dh+3,dw,14);
  ctx.fillStyle=sc;ctx.font='bold 9px monospace';ctx.textAlign='center';
  ctx.fillText(a.pair,x+dw/2,y+dh+13);ctx.textAlign='left';
  // bubble
  const mi=Math.floor((tick+AGENTS.indexOf(a)*35)/100)%a.msgs.length;
  drawBubble(x+dw/2,y,a.msgs[mi],a.signal);
}}

function updateAgents(){{
  AGENTS.forEach(a=>{{
    if(a.walking){{
      a.px+=a.dir*0.0015;
      a.fr+=1;
      if(a.px>0.92){{a.px=0.92;a.dir=-1;}}
      if(a.px<0.05){{a.px=0.05;a.dir=1;}}
    }}
    if(Math.random()<0.003){{
      a.walking=false;
      setTimeout(()=>a.walking=true,1500+Math.random()*2000);
    }}
  }});
}}

function loop(){{
  tick++;
  ctx.clearRect(0,0,cv.width,cv.height);
  updateAgents();
  [...AGENTS].sort((a,b)=>a.py-b.py).forEach(a=>drawAgent(a));
  requestAnimationFrame(loop);
}}
loop();
</script>
"""

SPRITE_URL = "https://raw.githubusercontent.com/pech3930/forex-bot/main/Astronaut.png"

if not run_btn:
    default_agents=build_agents(
        selected_pairs if selected_pairs else ["EUR/USD","USD/THB","USD/JPY","GBP/USD","XAU/USD"],{})
    st.components.v1.html(render_canvas(default_agents,SPRITE_URL),height=620,scrolling=False)
    st.markdown("""
    <div style="text-align:center;font-family:'Press Start 2P',monospace;font-size:7px;color:#333;padding:8px">
    ← PRESS ANALYZE NOW TO START
    </div>""", unsafe_allow_html=True)
else:
    if not api_key:
        st.error("NO API KEY")
    elif not selected_pairs:
        st.error("SELECT PAIRS")
    else:
        ph=st.empty()
        loading=build_agents(selected_pairs,{p:("NEUTRAL","Loading...") for p in selected_pairs})
        for a in loading: a["msgs"]=["Fetching!","Reading...","Analyzing!","Working..."]
        ph.components.v1.html(render_canvas(loading,SPRITE_URL),height=620,scrolling=False)
        with st.spinner(""):
            articles=fetch_news()
            raw=analyze(articles,selected_pairs,api_key)
            overview,signals,watch=parse_result(raw,selected_pairs)
        final=build_agents(selected_pairs,signals)
        ph.empty()
        st.components.v1.html(render_canvas(final,SPRITE_URL),height=620,scrolling=False)
        cols=st.columns(len(selected_pairs))
        for i,(p,col) in enumerate(zip(selected_pairs,cols)):
            sig,reason=signals.get(p,("NEUTRAL","No data"))
            sc="#00c853" if sig=="BULLISH" else "#ff3131" if sig=="BEARISH" else "#ffd700"
            arrow="▲" if sig=="BULLISH" else "▼" if sig=="BEARISH" else "◆"
            with col:
                st.markdown(f"""
                <div style="background:#0d0d1a;border:2px solid {sc};padding:8px;text-align:center;margin-bottom:6px">
                  <div style="font-family:'Press Start 2P',monospace;font-size:6px;color:#888;margin-bottom:4px">{p}</div>
                  <div style="font-family:'Press Start 2P',monospace;font-size:7px;color:{sc};border:1px solid {sc};padding:2px 4px;display:inline-block">{arrow} {sig}</div>
                  <div style="font-family:'Press Start 2P',monospace;font-size:5px;color:#555;margin-top:4px;line-height:1.6">{reason[:45]}</div>
                </div>""", unsafe_allow_html=True)
        if overview:
            st.markdown(f"""
            <div style="background:#0d0d1a;border:2px solid #4a9eff;padding:10px;margin-top:4px">
              <div style="font-family:'Press Start 2P',monospace;font-size:7px;color:#4a9eff;margin-bottom:6px">📋 OVERVIEW</div>
              <div style="font-family:'Press Start 2P',monospace;font-size:6px;color:#ccc;line-height:1.9">{overview}</div>
            </div>""", unsafe_allow_html=True)
        if watch:
            st.markdown(f"""
            <div style="background:#0d0d1a;border:2px solid #ffd700;padding:8px;margin-top:6px">
              <div style="font-family:'Press Start 2P',monospace;font-size:7px;color:#ffd700;margin-bottom:4px">⚠ WATCH</div>
              <div style="font-family:'Press Start 2P',monospace;font-size:6px;color:#aaa;line-height:1.8">{watch}</div>
            </div>""", unsafe_allow_html=True)
        st.markdown("""
        <div style="border:2px dashed #ff3131;padding:6px 10px;font-family:'Press Start 2P',monospace;font-size:6px;color:#ff3131;margin-top:8px">
        ⚠ NOT FINANCIAL ADVICE · FOR EDUCATIONAL PURPOSES ONLY
        </div>""", unsafe_allow_html=True)
