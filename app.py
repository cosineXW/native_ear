import streamlit as st
import whisper
import random
import os
import torch
import numpy as np
import matplotlib.pyplot as plt
import json
import difflib

# --- 1. Basic Config & Model Loading ---
st.set_page_config(page_title="The Native Ear", page_icon="🎧", layout="centered")

@st.cache_resource
def load_whisper_models():
    # 听劝！必须改成 base，不然 Hugging Face 免费版直接内存爆炸崩溃
    return whisper.load_model("base")

with st.spinner("Initializing Whisper Forensic Model..."):
    m_model = load_whisper_models()

def load_database():
    with open('database.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def load_summaries():
    with open('summaries.json', 'r', encoding='utf-8') as f:
        return json.load(f)

PREBAKED_DB = load_database()
SUMMARIES = load_summaries()
ALL_NATIVE_OPTIONS = list(PREBAKED_DB.keys())

# --- Q1 x Q2 → scenario key 映射 ---
Q1_OPTIONS = ["Not at all", "Partially", "Fully"]
Q2_OPTIONS = ["Purely in my native pronunciation", "I unconsciously leaned toward the original language", "I deliberately imitated the original language"]

SCENARIO_KEY_MAP = {
    ("Not at all", "Purely in my native pronunciation"): "not_at_all__native_pronunciation",
    ("Not at all", "I unconsciously leaned toward the original language"): "not_at_all__unconsciously_leaned",
    ("Not at all", "I deliberately imitated the original language"): "not_at_all__deliberately_imitated",
    ("Partially", "Purely in my native pronunciation"): "partially__native_pronunciation",
    ("Partially", "I unconsciously leaned toward the original language"): "partially__unconsciously_leaned",
    ("Partially", "I deliberately imitated the original language"): "partially__deliberately_imitated",
    ("Fully", "Purely in my native pronunciation"): "fully__native_pronunciation",
    ("Fully", "I unconsciously leaned toward the original language"): "fully__unconsciously_leaned",
    ("Fully", "I deliberately imitated the original language"): "fully__deliberately_imitated",
}

# ============================================================
# --- INTRO SLIDESHOW ---
# ============================================================

# SVG 插图生成函数（支持 lang='zh'/'en'）
def svg_slide_1(lang='zh'):
    """标题页 — 耳朵 + 声波"""
    subtitle = "机器听觉中的偏见与审判" if lang == 'zh' else "Bias and Judgment in Machine Listening"
    return f'''<svg viewBox="0 0 400 250" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bg1" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#0f0c29"/>
      <stop offset="50%" style="stop-color:#302b63"/>
      <stop offset="100%" style="stop-color:#24243e"/>
    </linearGradient>
  </defs>
  <rect width="400" height="250" fill="url(#bg1)" rx="12"/>
  <!-- 耳朵轮廓 -->
  <g transform="translate(170,40) scale(0.8)">
    <path d="M50,10 C20,10 5,40 5,75 C5,110 20,140 40,160 C50,170 55,180 55,195
             C55,205 50,210 45,210 C40,210 38,205 38,200"
          fill="none" stroke="#e0d0ff" stroke-width="3" stroke-linecap="round"/>
    <path d="M50,10 C75,10 90,35 90,65 C90,90 78,100 65,100 C55,100 48,90 50,80
             C52,72 60,68 65,72"
          fill="none" stroke="#e0d0ff" stroke-width="3" stroke-linecap="round"/>
  </g>
  <!-- 声波 -->
  <g opacity="0.5">
    <path d="M280,80 Q290,60 300,80 Q310,100 320,80 Q330,60 340,80" fill="none" stroke="#7b68ee" stroke-width="2"/>
    <path d="M275,105 Q290,75 305,105 Q320,135 335,105 Q350,75 365,105" fill="none" stroke="#9b89ff" stroke-width="2"/>
    <path d="M270,130 Q290,90 310,130 Q330,170 350,130 Q370,90 390,130" fill="none" stroke="#b8a9ff" stroke-width="1.5"/>
  </g>
  <!-- 标题 -->
  <text x="200" y="220" text-anchor="middle" fill="#ffffff" font-size="16" font-family="sans-serif" font-weight="bold">The Native Ear</text>
  <text x="200" y="240" text-anchor="middle" fill="#a0a0cc" font-size="10" font-family="sans-serif">{subtitle}</text>
</svg>'''

def svg_slide_2(lang='zh'):
    """LADO — 护照 + 声纹"""
    passport_l1 = "语言" if lang == 'zh' else "LINGUISTIC"
    passport_l2 = "护照" if lang == 'zh' else "PASSPORT"
    certified = "LADO 认证" if lang == 'zh' else "LADO CERTIFIED"
    analysis = "声纹分析" if lang == 'zh' else "VOICE ANALYSIS"
    bottom = "你的口音 = 你的护照？" if lang == 'zh' else "Your accent = your passport?"
    return f'''<svg viewBox="0 0 400 250" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bg2" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#1a1a2e"/>
      <stop offset="100%" style="stop-color:#16213e"/>
    </linearGradient>
  </defs>
  <rect width="400" height="250" fill="url(#bg2)" rx="12"/>
  <!-- 护照 -->
  <rect x="40" y="50" width="120" height="160" rx="8" fill="#1e3a5f" stroke="#4a7ab5" stroke-width="2"/>
  <text x="100" y="85" text-anchor="middle" fill="#8bb8e8" font-size="9" font-family="sans-serif">{passport_l1}</text>
  <text x="100" y="100" text-anchor="middle" fill="#8bb8e8" font-size="9" font-family="sans-serif">{passport_l2}</text>
  <circle cx="100" cy="135" r="25" fill="none" stroke="#4a7ab5" stroke-width="1.5"/>
  <text x="100" y="140" text-anchor="middle" fill="#4a7ab5" font-size="24">?</text>
  <text x="100" y="185" text-anchor="middle" fill="#5a8aba" font-size="8" font-family="sans-serif">{certified}</text>
  <!-- 箭头 -->
  <path d="M180,130 L220,130" stroke="#ff6b6b" stroke-width="2" marker-end="url(#arr2)"/>
  <defs><marker id="arr2" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#ff6b6b"/></marker></defs>
  <!-- 声纹波形 -->
  <g transform="translate(240,70)">
    <rect width="130" height="120" rx="6" fill="#0d1b2a" stroke="#2a4a6b" stroke-width="1"/>
    <g transform="translate(10,60)">
      <line x1="0" y1="-30" x2="0" y2="30" stroke="#4ecdc4" stroke-width="3" opacity="0.7"/>
      <line x1="10" y1="-15" x2="10" y2="15" stroke="#4ecdc4" stroke-width="3" opacity="0.5"/>
      <line x1="20" y1="-40" x2="20" y2="40" stroke="#4ecdc4" stroke-width="3" opacity="0.9"/>
      <line x1="30" y1="-20" x2="30" y2="20" stroke="#ff6b6b" stroke-width="3" opacity="0.6"/>
      <line x1="40" y1="-35" x2="40" y2="35" stroke="#ff6b6b" stroke-width="3" opacity="0.8"/>
      <line x1="50" y1="-10" x2="50" y2="10" stroke="#4ecdc4" stroke-width="3" opacity="0.4"/>
      <line x1="60" y1="-25" x2="60" y2="25" stroke="#4ecdc4" stroke-width="3" opacity="0.6"/>
      <line x1="70" y1="-45" x2="70" y2="45" stroke="#ff6b6b" stroke-width="3" opacity="0.9"/>
      <line x1="80" y1="-18" x2="80" y2="18" stroke="#4ecdc4" stroke-width="3" opacity="0.5"/>
      <line x1="90" y1="-8" x2="90" y2="8" stroke="#4ecdc4" stroke-width="3" opacity="0.3"/>
      <line x1="100" y1="-30" x2="100" y2="30" stroke="#ff6b6b" stroke-width="3" opacity="0.7"/>
    </g>
    <text x="65" y="110" text-anchor="middle" fill="#7a9ab8" font-size="8" font-family="sans-serif">{analysis}</text>
  </g>
  <text x="200" y="235" text-anchor="middle" fill="#a0a0cc" font-size="10" font-family="sans-serif">{bottom}</text>
</svg>'''

def svg_slide_3(lang='zh'):
    """空耳 — 音符变文字"""
    lbl_original = "原文" if lang == 'zh' else "Original"
    lbl_explain = "(西班牙语：跟我来)" if lang == 'zh' else "(Spanish: Come with me)"
    lbl_ear = "中文耳朵" if lang == 'zh' else "Chinese Ear"
    lbl_misheard = "空耳" if lang == 'zh' else "Misheard"
    lbl_sounds = "(听起来像中文！)" if lang == 'zh' else "(Sounds like Chinese!)"
    lbl_bot = "🤖 Whisper 模型：" if lang == 'zh' else "🤖 Whisper Model:"
    lbl_detected = '"检测结果：中文 87%"' if lang == 'zh' else '"Detected: Chinese 87%"'
    lbl_but = "但这其实是西班牙语啊..." if lang == 'zh' else "But this is actually Spanish..."
    return f'''<svg viewBox="0 0 400 250" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bg3" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#1a1a2e"/>
      <stop offset="100%" style="stop-color:#2d1b46"/>
    </linearGradient>
  </defs>
  <rect width="400" height="250" fill="url(#bg3)" rx="12"/>
  <!-- 左边：原文 -->
  <g transform="translate(30,40)">
    <rect width="150" height="80" rx="10" fill="#2a1f4e" stroke="#6c5ce7" stroke-width="1.5"/>
    <text x="75" y="25" text-anchor="middle" fill="#a29bfe" font-size="9" font-family="sans-serif">{lbl_original}</text>
    <text x="75" y="50" text-anchor="middle" fill="#ddd" font-size="12" font-family="sans-serif">♪ Ven conmigo ♪</text>
    <text x="75" y="68" text-anchor="middle" fill="#888" font-size="8" font-family="sans-serif">{lbl_explain}</text>
  </g>
  <!-- 箭头 + 耳朵 -->
  <g transform="translate(185,55)">
    <text x="15" y="15" text-anchor="middle" fill="#ffd93d" font-size="28">👂</text>
    <text x="15" y="40" text-anchor="middle" fill="#ffd93d" font-size="8" font-family="sans-serif">{lbl_ear}</text>
  </g>
  <!-- 右边：空耳 -->
  <g transform="translate(220,40)">
    <rect width="150" height="80" rx="10" fill="#1b3a2a" stroke="#00b894" stroke-width="1.5"/>
    <text x="75" y="25" text-anchor="middle" fill="#55efc4" font-size="9" font-family="sans-serif">{lbl_misheard}</text>
    <text x="75" y="50" text-anchor="middle" fill="#ddd" font-size="12" font-family="sans-serif">♪ 蚊子咪过 ♪</text>
    <text x="75" y="68" text-anchor="middle" fill="#888" font-size="8" font-family="sans-serif">{lbl_sounds}</text>
  </g>
  <!-- 下方：机器的困惑 -->
  <g transform="translate(100,145)">
    <rect width="200" height="70" rx="10" fill="#1a1a2e" stroke="#636e72" stroke-width="1" stroke-dasharray="4"/>
    <text x="100" y="25" text-anchor="middle" fill="#b2bec3" font-size="9" font-family="sans-serif">{lbl_bot}</text>
    <text x="100" y="45" text-anchor="middle" fill="#fd79a8" font-size="10" font-family="sans-serif">{lbl_detected}</text>
    <text x="100" y="60" text-anchor="middle" fill="#636e72" font-size="8" font-family="sans-serif">{lbl_but}</text>
  </g>
</svg>'''

def svg_slide_4(lang='zh'):
    """测试流程 — 3 步图"""
    s1_title = "听一段外语" if lang == 'zh' else "Listen"
    s1_l1 = "机器给你一段" if lang == 'zh' else "The machine gives you"
    s1_l2 = '"空耳"歌词' if lang == 'zh' else '"misheard" lyrics'
    s2_title = "照着念出来" if lang == 'zh' else "Read Aloud"
    s2_l1 = "用你最自然的" if lang == 'zh' else "Use your most"
    s2_l2 = "方式朗读它" if lang == 'zh' else "natural voice"
    s3_title = "机器审判你" if lang == 'zh' else "Be Judged"
    s3_l1 = "它会决定你" if lang == 'zh' else "It decides what"
    s3_l2 = '"是哪国人"' if lang == 'zh' else '"nationality" you are'
    tip_l1 = "这不是语言考试——没有对错。" if lang == 'zh' else "This is not a language test — there are no wrong answers."
    tip_l2 = "我们想让你亲身体验：当一台机器仅凭声音来判断你是谁，" if lang == 'zh' else "We want you to experience firsthand: when a machine judges"
    tip_l3 = "它的结论有多荒谬，又有多危险。" if lang == 'zh' else "who you are by sound alone, how absurd — and dangerous — its verdict can be."
    return f'''<svg viewBox="0 0 400 250" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bg4" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#0f0c29"/>
      <stop offset="100%" style="stop-color:#1a1a3e"/>
    </linearGradient>
  </defs>
  <rect width="400" height="250" fill="url(#bg4)" rx="12"/>
  <!-- Step 1 -->
  <g transform="translate(30,30)">
    <circle cx="50" cy="40" r="35" fill="#2d1b69" stroke="#6c5ce7" stroke-width="2"/>
    <text x="50" y="35" text-anchor="middle" fill="#a29bfe" font-size="24">🎧</text>
    <text x="50" y="52" text-anchor="middle" fill="#dfe6e9" font-size="8" font-weight="bold">1</text>
    <text x="50" y="95" text-anchor="middle" fill="#b2bec3" font-size="9" font-family="sans-serif">{s1_title}</text>
    <text x="50" y="108" text-anchor="middle" fill="#636e72" font-size="7.5" font-family="sans-serif">{s1_l1}</text>
    <text x="50" y="119" text-anchor="middle" fill="#636e72" font-size="7.5" font-family="sans-serif">{s1_l2}</text>
  </g>
  <!-- Arrow -->
  <path d="M130,70 L155,70" stroke="#636e72" stroke-width="1.5" marker-end="url(#a4)"/>
  <defs><marker id="a4" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#636e72"/></marker></defs>
  <!-- Step 2 -->
  <g transform="translate(155,30)">
    <circle cx="50" cy="40" r="35" fill="#1b3a2a" stroke="#00b894" stroke-width="2"/>
    <text x="50" y="35" text-anchor="middle" fill="#55efc4" font-size="24">🎤</text>
    <text x="50" y="52" text-anchor="middle" fill="#dfe6e9" font-size="8" font-weight="bold">2</text>
    <text x="50" y="95" text-anchor="middle" fill="#b2bec3" font-size="9" font-family="sans-serif">{s2_title}</text>
    <text x="50" y="108" text-anchor="middle" fill="#636e72" font-size="7.5" font-family="sans-serif">{s2_l1}</text>
    <text x="50" y="119" text-anchor="middle" fill="#636e72" font-size="7.5" font-family="sans-serif">{s2_l2}</text>
  </g>
  <!-- Arrow -->
  <path d="M255,70 L280,70" stroke="#636e72" stroke-width="1.5" marker-end="url(#a4)"/>
  <!-- Step 3 -->
  <g transform="translate(280,30)">
    <circle cx="50" cy="40" r="35" fill="#3a1b1b" stroke="#ff6b6b" stroke-width="2"/>
    <text x="50" y="35" text-anchor="middle" fill="#ff6b6b" font-size="24">⚖️</text>
    <text x="50" y="52" text-anchor="middle" fill="#dfe6e9" font-size="8" font-weight="bold">3</text>
    <text x="50" y="95" text-anchor="middle" fill="#b2bec3" font-size="9" font-family="sans-serif">{s3_title}</text>
    <text x="50" y="108" text-anchor="middle" fill="#636e72" font-size="7.5" font-family="sans-serif">{s3_l1}</text>
    <text x="50" y="119" text-anchor="middle" fill="#636e72" font-size="7.5" font-family="sans-serif">{s3_l2}</text>
  </g>
  <!-- 底部提示 -->
  <g transform="translate(40,170)">
    <rect width="320" height="55" rx="8" fill="#1a1a2e" stroke="#ffd93d" stroke-width="1" opacity="0.8"/>
    <text x="160" y="22" text-anchor="middle" fill="#ffd93d" font-size="9.5" font-family="sans-serif">{tip_l1}</text>
    <text x="160" y="40" text-anchor="middle" fill="#b2bec3" font-size="8.5" font-family="sans-serif">{tip_l2}</text>
    <text x="160" y="52" text-anchor="middle" fill="#b2bec3" font-size="8.5" font-family="sans-serif">{tip_l3}</text>
  </g>
</svg>'''

# --- 幻灯片内容（大白话中文 + 英文双语） ---
INTRO_SLIDES = [
    {
        "svg_fn": svg_slide_1,
        "title_zh": "欢迎来到 The Native Ear",
        "title_en": "Welcome to The Native Ear",
        "body_zh": (
            "想象一下：你逃离战火，来到一个陌生的国家申请庇护。"
            "你没有护照，没有身份证，唯一能证明你是谁的——是你的声音。\n\n"
            "于是，一个「语言专家」或者一台机器开始听你说话。"
            "不是听你说了什么，而是听你**怎么说的**——你的口音、你的语调、你的发音习惯。"
            "然后它下判断：你是不是你声称的那个国家的人。\n\n"
            "**这不是科幻小说。这是真实世界里正在发生的事。**"
        ),
        "body_en": (
            "Imagine fleeing a war zone and arriving in a foreign country to seek asylum. "
            "You have no passport, no ID — the only thing that can prove who you are is your voice.\n\n"
            "A \"language expert\" or a machine starts listening to you. "
            "Not *what* you say, but *how* you say it — your accent, your intonation, your pronunciation. "
            "Then it makes a judgment: are you really from the country you claim?\n\n"
            "**This is not science fiction. This is happening right now.**"
        ),
    },
    {
        "svg_fn": svg_slide_2,
        "title_zh": "什么是 LADO？",
        "title_en": "What is LADO?",
        "body_zh": (
            "LADO（Language Analysis for the Determination of Origin）= 语言来源鉴定分析。\n\n"
            "上世纪 90 年代，北欧国家开始用这种方法来甄别难民：\n"
            "让语言分析师听申请人说话，根据口音判断这个人到底来自哪里。"
            "后来英国、德国、澳大利亚等国纷纷跟进。\n\n"
            "它的核心假设很简单：**你说什么样的话 = 你是什么样的人。**\n\n"
            "但问题是——人会搬家、会学新语言、会在不同文化里长大。"
            "一个在肯尼亚长大的索马里人，口音可能听起来像肯尼亚人。"
            "LADO 可能因此拒绝她的庇护申请。\n"
            "**口音 ≠ 身份。但国家机器把它们画上了等号。**"
        ),
        "body_en": (
            "LADO (Language Analysis for the Determination of Origin) is a method used by governments "
            "to verify asylum seekers' origins based on how they speak.\n\n"
            "Starting in 1990s Scandinavia, analysts listen to applicants and judge where they're from "
            "based on accent alone. The UK, Germany, Australia and others adopted it since.\n\n"
            "The core assumption: **how you speak = where you're from.**\n\n"
            "But people migrate, learn new languages, grow up across cultures. "
            "A Somali raised in Kenya might sound Kenyan. LADO could deny her asylum for that.\n"
            "**Accent ≠ identity. But the state treats them as the same thing.**"
        ),
    },
    {
        "svg_fn": svg_slide_3,
        "title_zh": "当机器来充当那只「耳朵」",
        "title_en": "When a Machine Becomes the Ear",
        "body_zh": (
            "现在，我们把 LADO 的逻辑交给一台 AI 语音模型（Whisper）来执行。\n\n"
            "它会听你说话，然后判断你说的是什么语言。"
            "但它的判断方式和人类专家一样粗暴：**只听表面的声音模式，不管你是否真的理解。**\n\n"
            "更有趣的是——我们加入了「空耳」（misheard lyrics）的概念：\n"
            "就是用你的母语去「听」一段外语，让它听起来像你母语里的句子。"
            "比如西班牙语 \"Ven conmigo\" 在中文耳朵里可能变成「蚊子咪过」。\n\n"
            "**当你用母语的方式去读这段「空耳」歌词时，机器会怎么判断你的语言身份？**"
        ),
        "body_en": (
            "Now we hand LADO's logic to an AI speech model (Whisper).\n\n"
            "It listens to your voice and decides what language you're speaking. "
            "But it judges the same crude way: **surface sound patterns only, regardless of understanding.**\n\n"
            "We add a twist — \"misheard lyrics\" (soramimi/空耳):\n"
            "Foreign speech re-heard as phrases in your native language. "
            "Spanish \"Ven conmigo\" might sound like Chinese \"蚊子咪过\" to a Chinese ear.\n\n"
            "**When you read these misheard lyrics aloud, how will the machine judge your linguistic identity?**"
        ),
    },
    {
        "svg_fn": svg_slide_4,
        "title_zh": "你要做什么？",
        "title_en": "What Will You Do?",
        "body_zh": (
            "这个测试分三步：\n\n"
            "**第一步：听。** 机器随机给你一段外语音频和对应的「空耳」歌词——"
            "一段用你母语写成的、听起来像外语的句子。\n\n"
            "**第二步：念。** 你对着麦克风把这段空耳歌词读出来。"
            "用你最自然的方式——想怎么念就怎么念。\n\n"
            "**第三步：被审判。** 机器分析你的录音，给你一个「语言护照」——"
            "它会告诉你，在它耳朵里，你「是哪国人」。\n\n"
            "最后，你会看到你的自我认知和机器判断之间的落差。\n"
            "这个落差，就是整个项目想让你感受到的东西。"
        ),
        "body_en": (
            "The test has three steps:\n\n"
            "**Step 1: Listen.** The machine gives you a foreign audio clip and its \"misheard lyrics\" — "
            "a sentence written in your native language that sounds like the foreign speech.\n\n"
            "**Step 2: Read aloud.** Record yourself reading the misheard lyrics. "
            "Use your most natural voice — however you want to say it.\n\n"
            "**Step 3: Be judged.** The machine analyzes your recording and issues a \"linguistic passport\" — "
            "telling you what nationality your voice sounds like.\n\n"
            "At the end, you'll see the gap between your self-perception and the machine's verdict.\n"
            "That gap is exactly what this project wants you to feel."
        ),
    },
]

TOTAL_SLIDES = len(INTRO_SLIDES)

# --- 初始化 session state ---
if 'intro_done' not in st.session_state:
    st.session_state['intro_done'] = False
if 'slide_index' not in st.session_state:
    st.session_state['slide_index'] = 0
if 'intro_lang' not in st.session_state:
    st.session_state['intro_lang'] = 'zh'

# ======== 幻灯片模式 ========
if not st.session_state['intro_done']:

    # 语言切换（右上角）
    col_spacer, col_lang = st.columns([5, 1])
    with col_lang:
        lang_choice = st.toggle("EN", value=(st.session_state['intro_lang'] == 'en'), key="lang_toggle")
        st.session_state['intro_lang'] = 'en' if lang_choice else 'zh'

    lang = st.session_state['intro_lang']
    idx = st.session_state['slide_index']
    slide = INTRO_SLIDES[idx]

    # 显示 SVG 插图（根据当前语言动态生成）
    current_svg = slide["svg_fn"](lang)
    st.markdown(
        f'<div style="display:flex;justify-content:center;margin-bottom:1rem;">{current_svg}</div>',
        unsafe_allow_html=True
    )

    # 标题
    title_key = f"title_{lang}"
    st.markdown(f"### {slide[title_key]}")

    # 正文
    body_key = f"body_{lang}"
    st.markdown(slide[body_key])

    # 进度指示器
    progress_dots = ""
    for i in range(TOTAL_SLIDES):
        if i == idx:
            progress_dots += "● "
        else:
            progress_dots += "○ "
    st.markdown(f"<div style='text-align:center;color:#888;margin:1rem 0;letter-spacing:4px;'>{progress_dots}</div>", unsafe_allow_html=True)

    # 导航按钮
    if idx < TOTAL_SLIDES - 1:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if idx > 0:
                if st.button("← 上一页" if lang == 'zh' else "← Back", use_container_width=True):
                    st.session_state['slide_index'] -= 1
                    st.rerun()
        with col3:
            if st.button("下一页 →" if lang == 'zh' else "Next →", use_container_width=True, type="primary"):
                st.session_state['slide_index'] += 1
                st.rerun()
    else:
        # 最后一页：开始测试按钮
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if st.button("← 上一页" if lang == 'zh' else "← Back", use_container_width=True):
                st.session_state['slide_index'] -= 1
                st.rerun()
        with col2:
            st.markdown("")  # spacer
        with col3:
            pass

        st.markdown("---")
        if st.button(
            "🎧 开始测试 / Start the Test" if lang == 'zh' else "🎧 Start the Test",
            use_container_width=True,
            type="primary"
        ):
            st.session_state['intro_done'] = True
            st.rerun()

    st.stop()  # 幻灯片模式下不显示后面的测试内容

# ============================================================
# --- 正式测试（原有代码）---
# ============================================================

# --- 2. Sidebar Configuration ---
with st.sidebar:
    st.title("⚖️ Configuration")
    st.markdown("---")
    user_home_lang = st.selectbox(
        "Set Your Native Ear:",
        ALL_NATIVE_OPTIONS,
        help="This represents your native linguistic bias."
    )
    st.info(f"📍 Machine Bias: **{user_home_lang}**\n\nThe machine will force you to read cross-lingual misheard lyrics.")

# --- 3. Main Interface ---
st.title("🎧 The Native Ear")
st.markdown("*Bias and Judgment in Machine Listening*")
st.divider()

# -- STEP 1: Grab & Generate --
st.header("Step 1: The Biased Listener")

if st.button("🎲 1. Grab Audio & Generate Misheard Lyrics"):
    available_scripts = PREBAKED_DB.get(user_home_lang, [])

    if not available_scripts:
        st.error(f"Error: {user_home_lang} dictionary is empty!")
    else:
        script = random.choice(available_scripts)

        if os.path.exists(script["file"]):
            st.session_state['current_path'] = script["file"]
            st.session_state['original_lang'] = script["original_lang"]
            st.session_state['true_text'] = script["true_text"]
            st.session_state['fake_text'] = script["fake_text"]
            st.session_state['recorded_file'] = None
            st.session_state['analysis_done'] = False

            with st.spinner("Machine is establishing baseline from the original audio..."):
                res = m_model.transcribe(st.session_state['current_path'])
                st.session_state['machine_original_text'] = res["text"]

        else:
            st.error(f"Cannot find audio file: {script['file']}. Did you put it in the right folder?")

# -- Show Audio & Text --
if st.session_state.get('current_path'):
    st.write("🔈 **Original Audio:**")
    st.audio(st.session_state['current_path'], autoplay=True)

    st.write(f"📢 **Misheard Lyrics (Machine's {user_home_lang} hallucination):**")
    st.info(st.session_state['fake_text'])
    st.markdown("---")

    # -- STEP 2: Record --
    st.header("Step 2: Human Accommodation")
    st.markdown("Read the misheard text above to appease the machine.")

    # 核心修改：使用 Streamlit 自带的网页录音组件，完美解决 Hugging Face 录音报错问题
    audio_bytes = st.audio_input("🎤 2. Record your voice")

    if audio_bytes:
        temp_file = "_temp_realtime.wav"
        with open(temp_file, "wb") as f:
            f.write(audio_bytes.getbuffer())
        st.session_state['recorded_file'] = temp_file
        st.session_state['analysis_done'] = False
        st.success("Recording complete! Now answer the questionnaire below.")

# -- QUESTIONNAIRE: After Recording, Before Analysis --
if st.session_state.get('recorded_file') and not st.session_state.get('analysis_done'):
    st.markdown("---")
    st.header("🧠 Reflect on What You Just Did")
    st.markdown("Be honest — there are no wrong answers.")

    q1_answer = st.radio(
        "**Q1: Did you understand the original audio?**",
        Q1_OPTIONS,
        index=None,
        key="q1_radio"
    )

    q2_answer = st.radio(
        "**Q2: How did you read the misheard text just now?**",
        Q2_OPTIONS,
        index=None,
        key="q2_radio"
    )

    # Store answers in session state
    if q1_answer and q2_answer:
        st.session_state['q1_answer'] = q1_answer
        st.session_state['q2_answer'] = q2_answer
        scenario_key = SCENARIO_KEY_MAP.get((q1_answer, q2_answer))
        st.session_state['scenario_key'] = scenario_key
        scenario = SUMMARIES["scenarios"].get(scenario_key, {})
        st.success(f"{scenario.get('emoji', '')} Scenario recorded. Now let the machine judge you.")
    else:
        st.warning("Please answer both questions before proceeding to analysis.")

    st.markdown("---")
    st.header("Step 3: Forensic Judgment")

    if not st.session_state.get('q1_answer') or not st.session_state.get('q2_answer'):
        st.button("⚖️ 3. Analyze Linguistic Passport", disabled=True)
        st.caption("Complete the questionnaire above to unlock analysis.")
    elif st.button("⚖️ 3. Analyze Linguistic Passport"):
        with st.spinner("Analyzing your acoustic skeleton..."):
            audio = whisper.load_audio(st.session_state['recorded_file'])
            audio = whisper.pad_or_trim(audio)

            mel = whisper.log_mel_spectrogram(audio, n_mels=m_model.dims.n_mels).to(m_model.device)
            _, probs = m_model.detect_language(mel)

            options = whisper.DecodingOptions(fp16=torch.cuda.is_available())
            result = whisper.decode(m_model, mel, options)

            st.session_state['top_probs'] = sorted(probs.items(), key=lambda x: x[1], reverse=True)[:5]
            st.session_state['machine_recorded_text'] = result.text
            st.session_state['analysis_done'] = True

# -- Final Report --
if st.session_state.get('analysis_done'):
    st.subheader("📊 Your Linguistic Passport")

    top_probs = st.session_state['top_probs']
    labels = [lang for lang, prob in top_probs]
    sizes = [prob for lang, prob in top_probs]

    other_prob = 1.0 - sum(sizes)
    if other_prob > 0.01:
        labels.append("Other")
        sizes.append(other_prob)

    fig, ax = plt.subplots(figsize=(5, 5))
    colors = plt.cm.Pastel1(np.linspace(0, 1, len(labels)))
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, colors=colors,
           wedgeprops={'edgecolor': 'white', 'linewidth': 1.5})
    ax.axis('equal')
    st.pyplot(fig)

    # --- 计算 sim_AC 和复合分数 ---
    text_A = st.session_state['true_text']
    text_B = st.session_state['machine_original_text']
    text_C = st.session_state['machine_recorded_text']
    original_lang = st.session_state.get('original_lang', '')

    # 饼状图中概率最高的语种
    top_lang = top_probs[0][0] if top_probs else ''
    top_prob = top_probs[0][1] if top_probs else 0.0

    # Whisper 语言代码 → database.json 里的语种名映射
    WHISPER_LANG_TO_NAME = {
        'zh': 'Chinese', 'en': 'English', 'es': 'Spanish',
        'hi': 'Hindi', 'ja': 'Japanese', 'ko': 'Korean',
    }
    detected_lang_name = WHISPER_LANG_TO_NAME.get(top_lang, top_lang)

    # 如果检测到的语种和原音频语种不同 → sim_AC 直接归零
    if detected_lang_name.lower() != original_lang.lower():
        sim_AC = 0.0
    else:
        sim_AC = difflib.SequenceMatcher(None, text_A, text_C).ratio()

    # 复合分数 = 饼状图最高概率 × sim_AC
    composite_score = round(top_prob * sim_AC * 100, 1)

    # 根据复合分数选择 verdict 档位
    if composite_score == 0:
        verdict_key = "zero"
    elif composite_score < 50:
        verdict_key = "low"
    elif composite_score <= 85:
        verdict_key = "mid"
    else:
        verdict_key = "high"

    # --- 两段式 Summary ---
    st.markdown("---")
    # 中文选中文，其余全英文
    lang_code = "zh" if user_home_lang == "Chinese" else "en"

    # 前半段：问卷 → 你对自己的认知（9 种场景）
    scenario_key = st.session_state.get('scenario_key')
    if scenario_key:
        scenario = SUMMARIES["scenarios"].get(scenario_key, {})
        scenario_emoji = scenario.get("emoji", "")
        scenario_text = scenario.get(lang_code, scenario.get("en", ""))

        st.subheader(f"{scenario_emoji} Your Self-Report")
        st.markdown(f"> {scenario_text}")

    # 显示复合分数
    st.metric(label="Machine Conviction Score", value=f"{composite_score}%",
              help="Top language probability × text similarity with original. Higher = the machine is more convinced you 'are' this language.")

    # 后半段：机器判决（4 档）
    verdict = SUMMARIES["verdicts"].get(verdict_key, {})
    verdict_emoji = verdict.get("emoji", "")
    verdict_text = verdict.get(lang_code, verdict.get("en", ""))

    st.subheader(f"{verdict_emoji} Machine's Verdict")
    st.markdown(f"> {verdict_text}")

    # --- The Three Truths ---
    st.markdown("---")
    st.subheader("📝 The Three Truths")

    st.write("**1. The Absolute Truth (真实原句):**")
    st.code(text_A, language=None)

    st.write("**2. Machine's Baseline (大模型听原音频):**")
    st.code(text_B, language=None)

    st.write("**3. Machine's Judgment of YOU (大模型听你的录音):**")
    st.code(text_C, language=None)
