# 🎧 The Native Ear: Bias and Judgment in Machine Listening
An interactive audio-visual installation that explores linguistic bias, forced assimilation, and forensic judgment through the lens of machine listening models.

## 📌 Project Concept
"The Native Ear" reverses the traditional human-computer dynamic. Instead of machines trying to understand humans, humans are forced to accommodate the machine's auditory hallucinations. Using OpenAI's Whisper model, the project generates cross-lingual "misheard lyrics" (e.g., an English model mishearing Japanese) and evaluates how much the human user alters their pronunciation to appease the algorithm.

## 📂 Repository Structure
Ensure your local folder contains the following files before running:
- `app.py`: The main Streamlit application.
- `database.json`: The pre-baked cross-lingual hallucination scripts.
- `requirements.txt`: Python dependencies.
- `audio_samples/`: Folder containing the original audio files (.mp3).

## 🚀 Installation & Setup

**1. Clone or download this repository** to your local machine.

**2. Install dependencies:**
Open your terminal, navigate to the project folder, and run:
```bash
pip install -r requirements.txt

streamlit run app.py


# 🎧 The Native Ear (机器的原生耳)

这是一个探讨机器听觉中的语言偏见、强制同化（Forced Assimilation）以及算法法医级判定（Forensic Judgment）的交互式音视频装置作品。

## 📌 项目概念
"The Native Ear" 反转了传统的人机交互关系。在这个装置中，不再是机器努力去理解人类，而是**人类被迫去迎合机器的“听觉幻觉”**。

利用 OpenAI 的 Whisper 模型，本项目模拟了机器在面对未知语言时产生的跨语种“空耳”（例如：用英文模型的偏见去强行听译日语）。项目最终会生成一份数据报告，评估人类用户为了迎合这台充满偏见的算法，在多大程度上扭曲了自己的原始发音，以及在这个过程中丢失了多少真实的语义。

## 📂 项目结构
在运行代码之前，请确保你的本地文件夹包含以下核心内容：
- `app.py`: Streamlit 主程序应用。
- `database.json`: 预设的跨语种“发癫”空耳剧本库。
- `requirements.txt`: Python 依赖包清单。
- `audio_samples/`: 存放所有原始测试音频（.mp3）的文件夹。

## 🚀 快速上手 (Quick Start)

**1. 下载项目**
将本项目下载并解压到你的本地电脑，并进入该文件夹。

**2. 一键配置并启动**
打开终端（Terminal），直接复制并执行以下命令。它会自动安装所需的库并启动应用：

```bash
# 安装所有依赖库
pip install -r requirements.txt

# 启动交互装置
streamlit run app.py