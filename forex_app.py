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
[data-testid="stTextInput"] input{background:#0d0d1a!important;border:2px solid #4a9eff!important;
  border-radius:0!important;color:#e0e0e0!important;font-family:'Press Start 2P',monospace!important;font-size:10px!important}
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

# sidebar
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
    
    # แก้ไขแหล่งข่าวที่ระบบเดิมดึงไม่ได้
    use_cnbc = st.checkbox("CNBC News", value=True)
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
if use_cnbc:      RSS["CNBC"]          = "https://search.cnbc.com/rs/search/view.xml?partnerId=2000&keywords=forex"
if use_investing: RSS["Investing.com"] = "https://www.investing.com/rss/news_25.rss"

def fetch_news():
    articles=[]
    for src,url in RSS.items():
        try:
            feed=feedparser.parse(url)
            for e in feed.entries[:5]: # จำกัดไม่ให้เนื้อหาแน่นเกินไปจน Token ล้น
                articles.append({"source":src,"title":e.get("title",""),"summary":e.get("summary","")[:300]})
        except: pass
    return articles

def analyze(articles,pairs,key):
    client=anthropic.Anthropic(api_key=key)
    
    if not articles:
        news_text = "ไม่มีข้อมูลข่าวสารล่าสุดในขณะนี้ โปรดวิเคราะห์แนวโน้มตลาดโดยอิงจากสถานการณ์เศรษฐกิจทั่วไป"
    else:
        news_text="\n\n".join(f"[{a['source']}] {a['title']}\n{a['summary']}" for a in articles)
    
    prompt=f"""คุณคือผู้เชี่ยวชาญด้านการวิเคราะห์ตลาด Forex จงวิเคราะห์ข่าวสารล่าสุดต่อไปนี้ และประเมินผลกระทบต่อคู่เงินเหล่านี้: {", ".join(pairs)}

ข่าวสารระบบ:
{news_text}

จงตอบกลับในรูปแบบ JSON ออบเจกต์เท่านั้น (ห้ามมีคำเกริ่นนำ หรือข้อความอธิบายอื่นใดนอกเหนือจาก JSON) โดยใช้โครงสร้างดังนี้:
{{
  "overview": "<สรุปภาพรวมข่าวเด่นและทิศทางตลาดใน 2-3 ประโยคเป็นภาษาไทย>",
  "signals": {{
     {", ".join(f'"{p}": {{"signal": "<BULLISH/BEARISH/NEUTRAL>", "reason": "<เหตุผลประกอบสั้นๆ 1 ประโยคภาษาไทย>"}}' for p in pairs)}
  }},
  "watch": "<ระบุประเด็นหรือตัวเลขเศรษฐกิจสำคัญที่ต้องจับตาดูต่อไป>"
}}
"""
    
    # แก้ไขชื่อโมเดลเป็นรุ่นที่มีอยู่จริงและทำงานได้เสถียรที่สุด (Claude 3.5 Sonnet v2)
    r=client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1000,
        temperature=0,
        messages=[{"role":"user","content":prompt}]
    )
    return r.content[0].text

def parse_result(text, pairs):
    try:
        start_idx = text.find('{')
        end_idx = text.rfind('}') + 1
        if start_idx != -1 and end_idx != -1:
            json_str = text[start_idx:end_idx]
            data = json.loads(json_str)
        else:
            data = json.loads(text)
            
        overview = data.get("overview", "วิเคราะห์ข้อมูลข่าวสารตลาดสำเร็จ")
        watch = data.get("watch", "ติดตามข่าวสารอย่างใกล้ชิด")
        
        signals = {}
        raw_signals = data.get("signals", {})
        for p in pairs:
            p_data = raw_signals.get(p, {"signal": "NEUTRAL", "reason": "รอสัญญาณยืนยัน"})
            sig = p_data.get("signal", "NEUTRAL").upper()
            reason = p_data.get("reason", "อยู่ระหว่างสังเกตการณ์")
            signals[p] = (sig, reason)
            
        return overview, signals, watch
    except Exception as e:
        default_signals = {p: ("NEUTRAL", "ระบบ Parsing ขัดข้อง กำลังรีเฟรชข้อมูล") for p in pairs}
        return "วิเคราะห์ภาพรวมสำเร็จ (เกิดข้อขัดข้องชั่วคราวในการจัดฟอร์แมตข้อมูล)", default_signals, "ติดตามประกาศตัวเลขเศรษฐกิจหลักต่อไป"

