import streamlit as st
import anthropic
import feedparser
import os
from datetime import datetime

st.set_page_config(page_title="FOREX TRADING OFFICE", page_icon="💹", layout="wide")

st.markdown("""
<style>
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
[data-testid="stMultiSelect"]>div{background:#0d0d1a!important;border:2px solid #4a9eff!important;border-radius:0!important}
.scanline{background:repeating-linear-gradient(0deg,transparent,transparent 2px,rgba(0,0,0,0.05) 2px,rgba(0,0,0,0.05) 4px);
  pointer-events:none;position:fixed;top:0;left:0;width:100%;height:100%;z-index:9999}
</style>
<div class="scanline"></div>
""", unsafe_allow_html=True)

# ── header ──
st.markdown(f"""
<div style="font-family:'Press Start 2P',monospace;font-size:10px;background:#000;
  border:3px solid #4a9eff;padding:12px 18px;box-shadow:6px 6px 0 #1a4a7a;margin-bottom:14px;
  display:flex;justify-content:space-between;align-items:center">
  <span style="color:#4a9eff">💹 FOREX TRADING OFFICE</span>
  <span style="font-size:7px;color:#ffd700">POWERED BY CLAUDE AI</span>
  <span style="font-size:8px;color:#00ff41">● {datetime.now().strftime('%H:%M:%S')}</span>
</div>
""", unsafe_allow_html=True)

# ── sidebar ──
with st.sidebar:
    st.markdown('<div style="font-family:\'Press Start 2P\',monospace;font-size:8px;color:#4a9eff;margin-bottom:10px">⚙ CONFIG</div>', unsafe_allow_html=True)
    api_key = os.environ.get("ANTHROPIC_API_KEY","")
    if api_key:
        st.markdown('<div style="font-family:\'Press Start 2P\',monospace;font-size:7px;color:#00ff41;margin-bottom:8px">✓ KEY LOADED</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="font-family:\'VT323\',monospace;font-size:16px;color:#ffd700">🔑 API KEY</div>', unsafe_allow_html=True)
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
    <div style="border:2px solid #00ff41;background:#001a00;padding:5px 7px;margin:3px 0;font-size:10px">
      🤖 <span style="color:#00ff41">News Agent</span></div>
    <div style="border:2px solid #00ff41;background:#001a00;padding:5px 7px;margin:3px 0;font-size:10px">
      🧠 <span style="color:#00ff41">Analysis Agent</span></div>
    <div style="border:2px solid #333;background:#0d0d1a;padding:5px 7px;margin:3px 0;font-size:10px">
      ⚡ <span style="color:#555">Signal Agent</span></div>
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
    prompt=f"""คุณคือนักวิเคราะห์ Forex วิเคราะห์ข่าวและสรุปผลกระทบต่อ: {", ".join(pairs)}
ข่าว:\n{news_text}
ตอบในรูปแบบ (ภาษาไทย):
OVERVIEW: <สรุป 2-3 ประโยค>
PAIRS:
{chr(10).join(f"{p}: <BULLISH/BEARISH/NEUTRAL> | <เหตุผล 1 ประโยค>" for p in pairs)}
WATCH: <ข่าวที่ต้องติดตาม>"""
    r=client.messages.create(model="claude-opus-4-5",max_tokens=800,
        messages=[{"role":"user","content":prompt}])
    return r.content[0].text

def parse_result(text,pairs):
    overview,signals,watch,section="",{},"",""
    for line in text.strip().split("\n"):
        if   line.startswith("OVERVIEW:"): overview=line.replace("OVERVIEW:","").strip()
        elif line.startswith("WATCH:"):    watch=line.replace("WATCH:","").strip()
        elif line.startswith("PAIRS:"):    section="pairs"
        elif section=="pairs" and "|" in line:
            for p in pairs:
                if p in line:
                    pts=line.split("|")
                    sig=pts[0].split(":")[-1].strip().upper()
                    reason=pts[1].strip() if len(pts)>1 else ""
                    if   "BULLISH" in sig: signals[p]=("BULLISH",reason)
                    elif "BEARISH" in sig: signals[p]=("BEARISH",reason)
                    else:                  signals[p]=("NEUTRAL",reason)
    return overview,signals,watch

