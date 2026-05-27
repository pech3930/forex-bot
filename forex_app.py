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

ข่าวสาร:
{news_text}

ตอบกลับในรูปแบบ JSON เท่านั้น:
{{
  "overview": "<สรุป 2-3 ประโยคภาษาไทย>",
  "signals": {{
    {", ".join(f'"{p}": {{"signal": "<BULLISH/BEARISH/NEUTRAL>", "reason": "<เหตุผล 1 ประโยคภาษาไทย>"}}' for p in pairs)}
  }},
  "watch": "<ประเด็นที่ต้องติดตาม>"
}}"""
    r=client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1000,
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
    # positions in tile coordinates (col, row) inside the office
    positions=[(5,4),(9,4),(5,8),(9,8),(7,6),(3,6)]
    agents=[]
    for i,p in enumerate(pairs):
        sig,reason=signals.get(p,("NEUTRAL","Analyzing..."))
        msgs={"BULLISH":[p+"!","▲ BUY!","Bullish!","Going UP!"],
              "BEARISH":[p+"!","▼ SELL!","Bearish!","Going DOWN!"],
              "NEUTRAL":[p,"◆ WAIT","Watching","No signal"]}.get(sig,["..."])
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

// ── sizing ──
const TILE=16, SCALE=3, TS=TILE*SCALE; // each tile 16px * 3 = 48px on screen
const COLS=16, ROWS=12; // room size in tiles
let tick=0;

function resize(){{
  cv.width=window.innerWidth||860;
  cv.height=Math.round(cv.width*0.65);
}}
resize();
window.addEventListener('resize',resize);

// ── load assets ──
const assets=new Image(); assets.crossOrigin='anonymous'; assets.src=ASSET_URL;
const spr=new Image();    spr.crossOrigin='anonymous';    spr.src=SPRITE_URL;
let assetsReady=false, spriteReady=false;
assets.onload=()=>assetsReady=true;
spr.onload=()=>spriteReady=true;

// room offset to center it
function roomX(){{ return Math.floor((cv.width - COLS*TS)/2); }}
function roomY(){{ return Math.floor((cv.height - ROWS*TS)/2); }}

// draw one tile from all_assets.png (448x240, 16x16 each => 28 cols x 15 rows)
// sx,sy = tile col,row in the spritesheet
function drawTile(sx,sy,dx,dy,w=1,h=1){{
  if(!assetsReady) return;
  ctx.drawImage(assets, sx*TILE, sy*TILE, TILE*w, TILE*h,
                        roomX()+dx*TS, roomY()+dy*TS, TS*w, TS*h);
}}

// ── floor & walls ──
function drawFloor(){{
  // floor color
  ctx.fillStyle='#c8a87a';
  ctx.fillRect(roomX(), roomY(), COLS*TS, ROWS*TS);

  // floor tile pattern
  for(let x=0;x<COLS;x++) for(let y=0;y<ROWS;y++){{
    if((x+y)%2===0){{
      ctx.fillStyle='rgba(0,0,0,0.04)';
      ctx.fillRect(roomX()+x*TS, roomY()+y*TS, TS, TS);
    }}
  }}

  // walls (top & left)
  ctx.fillStyle='#d4c4a8';
  ctx.fillRect(roomX(), roomY()-TS, COLS*TS, TS);     // top wall
  ctx.fillRect(roomX()-TS, roomY(), TS, ROWS*TS);     // left wall

  // wall border
  ctx.fillStyle='#8B7355';
  ctx.fillRect(roomX(), roomY(), COLS*TS, 3);         // top edge
  ctx.fillRect(roomX(), roomY(), 3, ROWS*TS);         // left edge
  ctx.fillRect(roomX(), roomY()+ROWS*TS-3, COLS*TS, 3); // bottom edge
  ctx.fillRect(roomX()+COLS*TS-3, roomY(), 3, ROWS*TS); // right edge

  // baseboard
  ctx.fillStyle='#a08060';
  ctx.fillRect(roomX(), roomY()+ROWS*TS-6, COLS*TS, 6);
  ctx.fillRect(roomX()+COLS*TS-6, roomY(), 6, ROWS*TS);
}}

// ── draw office furniture using asset tiles ──
// all_assets.png layout (measured from image):
// Row 0: floor tiles top-left area
// Row 0-3 col 0-3: L-shaped desk top-left
// Row 0-1 col 0-5: big desk top
// Row 3-5 col 0-2: cabinet/shelf left
// Row 6-8 col 0-2: small furniture
// Row 0-2 col 7-9: computer setup
// Row 3-5 col 7-10: misc items
// Row 6-9 col 0-8: plants row
// Row 0-5 col 10-17: various items right side

function drawFurniture(){{
  if(!assetsReady) return;

  // ── DESKS (top-left of asset = brown desk, 2x2 tiles) ──
  // Desk 1 - top area
  drawTile(0,0, 1,1, 2,2);   // brown desk top-left
  drawTile(0,0, 4,1, 2,2);   // desk copy

  // Desk 2 - middle
  drawTile(0,3, 1,5, 2,2);
  drawTile(0,3, 4,5, 2,2);
  drawTile(0,3, 7,5, 2,2);

  // Desk 3 - bottom row
  drawTile(0,0, 1,9, 2,2);
  drawTile(0,0, 4,9, 2,2);
  drawTile(0,0, 10,9, 2,2);

  // ── COMPUTERS on desks (col 7-9, row 0-2 in assets) ──
  drawTile(7,0, 2,0, 2,2);   // computer on desk1
  drawTile(7,0, 5,0, 2,2);   // computer on desk2
  drawTile(7,0, 2,4, 2,2);   // computer on desk3
  drawTile(7,0, 5,4, 2,2);
  drawTile(7,0, 8,4, 2,2);
  drawTile(7,0, 2,8, 2,2);
  drawTile(7,0, 5,8, 2,2);
  drawTile(7,0,11,8, 2,2);

  // ── CHAIRS (col 13-14, row 0-2 in assets) ──
  drawTile(13,0, 2,3, 1,2);
  drawTile(13,0, 5,3, 1,2);
  drawTile(13,0, 2,7, 1,2);
  drawTile(13,0, 5,7, 1,2);
  drawTile(13,0, 8,7, 1,2);
  drawTile(13,0, 2,11,1,2);
  drawTile(13,0, 5,11,1,2);
  drawTile(13,0,11,11,1,2);

  // ── PLANTS row (row 6-8 col 0-8 in assets) ──
  drawTile(0,6,  0,0, 1,2);   // plant corner top-left
  drawTile(2,6, 15,0, 1,2);   // plant corner top-right
  drawTile(4,6,  0,10,1,2);   // plant corner bottom-left
  drawTile(6,6, 15,10,1,2);   // plant corner bottom-right
  drawTile(1,6,  7,0, 1,2);   // desk plant center top
  drawTile(3,6, 13,5, 1,2);   // plant right side

  // ── BOOKSHELF / cabinet right wall ──
  drawTile(10,0, 13,0, 2,3);  // bookshelf right top
  drawTile(10,0, 13,3, 2,3);  // bookshelf right bottom

  // ── whiteboard / BOSS sign ──
  drawTile(17,3,  8,0, 2,1);  // BOSS board
  drawTile(18,3, 10,0, 2,2);  // chart board

  // ── misc items on desks ──
  drawTile(9,0,  3,1, 1,1);   // papers
  drawTile(9,1,  6,1, 1,1);   // coffee
  drawTile(9,0,  9,5, 1,1);   // papers
  drawTile(9,1,  3,5, 1,1);   // coffee

  // ── water cooler ──
  drawTile(9,2, 12,4, 1,2);

  // ── trash bin ──
  drawTile(13,6, 14,10,1,1);
  drawTile(13,6,  0,4, 1,1);
}}

// ── ambient light overlay ──
function drawLight(){{
  const cx=roomX()+cv.width*0.5-roomX();
  const cy=roomY()+ROWS*TS*0.4;
  const grad=ctx.createRadialGradient(roomX()+COLS*TS/2,roomY()+ROWS*TS/2,20,
                                       roomX()+COLS*TS/2,roomY()+ROWS*TS/2,COLS*TS*0.7);
  grad.addColorStop(0,'rgba(255,240,200,0.08)');
  grad.addColorStop(1,'rgba(255,240,200,0)');
  ctx.fillStyle=grad;
  ctx.fillRect(roomX(),roomY(),COLS*TS,ROWS*TS);
}}

// ── Astronaut sprite ──
const WALK_FRAMES=[8,9,10,11];
const STAND_FRAME=8;
const TOTAL_FRAMES=12;
let FW=0,FH=0;

function getSpriteSize(){{
  if(!spriteReady||spr.width===0) return {{fw:16,fh:24}};
  if(FW===0){{FW=Math.round(spr.width/TOTAL_FRAMES);FH=spr.height;}}
  return {{fw:FW,fh:FH}};
}}

function drawSprite(px,py,frameIdx,dir,tint){{
  const {{fw,fh}}=getSpriteSize();
  if(!spriteReady||fw===0) return;
  const dw=fw*SCALE,dh=fh*SCALE;
  ctx.save();
  if(dir<0){{ctx.translate(px+dw,py);ctx.scale(-1,1);ctx.drawImage(spr,frameIdx*fw,0,fw,fh,0,0,dw,dh);}}
  else ctx.drawImage(spr,frameIdx*fw,0,fw,fh,px,py,dw,dh);
  ctx.globalCompositeOperation='multiply';
  ctx.globalAlpha=0.2;
  ctx.fillStyle=tint;
  ctx.fillRect(dir<0?0:px,py,dw,dh);
  ctx.globalCompositeOperation='source-over';
  ctx.globalAlpha=1;
  ctx.restore();
}}

// ── Speech bubble ──
function drawBubble(px,py,text,sig){{
  const col=sig==='BULLISH'?'#00c853':sig==='BEARISH'?'#ff3131':'#ffd700';
  ctx.font='5px "Press Start 2P",monospace';
  const tw=ctx.measureText(text).width;
  const bw=tw+14,bh=18;
  const bx=px-bw/2,by=py-bh-10;
  ctx.fillStyle='#fff';ctx.fillRect(bx-2,by-2,bw+4,bh+4);
  ctx.fillStyle='#000';ctx.fillRect(bx,by,bw,bh);
  ctx.fillStyle=col;ctx.fillRect(bx,by,bw,3);
  ctx.fillStyle='#fff';ctx.font='5px "Press Start 2P",monospace';
  ctx.fillText(text,bx+7,by+13);
  ctx.fillStyle='#fff';ctx.beginPath();ctx.moveTo(px-4,by+bh+2);ctx.lineTo(px+4,by+bh+2);ctx.lineTo(px,by+bh+10);ctx.fill();
  ctx.fillStyle='#000';ctx.beginPath();ctx.moveTo(px-2,by+bh+2);ctx.lineTo(px+2,by+bh+2);ctx.lineTo(px,by+bh+8);ctx.fill();
}}

// ── Draw agent ──
function drawAgent(a){{
  const {{fw,fh}}=getSpriteSize();
  const dw=fw*SCALE,dh=fh*SCALE;
  // convert tile position to screen
  const px=roomX()+a.tx*TS + (TS-dw)/2;
  const py=roomY()+a.ty*TS + (TS-dh);
  const frameIdx=a.walking?WALK_FRAMES[Math.floor(a.fr/6)%4]:STAND_FRAME;
  // shadow
  ctx.fillStyle='rgba(0,0,0,0.18)';
  ctx.beginPath();ctx.ellipse(px+dw/2,py+dh,dw/2.5,4,0,0,Math.PI*2);ctx.fill();
  drawSprite(px,py,frameIdx,a.dir,a.tint);
  // pair label
  const sc=a.signal==='BULLISH'?'#00c853':a.signal==='BEARISH'?'#ff3131':'#ffd700';
  ctx.fillStyle='rgba(0,0,0,0.85)';ctx.fillRect(px,py+dh+1,dw,11);
  ctx.fillStyle=sc;ctx.font='5px monospace';ctx.textAlign='center';
  ctx.fillText(a.pair,px+dw/2,py+dh+9);ctx.textAlign='left';
  // bubble
  const msgIdx=Math.floor((tick+AGENTS.indexOf(a)*35)/90)%a.msgs.length;
  drawBubble(px+dw/2,py-2,a.msgs[msgIdx],a.signal);
}}

// ── Update agents (walk within room) ──
function updateAgents(){{
  AGENTS.forEach(a=>{{
    if(a.walking){{
      a.tx+=a.dir*0.03;
      a.fr+=1;
      if(a.tx>COLS-2){{a.tx=COLS-2;a.dir=-1;}}
      if(a.tx<1){{a.tx=1;a.dir=1;}}
    }}
    if(Math.random()<0.003){{
      a.walking=false;
      setTimeout(()=>a.walking=true,1500+Math.random()*2500);
    }}
  }});
}}

// ── Main loop ──
function loop(){{
  tick++;
  ctx.clearRect(0,0,cv.width,cv.height);

  // background
  ctx.fillStyle='#1a1208';
  ctx.fillRect(0,0,cv.width,cv.height);

  drawFloor();
  drawFurniture();
  drawLight();

  updateAgents();
  // depth sort by ty
  [...AGENTS].sort((a,b)=>a.ty-b.ty).forEach(a=>drawAgent(a));

  // clock
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
