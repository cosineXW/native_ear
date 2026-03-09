import streamlit as st
import whisper
import random
import os
import torch
import sounddevice as sd
import soundfile as sf
import numpy as np
import matplotlib.pyplot as plt
import json
import difflib

# --- 1. Basic Config & Model Loading ---
st.set_page_config(page_title="The Native Ear", page_icon="🎧", layout="centered")

@st.cache_resource
def load_whisper_models():
    # 只加载大模型用于准确的特征提取和法医鉴定
    return whisper.load_model("large")

with st.spinner("Initializing Whisper Forensic Model..."):
    m_large = load_whisper_models()

# 加载你的 JSON 剧本库
def load_database():
    with open('database.json', 'r', encoding='utf-8') as f:
        return json.load(f)

PREBAKED_DB = load_database()
ALL_NATIVE_OPTIONS = list(PREBAKED_DB.keys())

# --- 文本相似度算法 ---
def calculate_similarity(text1, text2):
    # 算出一个 0 到 100 的百分数
    if not text1 or not text2:
        return 0.0
    return round(difflib.SequenceMatcher(None, text1, text2).ratio() * 100, 1)

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
        # 随机抽取一个剧本
        script = random.choice(available_scripts)
        
        if os.path.exists(script["file"]):
            st.session_state['current_path'] = script["file"]
            st.session_state['original_lang'] = script["original_lang"]
            st.session_state['true_text'] = script["true_text"]
            st.session_state['fake_text'] = script["fake_text"]
            st.session_state['recorded_file'] = None 
            st.session_state['analysis_done'] = False
            
            # --- 核心新增：直接让大模型去听一遍“原声音频” ---
            with st.spinner("Machine is establishing baseline from the original audio..."):
                # 不做语言强加，看它到底听到什么
                res = m_large.transcribe(st.session_state['current_path'])
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
    
    RECORD_DURATION = 15
    SAMPLE_RATE = 16000
    
    if st.button(f"🎤 2. Start Recording ({RECORD_DURATION}s)"):
        with st.spinner(f'Recording for {RECORD_DURATION} seconds... Speak now!'):
            recording = sd.rec(int(RECORD_DURATION * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1, dtype='float32')
            sd.wait()
            temp_file = "_temp_realtime.wav"
            sf.write(temp_file, recording, SAMPLE_RATE)
            st.session_state['recorded_file'] = temp_file
            st.session_state['analysis_done'] = False 
            st.success("Recording complete!")

# -- Show recorded audio and Analysis --
if st.session_state.get('recorded_file'):
    st.audio(st.session_state['recorded_file'])
    
    st.markdown("---")
    st.header("Step 3: Forensic Judgment")
    if st.button("⚖️ 3. Analyze Linguistic Passport"):
        with st.spinner("Analyzing your acoustic skeleton..."):
            audio = whisper.load_audio(st.session_state['recorded_file'])
            audio = whisper.pad_or_trim(audio) 
            
            mel = whisper.log_mel_spectrogram(audio, n_mels=m_large.dims.n_mels).to(m_large.device)            
            _, probs = m_large.detect_language(mel)
            
            options = whisper.DecodingOptions(fp16=torch.cuda.is_available())
            result = whisper.decode(m_large, mel, options)
            
            st.session_state['top_probs'] = sorted(probs.items(), key=lambda x: x[1], reverse=True)[:5]
            st.session_state['machine_recorded_text'] = result.text
            st.session_state['analysis_done'] = True

# -- Final Report --
if st.session_state.get('analysis_done'):
    st.subheader("📊 Detected Language Distribution")
    
    # 1. 饼状图
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
    
    # 2. 句子展示
    st.markdown("---")
    st.subheader("📝 The Three Truths")
    
    text_A = st.session_state['true_text']
    text_B = st.session_state['machine_original_text']
    text_C = st.session_state['machine_recorded_text']
    
    st.write("**1. The Absolute Truth (真实原句):**")
    st.code(text_A, language=None)
    
    st.write("**2. Machine's Baseline (大模型听原音频):**")
    st.code(text_B, language=None)
    
    st.write("**3. Machine's Judgment of YOU (大模型听你的录音):**")
    st.code(text_C, language=None)
    
    # 3. 差值算法与总结
    st.markdown("---")
    st.subheader("📈 Algorithm Report: The Cost of Assimilation")
    
    sim_AB = calculate_similarity(text_A, text_B)
    sim_BC = calculate_similarity(text_B, text_C)
    sim_AC = calculate_similarity(text_A, text_C)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(label="Machine Accuracy\n(原声识别率)", value=f"{sim_AB}%", 
                  help="Similarity between True Sentence and Machine Baseline. Proves the machine CAN hear correctly when unbiased.")
    with col2:
        st.metric(label="Human Accommodation\n(人机同化率)", value=f"{sim_BC}%", 
                  help="Similarity between Machine Baseline and Your Recording. How much your pronunciation submitted to the machine's bias.")
    with col3:
        st.metric(label="Meaning Retention\n(原意保留度)", value=f"{sim_AC}%", delta="- Lost in Translation", delta_color="inverse",
                  help="Similarity between True Sentence and Your Recording. Shows how meaning is destroyed by forced assimilation.")

    st.info("💡 **Summary**: The data above reveals the violence of machine listening. Even if your 'Human Accommodation' score goes up, the 'Meaning Retention' plummets to near zero. You appeased the algorithm, but your voice lost its original truth.")