# ── build agent data for JS ──
def build_agents_js(pairs, signals):
    tints=['#44aaff','#ffaa44','#aa88ff','#44ffaa','#ffdd44','#ff88aa']
    agents=[]
    positions=[(2.3,2.8),(4.8,4.2),(1.5,5.0),(5.5,2.0),(3.5,5.5),(2.5,4.5)]
    for i,p in enumerate(pairs):
        sig,reason=signals.get(p,("NEUTRAL","Analyzing..."))
        msgs_map={
            "BULLISH":[f"{p}!","▲ BUY!","Bullish!","Going UP!"],
            "BEARISH":[f"{p}!","▼ SELL!","Bearish!","Going DOWN!"],
            "NEUTRAL":[f"{p}","◆ NEUTRAL","Watching...","No signal"],
        }
        msgs=msgs_map.get(sig,["..."])
        gx,gy=positions[i%len(positions)]
        agents.append({
            "pair":p,"signal":sig,"reason":reason,
            "gx":gx,"gy":gy,"tint":tints[i%len(tints)],
            "msgs":msgs,"fr":i*25,"walking":True,"dir":1 if i%2==0 else -1
        })
    return agents

# ── canvas HTML ──
def render_canvas(agents_data):
    agents_json = str(agents_data).replace("True","true").replace("False","false").replace("'",'"')
    return f"""
<canvas id="fc" style="width:100%;image-rendering:pixelated;display:block;border:3px solid #2a3f6a"></canvas>
<script>
const W=680,H=480;
const cv=document.getElementById('fc');
cv.width=W;cv.height=H;
const ctx=cv.getContext('2d');
ctx.imageSmoothingEnabled=false;

const AGENTS={agents_json};
let tick=0;

function isoX(x,y){{return W/2+(x-y)*32;}}
function isoY(x,y){{return 75+(x+y)*16;}}

function poly(pts,col){{
  ctx.beginPath();ctx.moveTo(pts[0][0],pts[0][1]);
  for(let i=1;i<pts.length;i++)ctx.lineTo(pts[i][0],pts[i][1]);
  ctx.closePath();ctx.fillStyle=col;ctx.fill();
  ctx.strokeStyle='rgba(0,0,0,0.2)';ctx.lineWidth=0.6;ctx.stroke();
}}

function isoFaces(gx,gy,gz,gw,gd,gh,tc,lc,rc){{
  const ox=isoX(gx,gy),oy=isoY(gx,gy);
  const TW=gw*32,TD=gd*32,TH=gh*16;
  poly([[ox,oy-TH],[ox+TW,oy+TW/2-TH],[ox+TW-TD,oy+TW/2+TD/2-TH],[ox-TD,oy+TD/2-TH]],tc);
  poly([[ox-TD,oy+TD/2-TH],[ox+TW-TD,oy+TW/2+TD/2-TH],[ox+TW-TD,oy+TW/2+TD/2],[ox-TD,oy+TD/2]],lc);
  poly([[ox+TW,oy+TW/2-TH],[ox+TW-TD,oy+TW/2+TD/2-TH],[ox+TW-TD,oy+TW/2+TD/2],[ox+TW,oy+TW/2]],rc);
}}

function drawRoom(){{
  // floor
  for(let x=0;x<8;x++) for(let y=0;y<8;y++){{
    const a=(x+y)%2===0;
    const ox=isoX(x,y),oy=isoY(x,y);
    poly([[ox,oy-16],[ox+32,oy],[ox,oy+16],[ox-32,oy]],a?'#c8956c':'#b8845c');
  }}
  // walls
  for(let x=0;x<8;x++) isoFaces(x,-0.5,0,1,0.08,4,'#d4c4b0','#b8a898','#c0b0a0');
  for(let y=0;y<8;y++) isoFaces(-0.5,y,0,0.08,1,4,'#d4c4b0','#b8a898','#c0b0a0');
  // bookshelf
  isoFaces(0,0,0,2,0.6,3,'#8B5E3C','#6B4522','#7a5030');
  const bc=['#c0392b','#2980b9','#27ae60','#8e44ad','#e67e22','#e74c3c','#3498db'];
  for(let s=0;s<3;s++){{
    isoFaces(0.05,0.05,s+0.3,1.9,0.5,0.1,'#9a6a3a','#7a4a2a','#8a5a30');
    for(let b=0;b<5;b++) isoFaces(0.1+b*0.35,0.08,s+0.4,0.28,0.45,0.7,bc[(s*5+b)%7],bc[(s*5+b+1)%7],bc[(s*5+b+2)%7]);
  }}
  // desk 1
  isoFaces(1,1,0,2.5,1.2,0.7,'#9a6a3a','#7a4a2a','#8a5a30');
  isoFaces(1,1,0.7,2.5,1.2,0.08,'#c8956c','#a87550','#b88560');
  isoFaces(1.3,1.1,0.78,1,0.15,1.2,'#2a2a3a','#1a1a2a','#222232');
  isoFaces(1.35,1.13,0.9,0.9,0.08,0.9,'#0a2040','#072030','#0a1830');
  const sx=isoX(1.4,1.14),sy=isoY(1.4,1.14)-0.9*16;
  ctx.fillStyle='#00ff41';
  for(let i=0;i<5;i++) ctx.fillRect(sx-8+i*2,sy-i*4+16,20+i*3,1.5);
  isoFaces(1.7,1.12,0.7,0.3,0.1,0.2,'#333','#222','#2a2a2a');
  isoFaces(2.2,1.2,0.72,0.8,0.5,0.06,'#888','#666','#777');
  // desk 2
  isoFaces(4,3,0,2,1.2,0.7,'#9a6a3a','#7a4a2a','#8a5a30');
  isoFaces(4,3,0.7,2,1.2,0.08,'#c8956c','#a87550','#b88560');
  isoFaces(4.3,3.2,0.78,0.9,0.7,0.06,'#888','#666','#777');
  isoFaces(4.3,3.2,0.84,0.9,0.08,0.5,'#2a2a3a','#1a1a2a','#222232');
  const lx=isoX(4.35,3.22),ly=isoY(4.35,3.22)-0.84*16;
  ctx.fillStyle='#4a9eff';ctx.fillRect(lx-5,ly-4,18,2);
  ctx.fillStyle='#00ff41';ctx.fillRect(lx-5,ly,14,2);
  // plant big
  isoFaces(6.5,0.5,0,0.4,0.4,0.5,'#c0522a','#a03a1a','#b04422');
  const px=isoX(6.7,0.7),py=isoY(6.7,0.7)-8;
  ctx.fillStyle='#2d7a1b';
  ctx.beginPath();ctx.ellipse(px-6,py-14,7,12,-.3,0,Math.PI*2);ctx.fill();
  ctx.beginPath();ctx.ellipse(px+6,py-12,6,10,.3,0,Math.PI*2);ctx.fill();
  ctx.beginPath();ctx.ellipse(px,py-18,5,14,0,0,Math.PI*2);ctx.fill();
  ctx.fillStyle='#3a9a22';ctx.beginPath();ctx.ellipse(px-3,py-16,4,8,-.2,0,Math.PI*2);ctx.fill();
  // plant desk
  isoFaces(3.3,1.1,0.78,0.25,0.25,0.35,'#8B4513','#6B3010','#7a3f10');
  const dp=isoX(3.42,1.22),dpy=isoY(3.42,1.22)-13;
  ctx.fillStyle='#2d7a1b';ctx.beginPath();ctx.ellipse(dp,dpy-6,6,8,0,0,Math.PI*2);ctx.fill();
  ctx.fillStyle='#3a9a22';ctx.beginPath();ctx.ellipse(dp-3,dpy-4,4,5,-.3,0,Math.PI*2);ctx.fill();
  // whiteboard
  isoFaces(3,0,1.5,2,0.08,1.5,'#f0f0e8','#e0e0d8','#e8e8e0');
  const wx=isoX(3.1,-0.01),wy=isoY(3.1,-0.01)-1.5*16;
  ctx.fillStyle='#2980b9';ctx.font='5px monospace';ctx.fillText('FOREX SIGNALS',wx-12,wy+8);
  ctx.fillStyle='#00c853';ctx.fillRect(wx-8,wy+12,22,2);
  ctx.fillStyle='#ff3131';ctx.fillRect(wx-8,wy+17,16,2);
  ctx.fillStyle='#ffd700';ctx.fillRect(wx-8,wy+22,20,2);
  // window
  isoFaces(-0.06,3,1,0.06,1.5,1.5,'#87ceeb','#6aadcc','#78bedd');
  // chairs
  isoFaces(2,2.2,0,0.7,0.7,0.5,'#1a1a2e','#0d0d1a','#141428');
  isoFaces(2,2.2,0.5,0.7,0.7,0.08,'#333','#222','#2a2a2a');
  isoFaces(2,2.2,0.58,0.7,0.1,0.8,'#1a1a2e','#0d0d1a','#141428');
  isoFaces(5,4.5,0,0.7,0.7,0.5,'#1a1a2e','#0d0d1a','#141428');
  isoFaces(5,4.5,0.5,0.7,0.7,0.08,'#333','#222','#2a2a2a');
  isoFaces(5,4.5,0.58,0.7,0.1,0.8,'#1a1a2e','#0d0d1a','#141428');
  // shelf top
  isoFaces(5.5,0.2,1,1.5,0.3,0.1,'#8B5E3C','#6B4522','#7a5030');
  isoFaces(5.5,0.2,2,1.5,0.3,0.1,'#8B5E3C','#6B4522','#7a5030');
  isoFaces(5.6,0.22,1.1,0.3,0.2,0.4,'#c0392b','#a02a1a','#b0321a');
  isoFaces(6.0,0.22,1.1,0.2,0.2,0.5,'#2980b9','#1a6090','#2270a0');
  isoFaces(6.4,0.22,1.1,0.25,0.2,0.3,'#27ae60','#1a8040','#229850');
  // glow
  const grad=ctx.createRadialGradient(isoX(3.5,3.5),isoY(3.5,3.5),5,isoX(3.5,3.5),isoY(3.5,3.5),100);
  grad.addColorStop(0,'rgba(255,240,180,0.15)');
  grad.addColorStop(1,'rgba(255,240,180,0)');
  ctx.fillStyle=grad;
  ctx.beginPath();ctx.ellipse(isoX(3.5,3.5),isoY(3.5,3.5),100,55,0,0,Math.PI*2);ctx.fill();
}}

function drawBubble(px,py,text,sig){{
  const col=sig==='BULLISH'?'#00c853':sig==='BEARISH'?'#ff3131':'#ffd700';
  ctx.font='5px "Press Start 2P",monospace';
  const tw=ctx.measureText(text).width;
  const bw=tw+14,bh=18;
  const bx=px-bw/2,by=py-bh-14;
  ctx.fillStyle='#fff';ctx.fillRect(bx-2,by-2,bw+4,bh+4);
  ctx.fillStyle='#000';ctx.fillRect(bx,by,bw,bh);
  ctx.fillStyle=col;ctx.fillRect(bx,by,bw,3);
  ctx.fillStyle='#fff';ctx.font='5px "Press Start 2P",monospace';
  ctx.fillText(text,bx+7,by+13);
  ctx.fillStyle='#fff';ctx.beginPath();ctx.moveTo(px-4,by+bh+2);ctx.lineTo(px+4,by+bh+2);ctx.lineTo(px,by+bh+10);ctx.fill();
  ctx.fillStyle='#000';ctx.beginPath();ctx.moveTo(px-2,by+bh+2);ctx.lineTo(px+2,by+bh+2);ctx.lineTo(px,by+bh+8);ctx.fill();
}}

function drawAstro(gx,gy,sig,tint,fr,walking){{
  const px=isoX(gx,gy),py=isoY(gx,gy)-14;
  const S=2.2,bob=walking?Math.sin(fr*0.25)*1.2:0,lsw=walking?Math.sin(fr*0.25)*2:0,asw=walking?Math.sin(fr*0.25)*1.5:0;
  const p=(ox,oy,w,h,col)=>{{ctx.fillStyle=col;ctx.fillRect(Math.round(px+ox*S),Math.round(py+(oy+bob)*S),Math.ceil(w*S),Math.ceil(h*S));}};
  ctx.fillStyle='rgba(0,0,0,0.2)';ctx.beginPath();ctx.ellipse(px+7*S,py+25*S,6*S,2*S,0,0,Math.PI*2);ctx.fill();
  p(2,21+lsw,4,2,'#556');p(8,21-lsw,4,2,'#556');
  p(3,16+lsw,3,6,'#ccd');p(8,16-lsw,3,6,'#ccd');
  p(2,9,10,8,'#dde');p(3,10,8,6,'#eef');p(5,11,4,3,'#bbc');p(6,12,2,2,tint+'55');
  p(1,10,2,6,'#99a');p(11,10,2,6,'#99a');
  p(0,10+asw,2,6,'#ccd');p(12,10-asw,2,6,'#ccd');
  p(8,7,3,3,'#f8c8a0');
  p(3,1,8,8,'#dde');p(2,3,10,5,'#dde');
  const vc=sig==='BULLISH'?'#00aaff':sig==='BEARISH'?'#ff5555':'#ffcc44';
  p(4,2,6,6,vc+'cc');p(5,3,4,4,'#ffffff33');
  p(5,5,2,2,'#fff');p(9,5,2,2,'#fff');p(5,5,1,1,'#111');p(9,5,1,1,'#111');
  if(sig==='BULLISH'){{p(6,8,4,1,'#fff');p(5,7,1,1,'#fff');p(10,7,1,1,'#fff');}}
  else if(sig==='BEARISH'){{p(6,8,4,1,'#fff');p(5,9,1,1,'#fff');p(10,9,1,1,'#fff');}}
  else{{p(6,8,4,1,'#fff');}}
  p(8,0,1,2,'#aab');
  ctx.fillStyle=tint;ctx.beginPath();ctx.arc(px+8.5*S,py+bob*S,2.5*S,0,Math.PI*2);ctx.fill();
  return {{px:px+7*S,py:py}};
}}

function updateAgents(){{
  AGENTS.forEach(a=>{{
    if(a.walking){{
      a.gx+=a.dir*0.012;a.gy+=a.dir*0.004;a.fr+=1;
      if(a.gx>6.5){{a.gx=6.5;a.dir=-1;}}
      if(a.gx<0.8){{a.gx=0.8;a.dir=1;}}
    }}
    if(Math.random()<0.003){{a.walking=false;setTimeout(()=>a.walking=true,2000+Math.random()*2000);}}
  }});
}}

function depthSort(arr){{return [...arr].sort((a,b)=>(a.gx+a.gy)-(b.gx+b.gy));}}

function loop(){{
  tick++;
  ctx.clearRect(0,0,W,H);
  ctx.fillStyle='#1a1a2e';ctx.fillRect(0,0,W,H);
  drawRoom();
  updateAgents();
  depthSort(AGENTS).forEach((a,i)=>{{
    const pos=drawAstro(a.gx,a.gy,a.signal,a.tint,a.fr,a.walking);
    const msgIdx=Math.floor((tick+i*35)/90)%a.msgs.length;
    drawBubble(pos.px,pos.py,a.msgs[msgIdx],a.signal);
  }});
  // clock
  const n=new Date();
  const ts=n.getHours().toString().padStart(2,'0')+':'+n.getMinutes().toString().padStart(2,'0')+':'+n.getSeconds().toString().padStart(2,'0');
  ctx.fillStyle='rgba(0,0,0,0.8)';ctx.fillRect(W-90,6,84,16);
  ctx.fillStyle='#00ff41';ctx.font='7px "Press Start 2P",monospace';ctx.fillText(ts,W-84,18);
  requestAnimationFrame(loop);
}}
loop();
</script>
"""

