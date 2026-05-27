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

with st.sidebar:
