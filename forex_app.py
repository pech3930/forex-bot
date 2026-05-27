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
.scanline{background:repeating-linear-gradient(0deg,transparent,transparent 2px,rgba(0,0,0,0.04) 2px,rgba(0,0,0,0.04) 4px);
  pointer-events:none;position:fixed;top:0;left:0;width:100%;height:100%;z-index:9999}
</style>
<div class="scanline"></div>
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
    positions=[(3,4),(7,4),(11,4),(3,8),(7,8),(11,8)]
    agents=[]
    for i,p in enumerate(pairs):
        sig,reason=signals.get(p,("NEUTRAL","Analyzing..."))
        msgs={"BULLISH":[p+"!","▲ BUY!","Bullish!","UP!"],
              "BEARISH":[p+"!","▼ SELL!","Bearish!","DOWN!"],
              "NEUTRAL":[p,"◆ WAIT","Watch","..."]}.get(sig,["..."])
        tx,ty=positions[i%len(positions)]
        agents.append({"pair":p,"signal":sig,"reason":reason,
                       "tx":float(tx),"ty":float(ty),
                       "tint":tints[i%len(tints)],"msgs":msgs,"fr":i*20,
                       "walking":True,"dir":1 if i%2==0 else -1})
    return agents

def render_canvas(agents, asset_url, sprite_url):
    agents_json=str(agents).replace("True","true").replace("False","false").replace("'",'"')
    return f"""
<style>
html,body{{margin:0;padding:0;background:#2a1a0e;overflow:hidden}}
canvas{{display:block;image-rendering:pixelated}}
</style>
<canvas id="fc"></canvas>
<script>
const ASSET_URL="{asset_url}";
const SPRITE_URL="{sprite_url}";
const AGENTS={agents_json};
const cv=document.getElementById('fc');
const ctx=cv.getContext('2d');
ctx.imageSmoothingEnabled=false;

cv.width=window.innerWidth||860;
cv.height=Math.round(cv.width*0.62);
window.addEventListener('resize',()=>{{
  cv.width=window.innerWidth||860;
  cv.height=Math.round(cv.width*0.62);
}});

// ── tile config ──
// all_assets.png = 448x240, 16x16 per tile
const T=16, S=3; // tile size, scale
const TW=T*S;   // tile on screen = 48px

// ── load images ──
const assets=new Image();
assets.crossOrigin='anonymous';
assets.src=ASSET_URL;
let assetsOK=false;
assets.onload=()=>{{ assetsOK=true; console.log('assets loaded',assets.width,assets.height); }};
assets.onerror=()=>console.error('assets failed');

const spr=new Image();
spr.crossOrigin='anonymous';
spr.src=SPRITE_URL;
let sprOK=false, FW=0, FH=0;
spr.onload=()=>{{
  sprOK=true;
  FW=Math.round(spr.width/12);
  FH=spr.height;
  console.log('sprite loaded',spr.width,spr.height,'frame',FW,FH);
}};

let tick=0;

// ── room layout ──
const ROOM_COLS=16, ROOM_ROWS=12;
function rx(){{ return Math.floor((cv.width - ROOM_COLS*TW)/2); }}
function ry(){{ return Math.floor((cv.height - ROOM_ROWS*TW)/2); }}

// draw tile from spritesheet
function dt(srcX,srcY,dstX,dstY,w=1,h=1){{
  if(!assetsOK) return;
  ctx.drawImage(assets,
    srcX*T, srcY*T, T*w, T*h,
    rx()+dstX*TW, ry()+dstY*TW, TW*w, TW*h);
}}

// draw solid colored tile
function fillTile(dstX,dstY,col,w=1,h=1){{
  ctx.fillStyle=col;
  ctx.fillRect(rx()+dstX*TW, ry()+dstY*TW, TW*w, TW*h);
}}

function drawRoom(){{
  // ── floor ──
  for(let x=0;x<ROOM_COLS;x++) for(let y=0;y<ROOM_ROWS;y++){{
    ctx.fillStyle=(x+y)%2===0?'#c8a870':'#b89860';
    ctx.fillRect(rx()+x*TW, ry()+y*TW, TW, TW);
    // subtle grid
    ctx.strokeStyle='rgba(0,0,0,0.08)';
    ctx.lineWidth=1;
    ctx.strokeRect(rx()+x*TW, ry()+y*TW, TW, TW);
  }}

  // ── walls ──
  // top wall
  ctx.fillStyle='#d8c8a8';
  ctx.fillRect(rx(), ry()-TW, ROOM_COLS*TW, TW);
  // left wall
  ctx.fillRect(rx()-TW, ry(), TW, ROOM_ROWS*TW);
  // wall top border
  ctx.fillStyle='#6b5a3a';
  ctx.fillRect(rx(), ry(), ROOM_COLS*TW, 4);
  ctx.fillRect(rx(), ry(), 4, ROOM_ROWS*TW);
  ctx.fillRect(rx(), ry()+ROOM_ROWS*TW-4, ROOM_COLS*TW, 4);
  ctx.fillRect(rx()+ROOM_COLS*TW-4, ry(), 4, ROOM_ROWS*TW);

  if(!assetsOK){{
    // fallback: draw colored boxes if assets not loaded yet
    ctx.fillStyle='#8B5E3C'; ctx.fillRect(rx()+TW,ry()+TW,TW*3,TW*2);
    ctx.fillStyle='#8B5E3C'; ctx.fillRect(rx()+TW*5,ry()+TW,TW*3,TW*2);
    ctx.fillStyle='#8B5E3C'; ctx.fillRect(rx()+TW*9,ry()+TW,TW*3,TW*2);
    return;
  }}

  // ── DESKS: use col 0-5, row 0-3 from assets (brown L-desk) ──
  // Top row desks
  dt(0,0, 1,1, 4,3);   // big desk top-left area
  dt(0,0, 6,1, 4,3);   // big desk top-mid
  dt(0,0,11,1, 4,3);   // big desk top-right

  // Middle row desks
  dt(0,0, 1,5, 4,3);
  dt(0,0, 6,5, 4,3);
  dt(0,0,11,5, 4,3);

  // Bottom row desks
  dt(0,0, 1,9, 4,3);
  dt(0,0, 6,9, 4,3);
  dt(0,0,11,9, 4,3);

  // ── COMPUTERS: col 7-8, row 0-2 ──
  dt(7,0, 2,0, 2,2);
  dt(7,0, 7,0, 2,2);
  dt(7,0,12,0, 2,2);
  dt(7,0, 2,4, 2,2);
  dt(7,0, 7,4, 2,2);
  dt(7,0,12,4, 2,2);
  dt(7,0, 2,8, 2,2);
  dt(7,0, 7,8, 2,2);
  dt(7,0,12,8, 2,2);

  // ── PLANTS: col 0-7, row 6-8 ──
  dt(0,6, 0,0, 1,2);    // corner plant TL
  dt(2,6,15,0, 1,2);    // corner plant TR
  dt(4,6, 0,10,1,2);    // corner plant BL
  dt(6,6,15,10,1,2);    // corner plant BR
  dt(1,6, 5,0, 1,2);    // center top plant
  dt(3,6,10,0, 1,2);
  dt(5,6, 5,10,1,2);
  dt(7,6,10,10,1,2);

  // ── BOOKSHELF right wall: col 10-11, row 0-5 ──
  dt(10,0,14,1, 2,5);
  dt(10,0,14,6, 2,5);

  // ── BOSS/chart board: col 17-20, row 3-5 ──
  dt(17,3, 6,0, 4,2);

  // ── water cooler: col 9, row 2-3 ──
  dt(9,2,13,4, 1,2);

  // ── misc desk items ──
  dt(9,0, 3,2, 1,1);   // papers
  dt(9,1, 4,2, 1,1);   // coffee
  dt(9,0, 8,2, 1,1);
  dt(9,1, 9,2, 1,1);
  dt(9,0, 3,6, 1,1);
  dt(9,1, 4,6, 1,1);

  // ── trash bins ──
  dt(13,6, 0,5, 1,1);
  dt(13,6,15,5, 1,1);
  dt(13,6, 0,11,1,1);
  dt(13,6,15,11,1,1);

  // ── ambient light ──
  const grad=ctx.createRadialGradient(
    rx()+ROOM_COLS*TW/2, ry()+ROOM_ROWS*TW/2, 10,
    rx()+ROOM_COLS*TW/2, ry()+ROOM_ROWS*TW/2, ROOM_COLS*TW*0.6);
  grad.addColorStop(0,'rgba(255,245,200,0.1)');
  grad.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=grad;
  ctx.fillRect(rx(),ry(),ROOM_COLS*TW,ROOM_ROWS*TW);
}}

// ── sprite helpers ──
const WALK=[8,9,10,11], STAND=8;

function drawSprite(px,py,frame,dir,tint){{
  if(!sprOK||FW===0) return;
  const dw=FW*S, dh=FH*S;
  ctx.save();
  if(dir<0){{ctx.translate(px+dw,py);ctx.scale(-1,1);ctx.drawImage(spr,frame*FW,0,FW,FH,0,0,dw,dh);}}
  else ctx.drawImage(spr,frame*FW,0,FW,FH,px,py,dw,dh);
  ctx.globalCompositeOperation='multiply';
  ctx.globalAlpha=0.2;
  ctx.fillStyle=tint;
  ctx.fillRect(dir<0?0:px,py,dw,dh);
  ctx.globalCompositeOperation='source-over';
  ctx.globalAlpha=1;
  ctx.restore();
}}

function drawBubble(px,py,text,sig){{
  const col=sig==='BULLISH'?'#00c853':sig==='BEARISH'?'#ff3131':'#ffd700';
  ctx.font='5px "Press Start 2P",monospace';
  const tw=ctx.measureText(text).width;
  const bw=tw+14,bh=18,bx=px-bw/2,by=py-bh-10;
  ctx.fillStyle='#fff';ctx.fillRect(bx-2,by-2,bw+4,bh+4);
  ctx.fillStyle='#000';ctx.fillRect(bx,by,bw,bh);
  ctx.fillStyle=col;ctx.fillRect(bx,by,bw,3);
  ctx.fillStyle='#fff';ctx.font='5px "Press Start 2P",monospace';
  ctx.fillText(text,bx+7,by+13);
  ctx.fillStyle='#fff';ctx.beginPath();ctx.moveTo(px-4,by+bh+2);ctx.lineTo(px+4,by+bh+2);ctx.lineTo(px,by+bh+10);ctx.fill();
  ctx.fillStyle='#000';ctx.beginPath();ctx.moveTo(px-2,by+bh+2);ctx.lineTo(px+2,by+bh+2);ctx.lineTo(px,by+bh+8);ctx.fill();
}}

function drawAgent(a){{
  if(!sprOK||FW===0) return;
  const dw=FW*S,dh=FH*S;
  const px=rx()+a.tx*TW+(TW-dw)/2;
  const py=ry()+a.ty*TW+(TW-dh);
  const frame=a.walking?WALK[Math.floor(a.fr/6)%4]:STAND;
  ctx.fillStyle='rgba(0,0,0,0.15)';
  ctx.beginPath();ctx.ellipse(px+dw/2,py+dh,dw/2.5,3,0,0,Math.PI*2);ctx.fill();
  drawSprite(px,py,frame,a.dir,a.tint);
  const sc=a.signal==='BULLISH'?'#00c853':a.signal==='BEARISH'?'#ff3131':'#ffd700';
  ctx.fillStyle='rgba(0,0,0,0.8)';ctx.fillRect(px,py+dh+1,dw,10);
  ctx.fillStyle=sc;ctx.font='5px monospace';ctx.textAlign='center';
  ctx.fillText(a.pair,px+dw/2,py+dh+9);ctx.textAlign='left';
  const mi=Math.floor((tick+AGENTS.indexOf(a)*35)/90)%a.msgs.length;
  drawBubble(px+dw/2,py,a.msgs[mi],a.signal);
}}

function updateAgents(){{
  AGENTS.forEach(a=>{{
    if(a.walking){{
      a.tx+=a.dir*0.025; a.fr+=1;
      if(a.tx>ROOM_COLS-2){{a.tx=ROOM_COLS-2;a.dir=-1;}}
      if(a.tx<1){{a.tx=1;a.dir=1;}}
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
  ctx.fillStyle='#1a1208';
  ctx.fillRect(0,0,cv.width,cv.height);
  drawRoom();
  updateAgents();
  [...AGENTS].sort((a,b)=>a.ty-b.ty).forEach(a=>drawAgent(a));
  const n=new Date();
  const ts=n.getHours().toString().padStart(2,'0')+':'+
           n.getMinutes().toString().padStart(2,'0')+':'+
           n.getSeconds().toString().padStart(2,'0');
  ctx.fillStyle='rgba(0,0,0,0.85)';ctx.fillRect(cv.width-96,8,90,18);
  ctx.fillStyle='#00ff41';ctx.font='8px "Press Start 2P",monospace';
  ctx.fillText(ts,cv.width-90,21);
  requestAnimationFrame(loop);
}}
loop();
</script>
"""

ASSET_URL  = "https://raw.githubusercontent.com/pech3930/forex-bot/main/all_assets.png"
SPRITE_URL = "https://raw.githubusercontent.com/pech3930/forex-bot/main/Astronaut.png"

if not run_btn:
    default_agents=build_agents(
        selected_pairs if selected_pairs else ["EUR/USD","USD/THB","USD/JPY","GBP/USD","XAU/USD"],{})
    st.components.v1.html(render_canvas(default_agents,ASSET_URL,SPRITE_URL),height=620,scrolling=False)
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
        ph.components.v1.html(render_canvas(loading,ASSET_URL,SPRITE_URL),height=620,scrolling=False)
        with st.spinner(""):
            articles=fetch_news()
            raw=analyze(articles,selected_pairs,api_key)
            overview,signals,watch=parse_result(raw,selected_pairs)
        final=build_agents(selected_pairs,signals)
        ph.empty()
        st.components.v1.html(render_canvas(final,ASSET_URL,SPRITE_URL),height=620,scrolling=False)
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