# ── main ──
if not run_btn:
    # default agents (neutral)
    default_agents=[{
        "pair":p,"signal":"NEUTRAL","reason":"Awaiting analysis",
        "gx":pos[0],"gy":pos[1],"tint":t,
        "msgs":["Analyzing...","Waiting...","Stand by","Loading..."],
        "fr":i*25,"walking":True,"dir":1 if i%2==0 else -1
    } for i,(p,pos,t) in enumerate(zip(
        ["EUR/USD","USD/THB","USD/JPY","GBP/USD","XAU/USD"],
        [(2.3,2.8),(4.8,4.2),(1.5,5.0),(5.5,2.0),(3.5,5.5)],
        ['#44aaff','#ffaa44','#aa88ff','#44ffaa','#ffdd44']
    ))]
    st.components.v1.html(render_canvas(default_agents), height=500, scrolling=False)
    st.markdown("""
    <div style="text-align:center;font-family:'Press Start 2P',monospace;font-size:7px;color:#333;padding:10px;letter-spacing:0.1em">
      ← INSERT API KEY AND PRESS ANALYZE NOW
    </div>""", unsafe_allow_html=True)

else:
    if not api_key:
        st.markdown('<div style="border:2px solid #ff3131;padding:10px;font-family:\'Press Start 2P\',monospace;font-size:7px;color:#ff3131">❌ NO API KEY</div>', unsafe_allow_html=True)
    elif not selected_pairs:
        st.markdown('<div style="border:2px solid #ff3131;padding:10px;font-family:\'Press Start 2P\',monospace;font-size:7px;color:#ff3131">❌ SELECT PAIRS</div>', unsafe_allow_html=True)
    else:
        # loading agents
        loading_agents=[{
            "pair":p,"signal":"NEUTRAL","reason":"Fetching...",
            "gx":pos[0],"gy":pos[1],"tint":t,
            "msgs":["Fetching!","Reading news","Analyzing!","Working..."],
            "fr":i*25,"walking":True,"dir":1 if i%2==0 else -1
        } for i,(p,pos,t) in enumerate(zip(
            selected_pairs,
            [(2.3,2.8),(4.8,4.2),(1.5,5.0),(5.5,2.0),(3.5,5.5),(2.0,4.0)],
            ['#44aaff','#ffaa44','#aa88ff','#44ffaa','#ffdd44','#ff88aa']
        ))]
        canvas_ph=st.empty()
        canvas_ph.components.v1.html(render_canvas(loading_agents),height=500,scrolling=False)

        with st.spinner(""):
            articles=fetch_news()
            raw=analyze(articles,selected_pairs,api_key)
            overview,signals,watch=parse_result(raw,selected_pairs)

        # final agents with real signals
        final_agents=build_agents_js(selected_pairs,signals)
        canvas_ph.empty()
        st.components.v1.html(render_canvas(final_agents),height=500,scrolling=False)

        # signal cards below canvas
        cols=st.columns(len(selected_pairs))
        for i,(p,col) in enumerate(zip(selected_pairs,cols)):
            sig,reason=signals.get(p,("NEUTRAL","No data"))
            sc="#00c853" if sig=="BULLISH" else "#ff3131" if sig=="BEARISH" else "#ffd700"
            arrow="▲" if sig=="BULLISH" else "▼" if sig=="BEARISH" else "◆"
            with col:
                st.markdown(f"""
                <div style="background:#0d0d1a;border:2px solid {sc};padding:8px;text-align:center">
                  <div style="font-family:'Press Start 2P',monospace;font-size:6px;color:#888;margin-bottom:4px">{p}</div>
                  <div style="font-family:'Press Start 2P',monospace;font-size:7px;color:{sc};border:1px solid {sc};padding:2px 4px;display:inline-block">{arrow} {sig}</div>
                  <div style="font-family:'Press Start 2P',monospace;font-size:5px;color:#555;margin-top:4px;line-height:1.6">{reason[:40]}</div>
                </div>""", unsafe_allow_html=True)

        if overview:
            st.markdown(f"""
            <div style="background:#0d0d1a;border:2px solid #4a9eff;padding:10px;margin-top:8px">
              <div style="font-family:'Press Start 2P',monospace;font-size:7px;color:#4a9eff;margin-bottom:6px">📋 OVERVIEW</div>
              <div style="font-family:'Press Start 2P',monospace;font-size:6px;color:#ccc;line-height:1.8">{overview}</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("""
        <div style="border:2px dashed #ff3131;padding:6px 10px;font-family:'Press Start 2P',monospace;font-size:6px;color:#ff3131;margin-top:8px">
        ⚠ NOT FINANCIAL ADVICE · FOR EDUCATIONAL PURPOSES ONLY
        </div>""", unsafe_allow_html=True)
