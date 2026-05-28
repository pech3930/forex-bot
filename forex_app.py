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
html,body,[class*="css"]{font-family:'Press Start 2P',monospace;background:#0a0a14;color:#e0e0e0}
.stApp{background:#0a0a14}
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
    # fixed positions: agents stand at their desk (measured from office_bg.png)
    # (x%, y%) — percentage of background image
    desk_positions=[
        (0.34, 0.65),  # เก้าอี้ 1: ซ้ายบน
        (0.51, 0.54),  # เก้าอี้ 2: กลางบน
        (0.80, 0.72),  # เก้าอี้ 3: ขวาล่าง ใกล้ตู้น้ำ
        (0.62, 0.90),  # เก้าอี้ 4: กลางล่างสุด
        (0.67, 0.53),  # เก้าอี้ 5: ขวากลาง
        (0.79, 0.63),  # เก้าอี้ 6: ขวาล่าง
    ]
    agents=[]
    for i,p in enumerate(pairs):
        sig,reason=signals.get(p,("NEUTRAL","Analyzing..."))
        msgs={"BULLISH":[p+"!","▲ BUY!","Bullish!","UP!"],
              "BEARISH":[p+"!","▼ SELL!","Bearish!","DOWN!"],
              "NEUTRAL":[p,"◆ WAIT","Watch","..."]}.get(sig,["..."])
        dx,dy=desk_positions[i%len(desk_positions)]
        agents.append({"pair":p,"signal":sig,"reason":reason,
                       "px":dx,"py":dy,
                       "minX":dx-0.03,"maxX":dx+0.03,
                       "tint":tints[i%len(tints)],"msgs":msgs,"fr":i*20,
                       "walking":True,"dir":1 if i%2==0 else -1})
    return agents
def render_canvas(agents, bg_url, sprite_url):
    agents_json=str(agents).replace("True","true").replace("False","false").replace("'",'"')
    return f"""
<style>
html,body{{margin:0;padding:0;overflow:hidden;background:#0a0a14}}
.scene{{position:relative;width:100%;height:700px;background:#0a0a14;
  display:flex;align-items:center;justify-content:center}}
.bg{{width:100%;height:100%;
  background:url('{bg_url}') center/contain no-repeat}}
canvas{{position:absolute;top:0;left:0;width:100%;height:100%}}
</style>
<div class="scene">
  <div class="bg"></div>
  <canvas id="fc"></canvas>
</div>
<script>
const SPRITE_URL="{sprite_url}";
const AGENTS={agents_json};
const cv=document.getElementById('fc');
const ctx=cv.getContext('2d');
ctx.imageSmoothingEnabled=false;

// ── sizing: match the scene div ──
function resize(){{
  const scene=document.querySelector('.scene');
  cv.width=scene.offsetWidth;
  cv.height=scene.offsetHeight;
}}
setTimeout(resize,200);
window.addEventListener('resize',resize);

// ── background image bounds ──
// the bg image uses "contain" so we need to find where it actually renders
const bgImg=new Image();
bgImg.src="{bg_url}";
let bgX=0,bgY=0,bgW=0,bgH=0;
function calcBgBounds(){{
  if(bgImg.width===0) return;
  const ratio=bgImg.width/bgImg.height;
  const sceneW=cv.width, sceneH=cv.height;
  const sceneRatio=sceneW/sceneH;
  if(sceneRatio>ratio){{
    bgH=sceneH; bgW=sceneH*ratio;
  }} else {{
    bgW=sceneW; bgH=sceneW/ratio;
  }}
  bgX=(sceneW-bgW)/2;
  bgY=(sceneH-bgH)/2;
}}

// ── sprite ──
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
 
  ctx.globalCompositeOperation='source-over';
  ctx.globalAlpha=1;
  ctx.restore();
}}

function drawBubble(cx,cy,text,sig){{
  const col=sig==='BULLISH'?'#00ff41':sig==='BEARISH'?'#ff3131':'#ffd700';
  ctx.font='bold 9px "Press Start 2P",monospace';
  const tw=ctx.measureText(text).width;
  const bw=tw+16,bh=22,bx=cx-bw/2,by=cy-bh-12;
  ctx.fillStyle='#fff';ctx.fillRect(bx-2,by-2,bw+4,bh+4);
  ctx.fillStyle='#000';ctx.fillRect(bx,by,bw,bh);
  ctx.fillStyle=col;ctx.fillRect(bx,by,bw,4);
  ctx.fillStyle='#fff';ctx.fillText(text,bx+8,by+16);
  ctx.fillStyle='#fff';ctx.beginPath();ctx.moveTo(cx-5,by+bh+2);ctx.lineTo(cx+5,by+bh+2);ctx.lineTo(cx,by+bh+11);ctx.fill();
  ctx.fillStyle='#000';ctx.beginPath();ctx.moveTo(cx-3,by+bh+2);ctx.lineTo(cx+3,by+bh+2);ctx.lineTo(cx,by+bh+9);ctx.fill();
}}

function drawAgent(a){{
  if(!sprOK||bgW===0) return;
  const dw=FW*S, dh=FH*S;
  // convert % position to actual screen pixels within background bounds
  const x=bgX + a.px*bgW - dw/2;
  const y=bgY + a.py*bgH - dh;
  const frame=a.walking?WALK[Math.floor(a.fr/6)%4]:STAND;
  // shadow
  ctx.fillStyle='rgba(0,0,0,0.4)';
  ctx.beginPath();ctx.ellipse(x+dw/2,y+dh,dw/2.2,5,0,0,Math.PI*2);ctx.fill();
  // sprite
  drawSprite(x,y,frame,a.dir,a.tint);
  // pair label
  const sc=a.signal==='BULLISH'?'#00ff41':a.signal==='BEARISH'?'#ff3131':'#ffd700';
  ctx.fillStyle='rgba(0,0,0,0.9)';ctx.fillRect(x-4,y+dh+3,dw+8,14);
  ctx.fillStyle=sc;ctx.font='bold 8px "Press Start 2P",monospace';
  ctx.textAlign='center';ctx.fillText(a.pair,x+dw/2,y+dh+14);ctx.textAlign='left';
  // bubble
  const mi=Math.floor((tick+AGENTS.indexOf(a)*40)/100)%a.msgs.length;
  drawBubble(x+dw/2,y,a.msgs[mi],a.signal);
}}

function updateAgents(){{
  AGENTS.forEach(a=>{{
    if(a.walking){{
      a.px+=a.dir*0.001;
      a.fr+=1;
      // clamp to patrol bounds — agents stay in their area
      if(a.px>a.maxX){{a.px=a.maxX;a.dir=-1;}}
      if(a.px<a.minX){{a.px=a.minX;a.dir=1;}}
    }}
    if(Math.random()<0.004){{
      a.walking=false;
      setTimeout(()=>a.walking=true,1500+Math.random()*2500);
    }}
  }});
}}

function loop(){{
  tick++;
  calcBgBounds();
  ctx.clearRect(0,0,cv.width,cv.height);
  updateAgents();
  [...AGENTS].sort((a,b)=>a.py-b.py).forEach(a=>drawAgent(a));
  // clock
  const n=new Date();
  const ts=n.getHours().toString().padStart(2,'0')+':'+
           n.getMinutes().toString().padStart(2,'0')+':'+
           n.getSeconds().toString().padStart(2,'0');
  ctx.fillStyle='rgba(0,0,0,0.8)';ctx.fillRect(cv.width-105,8,98,20);
  ctx.strokeStyle='#4a9eff';ctx.lineWidth=1;ctx.strokeRect(cv.width-105,8,98,20);
  ctx.fillStyle='#00ff41';ctx.font='9px "Press Start 2P",monospace';
  ctx.fillText(ts,cv.width-98,22);
  requestAnimationFrame(loop);
}}
loop();
</script>
"""

BG_URL     = "https://raw.githubusercontent.com/pech3930/forex-bot/main/office_bg.png"
SPRITE_URL = "https://raw.githubusercontent.com/pech3930/forex-bot/main/Astronaut.png"

if not run_btn:
    default_agents=build_agents(
        selected_pairs if selected_pairs else ["EUR/USD","USD/THB","USD/JPY","GBP/USD","XAU/USD"],{})
    st.components.v1.html(render_canvas(default_agents,BG_URL,SPRITE_URL),height=720,scrolling=False)
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
        ph.components.v1.html(render_canvas(loading,BG_URL,SPRITE_URL),height=720,scrolling=False)
        with st.spinner(""):
            articles=fetch_news()
            raw=analyze(articles,selected_pairs,api_key)
            overview,signals,watch=parse_result(raw,selected_pairs)
        final=build_agents(selected_pairs,signals)
        ph.empty()
        st.components.v1.html(render_canvas(final,BG_URL,SPRITE_URL),height=720,scrolling=False)
        cols=st.columns(len(selected_pairs))
        for i,(p,col) in enumerate(zip(selected_pairs,cols)):
            sig,reason=signals.get(p,("NEUTRAL","No data"))
            sc="#00ff41" if sig=="BULLISH" else "#ff3131" if sig=="BEARISH" else "#ffd700"
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