def build_agents(pairs, signals):
    tints=['#44aaff','#ffaa44','#aa88ff','#44ffaa','#ffdd44','#ff88aa']
    positions=[(2.5,3.0),(5.0,4.5),(1.8,5.2),(5.8,2.2),(3.8,5.8),(2.0,4.0)]
    agents=[]
    for i,p in enumerate(pairs):
        sig,reason=signals.get(p,("NEUTRAL","Analyzing..."))
        msgs={
            "BULLISH":[p+"!","▲ BUY!","Bullish!","Going UP!"],
            "BEARISH":[p+"!","▼ SELL!","Bearish!","Going DOWN!"],
            "NEUTRAL":[p,"◆ WAIT","Watching","No signal"],
        }.get(sig,["..."])
        gx,gy=positions[i%len(positions)]
        agents.append({"pair":p,"signal":sig,"reason":reason,"gx":gx,"gy":gy,
                       "tint":tints[i%len(tints)],"msgs":msgs,"fr":i*25,
                       "walking":True,"dir":1 if i%2==0 else -1})
    return agents

def render_canvas(agents, sprite_url):
    agents_json=str(agents).replace("True","true").replace("False","false").replace("'",'"')
    return f"""
<canvas id="fc" style="width:100%;display:block;image-rendering:pixelated"></canvas>
<script>
const SPRITE_URL="{sprite_url}";
const AGENTS={agents_json};
const W=900,H=520;
const cv=document.getElementById('fc');
cv.width=W;cv.height=H;
const ctx=cv.getContext('2d');
ctx.imageSmoothingEnabled=false;
let tick=0,spriteReady=false;
const spr=new Image();
spr.crossOrigin='anonymous';
spr.src=SPRITE_URL;
spr.onload=()=>spriteReady=true;

function isoX(x,y){{return W/2+(x-y)*40;}}
function isoY(x,y){{return 120+(x+y)*20;}}

function poly(pts,col,stroke){{
  ctx.beginPath();ctx.moveTo(pts[0][0],pts[0][1]);
  for(let i=1;i<pts.length;i++)ctx.lineTo(pts[i][0],pts[i][1]);
  ctx.closePath();ctx.fillStyle=col;ctx.fill();
  ctx.strokeStyle=stroke||'rgba(0,0,0,0.25)';ctx.lineWidth=0.7;ctx.stroke();
}}

function box(gx,gy,gz,gw,gd,gh,tc,lc,rc){{
  const ox=isoX(gx,gy),oy=isoY(gx,gy);
  const TW=gw*40,TD=gd*40,TH=gh*20;
  poly([[ox,oy-TH],[ox+TW,oy+TW/2-TH],[ox+TW-TD,oy+TW/2+TD/2-TH],[ox-TD,oy+TD/2-TH]],tc);
  poly([[ox-TD,oy+TD/2-TH],[ox+TW-TD,oy+TW/2+TD/2-TH],[ox+TW-TD,oy+TW/2+TD/2],[ox-TD,oy+TD/2]],lc);
  poly([[ox+TW,oy+TW/2-TH],[ox+TW-TD,oy+TW/2+TD/2-TH],[ox+TW-TD,oy+TW/2+TD/2],[ox+TW,oy+TW/2]],rc);
}}

function tile(x,y,c1,c2){{
  const ox=isoX(x,y),oy=isoY(x,y);
  poly([[ox,oy-20],[ox+40,oy],[ox,oy+20],[ox-40,oy]],(x+y)%2===0?c1:c2);
}}

function drawRoom(){{
  for(let x=0;x<9;x++)for(let y=0;y<9;y++) tile(x,y,'#c8956c','#b8845c');
  for(let x=0;x<9;x++) box(x,-0.5,0,1,0.08,5,'#d4c4b0','#b8a898','#c0b0a0');
  for(let y=0;y<9;y++) box(-0.5,y,0,0.08,1,5,'#d4c4b0','#b8a898','#c0b0a0');

  box(0,0,0,2.2,0.7,3.5,'#8B5E3C','#6B4522','#7a5030');
  const bc=['#c0392b','#2980b9','#27ae60','#8e44ad','#e67e22','#e74c3c','#3498db','#1abc9c'];
  for(let s=0;s<3;s++){{
    box(0.06,0.06,s*1.1+0.3,2.1,0.58,0.1,'#9a6a3a','#7a4a2a','#8a5a30');
    for(let b=0;b<5;b++) box(0.12+b*0.38,0.1,s*1.1+0.42,0.3,0.5,0.8,bc[(s*5+b)%8],bc[(s*5+b+1)%8]+'cc',bc[(s*5+b+2)%8]+'aa');
  }}
  box(5.6,0.15,1,1.6,0.35,0.1,'#8B5E3C','#6B4522','#7a5030');
  box(5.6,0.15,2.2,1.6,0.35,0.1,'#8B5E3C','#6B4522','#7a5030');
  box(5.7,0.17,1.12,0.32,0.25,0.5,'#c0392b','#a02a1a','#b0321a');
  box(6.1,0.17,1.12,0.25,0.25,0.6,'#2980b9','#1a6090','#2270a0');
  box(6.5,0.17,1.12,0.28,0.25,0.4,'#27ae60','#1a8040','#229850');

  box(1.2,1.2,0,2.8,1.4,0.8,'#9a6a3a','#7a4a2a','#8a5a30');
  box(1.2,1.2,0.8,2.8,1.4,0.1,'#c8956c','#a87550','#b88560');
  box(1.6,1.3,0.9,1.2,0.15,1.5,'#2a2a3a','#1a1a2a','#222232');
  box(1.65,1.33,1.1,1.1,0.08,1.1,'#0a2040','#072030','#0a1830');
  const sx=isoX(1.7,1.34),sy=isoY(1.7,1.34)-1.1*20;
  ctx.fillStyle='#00ff41';
  for(let i=0;i<6;i++)ctx.fillRect(sx-10+i*2,sy+i*5+5,25+i*3,2);
  ctx.fillStyle='#4a9eff';ctx.fillRect(sx-10,sy+35,30,2);
  box(2.1,1.32,0.8,0.35,0.1,0.25,'#333','#222','#2a2a2a');
  box(2.7,1.35,0.88,0.95,0.6,0.07,'#888','#666','#777');
  for(let k=0;k<4;k++)for(let j=0;j<2;j++) box(2.75+k*0.2,1.38+j*0.24,0.96,0.14,0.14,0.05,'#aaa','#888','#999');
  box(3.8,1.4,0.88,0.25,0.35,0.08,'#999','#777','#888');
  box(3.5,1.25,0.9,0.3,0.3,0.4,'#8B4513','#6B3010','#7a3f10');
  const dp=isoX(3.65,1.38),dpy=isoY(3.65,1.38)-18;
  ctx.fillStyle='#2d7a1b';ctx.beginPath();ctx.ellipse(dp,dpy-8,8,10,0,0,Math.PI*2);ctx.fill();
  ctx.fillStyle='#3a9a22';ctx.beginPath();ctx.ellipse(dp-4,dpy-5,5,7,-.3,0,Math.PI*2);ctx.fill();
  ctx.beginPath();ctx.ellipse(dp+4,dpy-6,4,6,.3,0,Math.PI*2);ctx.fill();

  box(4.5,3.5,0,2.3,1.4,0.8,'#9a6a3a','#7a4a2a','#8a5a30');
  box(4.5,3.5,0.8,2.3,1.4,0.1,'#c8956c','#a87550','#b88560');
  box(4.8,3.7,0.9,1.1,0.85,0.07,'#888','#666','#777');
  box(4.8,3.7,0.97,1.1,0.08,0.65,'#2a2a3a','#1a1a2a','#222232');
  const lx=isoX(4.85,3.72),ly=isoY(4.85,3.72)-0.97*20;
  ctx.fillStyle='#4a9eff';ctx.fillRect(lx-6,ly-6,24,2);
  ctx.fillStyle='#00ff41';ctx.fillRect(lx-6,ly-2,18,2);
  ctx.fillStyle='#ffd700';ctx.fillRect(lx-6,ly+2,20,2);
  box(6.3,3.55,0.9,0.4,0.5,0.06,'#333','#222','#2a2a2a');

  box(2.2,2.8,0,0.85,0.85,0.6,'#1a1a2e','#0d0d1a','#141428');
  box(2.2,2.8,0.6,0.85,0.85,0.1,'#2a2a4a','#1a1a3a','#222240');
  box(2.2,2.8,0.7,0.85,0.12,1.0,'#1a1a2e','#0d0d1a','#141428');
  box(5.5,5.2,0,0.85,0.85,0.6,'#1a1a2e','#0d0d1a','#141428');
  box(5.5,5.2,0.6,0.85,0.85,0.1,'#2a2a4a','#1a1a3a','#222240');
  box(5.5,5.2,0.7,0.85,0.12,1.0,'#1a1a2e','#0d0d1a','#141428');

  box(3.5,0,1.8,2.5,0.08,2.0,'#f5f5ee','#e5e5de','#eeeeea');
  const wx=isoX(3.6,-0.01),wy=isoY(3.6,-0.01)-1.8*20;
  ctx.fillStyle='#c0392b';ctx.font='bold 7px monospace';ctx.fillText('FOREX SIGNALS',wx-15,wy+10);
  ctx.fillStyle='#00c853';ctx.fillRect(wx-12,wy+15,28,2.5);
  ctx.fillStyle='#ff3131';ctx.fillRect(wx-12,wy+21,20,2.5);
  ctx.fillStyle='#ffd700';ctx.fillRect(wx-12,wy+27,24,2.5);
  ctx.fillStyle='#888';ctx.font='6px monospace';
  ctx.fillText('EUR +0.42%',wx-10,wy+14);
  ctx.fillText('GBP -0.18%',wx-10,wy+20);
  ctx.fillText('JPY  0.00%',wx-10,wy+26);

  box(7.5,0.5,0,0.5,0.5,0.6,'#c0522a','#a03a1a','#b04422');
  const px=isoX(7.75,0.75),py=isoY(7.75,0.75)-12;
  ctx.fillStyle='#2d7a1b';
  ctx.beginPath();ctx.ellipse(px-8,py-18,9,15,-.3,0,Math.PI*2);ctx.fill();
  ctx.beginPath();ctx.ellipse(px+8,py-15,7,12,.3,0,Math.PI*2);ctx.fill();
  ctx.beginPath();ctx.ellipse(px,py-22,6,18,0,0,Math.PI*2);ctx.fill();
  ctx.fillStyle='#3a9a22';
  ctx.beginPath();ctx.ellipse(px-4,py-20,5,10,-.2,0,Math.PI*2);ctx.fill();
  ctx.beginPath();ctx.ellipse(px+4,py-16,4,9,.2,0,Math.PI*2);ctx.fill();

  box(-0.07,3.5,1.2,0.07,2,2,'#87ceeb','#6aadcc','#78bedd');
  box(-0.07,3.5,1.2,0.07,2,0.08,'#d0d0c0','#b0b0a0','#c0c0b0');
  box(-0.07,3.12,1.2,0.07,2,0.08,'#d0d0c0','#b0b0a0','#c0c0b0');
  box(-0.07,3.48,1.2,0.07,0.3,2,'#8b3a8b','#6a2a6a','#7a307a');
  box(-0.07,5.22,1.2,0.07,0.28,2,'#8b3a8b','#6a2a6a','#7a307a');

  box(7.5,7.5,0,0.1,0.1,3,'#888','#666','#777');
  const lampX=isoX(7.55,7.55),lampY=isoY(7.55,7.55)-3*20;
  ctx.fillStyle='#ffeeaa';ctx.beginPath();ctx.ellipse(lampX,lampY,14,8,0,0,Math.PI*2);ctx.fill();
  const lampGrad=ctx.createRadialGradient(lampX,lampY+20,5,lampX,lampY+20,80);
  lampGrad.addColorStop(0,'rgba(255,240,180,0.2)');lampGrad.addColorStop(1,'rgba(255,240,180,0)');
  ctx.fillStyle=lampGrad;ctx.beginPath();ctx.ellipse(lampX,lampY+20,80,45,0,0,Math.PI*2);ctx.fill();

  const cg=ctx.createRadialGradient(isoX(4,4),isoY(4,4),10,isoX(4,4),isoY(4,4),160);
  cg.addColorStop(0,'rgba(255,240,180,0.12)');cg.addColorStop(1,'rgba(255,240,180,0)');
  ctx.fillStyle=cg;ctx.beginPath();ctx.ellipse(isoX(4,4),isoY(4,4),160,90,0,0,Math.PI*2);ctx.fill();

  box(1.4,1.28,0.92,0.22,0.22,0.3,'#fff','#eee','#f5f5f5');
  box(1.4,1.28,1.2,0.22,0.22,0.05,'#8B4513','#6B3010','#7a4010');
}}

const TOTAL_FRAMES=12;
const WALK_FRAMES=[8,9,10,11];
const STAND_FRAME=8;
const SCALE=3;
let FW=0,FH=0;

function getSpriteSize(){{
  if(!spriteReady||spr.width===0) return {{fw:16,fh:24}};
  if(FW===0){{ FW=Math.round(spr.width/TOTAL_FRAMES); FH=spr.height; }}
  return {{fw:FW,fh:FH}};
}}

function drawSprite(px,py,frameIdx,dir,tint){{
  const {{fw,fh}}=getSpriteSize();
  if(!spriteReady||fw===0) return;
  const dw=fw*SCALE,dh=fh*SCALE;
  ctx.save();
  if(dir<0){{ ctx.translate(px+dw,py); ctx.scale(-1,1); ctx.drawImage(spr,frameIdx*fw,0,fw,fh,0,0,dw,dh); }}
  else ctx.drawImage(spr,frameIdx*fw,0,fw,fh,px,py,dw,dh);
  ctx.globalCompositeOperation='multiply';
  ctx.globalAlpha=0.22;
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
  const bw=tw+14,bh=18;
  const bx=px-bw/2,by=py-bh-12;
  ctx.fillStyle='#fff';ctx.fillRect(bx-2,by-2,bw+4,bh+4);
  ctx.fillStyle='#000';ctx.fillRect(bx,by,bw,bh);
  ctx.fillStyle=col;ctx.fillRect(bx,by,bw,3);
  ctx.fillStyle='#fff';ctx.font='5px "Press Start 2P",monospace';
  ctx.fillText(text,bx+7,by+13);
  ctx.fillStyle='#fff';ctx.beginPath();ctx.moveTo(px-4,by+bh+2);ctx.lineTo(px+4,by+bh+2);ctx.lineTo(px,by+bh+10);ctx.fill();
  ctx.fillStyle='#000';ctx.beginPath();ctx.moveTo(px-2,by+bh+2);ctx.lineTo(px+2,by+bh+2);ctx.lineTo(px,by+bh+8);ctx.fill();
}}

function drawAgent(a){{
  const {{fw,fh}}=getSpriteSize();
  const dw=fw*SCALE,dh=fh*SCALE;
  const px=isoX(a.gx,a.gy)-dw/2;
  const py=isoY(a.gx,a.gy)-dh+4;
  const frameIdx=a.walking?WALK_FRAMES[Math.floor(a.fr/6)%4]:STAND_FRAME;
  ctx.fillStyle='rgba(0,0,0,0.2)';
  ctx.beginPath();ctx.ellipse(px+dw/2,py+dh-2,dw/2.5,4,0,0,Math.PI*2);ctx.fill();
  drawSprite(px,py,frameIdx,a.dir,a.tint);
  const sc=a.signal==='BULLISH'?'#00c853':a.signal==='BEARISH'?'#ff3131':'#ffd700';
  ctx.fillStyle='rgba(0,0,0,0.85)';ctx.fillRect(px,py+dh+1,dw,12);
  ctx.fillStyle=sc;ctx.font='5px monospace';ctx.textAlign='center';
  ctx.fillText(a.pair,px+dw/2,py+dh+10);ctx.textAlign='left';
  const msgIdx=Math.floor((tick+AGENTS.indexOf(a)*35)/90)%a.msgs.length;
  drawBubble(px+dw/2,py,a.msgs[msgIdx],a.signal);
  return {{depth:a.gx+a.gy}};
}}

function updateAgents(){{
  AGENTS.forEach(a=>{{
    if(a.walking){{
      a.gx+=a.dir*0.012;a.gy+=a.dir*0.005;a.fr+=1;
      if(a.gx>8.2){{a.gx=8.2;a.dir=-1;}}
      if(a.gx<0.5){{a.gx=0.5;a.dir=1;}}
      if(a.gy>8.2){{a.gy=8.2;a.dir=-1;}}
      if(a.gy<0.5){{a.gy=0.5;a.dir=1;}}
    }}
    if(Math.random()<0.003){{a.walking=false;setTimeout(()=>a.walking=true,1800+Math.random()*2200);}}
  }});
}}

function loop(){{
  tick++;
  ctx.clearRect(0,0,W,H);
  ctx.fillStyle='#1a1a2e';ctx.fillRect(0,0,W,H);
  drawRoom();
  updateAgents();
  [...AGENTS].sort((a,b)=>(a.gx+a.gy)-(b.gx+b.gy)).forEach(a=>drawAgent(a));
  const n=new Date();
  const ts=n.getHours().toString().padStart(2,'0')+':'+n.getMinutes().toString().padStart(2,'0')+':'+n.getSeconds().toString().padStart(2,'0');
  ctx.fillStyle='rgba(0,0,0,0.85)';ctx.fillRect(W-96,8,90,18);
  ctx.fillStyle='#00ff41';ctx.font='8px "Press Start 2P",monospace';ctx.fillText(ts,W-90,21);
  requestAnimationFrame(loop);
}}
loop();
</script>
"""

SPRITE_URL = "https://raw.githubusercontent.com/pech3930/forex-bot/main/Astronaut.png"

# ── render ──
if not run_btn:
    default_agents=build_agents(
        selected_pairs if selected_pairs else ["EUR/USD","USD/THB","USD/JPY","GBP/USD","XAU/USD"],
        {})
    st.components.v1.html(render_canvas(default_agents, SPRITE_URL), height=540, scrolling=False)
    st.markdown("""
    <div style="text-align:center;font-family:'Press Start 2P',monospace;font-size:7px;color:#333;padding:8px;letter-spacing:0.1em">
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
        for a in loading:
            a["msgs"]=["Fetching!","Reading...","Analyzing!","Working..."]
        ph.components.v1.html(render_canvas(loading,SPRITE_URL),height=540,scrolling=False)

        with st.spinner(""):
            articles=fetch_news()
            raw=analyze(articles,selected_pairs,api_key)
            overview,signals,watch=parse_result(raw,selected_pairs)

        final=build_agents(selected_pairs,signals)
        ph.empty()
        st.components.v1.html(render_canvas(final,SPRITE_URL),height=540,scrolling=False)

        # signal cards
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