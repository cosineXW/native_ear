# 🎧 The Native Ear: Bias and Judgment in Machine Listening

An interactive audio-visual installation that explores linguistic bias, forced assimilation, and forensic judgment through the lens of machine listening models.

## 📌 Project Concept

"The Native Ear" reverses the traditional human-computer dynamic. Instead of machines trying to understand humans, humans are forced to accommodate the machine's auditory hallucinations. Using OpenAI's Whisper model, the project generates cross-lingual "misheard lyrics" (e.g., an English model mishearing Japanese) and evaluates how much the human user alters their pronunciation to appease the algorithm.

## 🆕 Interactive Intro Slideshow

Before the test begins, users are guided through a 4-page visual introduction (with bilingual Chinese/English support) that explains:

1. **The real-world stakes** — how asylum seekers' voices are used to determine their identity
2. **What LADO is** — Language Analysis for the Determination of Origin, and why accent ≠ identity
3. **How the machine "ear" works** — the concept of misheard lyrics (空耳) and Whisper's role
4. **What users will do** — the three-step test flow (listen → read aloud → be judged)

Each slide features a custom SVG illustration that switches language along with the text. A language toggle (中/EN) in the top-right corner controls both text and illustration language.

## 📂 Repository Structure

Ensure your local folder contains the following files before running:

- `app.py`: The main Streamlit application (includes intro slideshow + test flow).
- `database.json`: The pre-baked cross-lingual hallucination scripts.
- `summaries.json`: Bilingual (中/EN) scenario descriptions and machine verdicts.
- `requirements.txt`: Python dependencies.
- `audio_samples/`: Folder containing the original audio files (.mp3).
- `article.pdf`: Source article — Michelle Pfeifer, "The Native Ear: Accented Testimonial Desire and Asylum" (2023).
- `9_summaries.md`: Design documentation for the 9 scenario summaries.

## 🚀 Installation & Setup

**1. Clone or download this repository** to your local machine.

**2. Install dependencies:**

```bash
pip install -r requirements.txt
```

**3. Run the app:**

```bash
streamlit run app.py
```

The app will open in your browser. You'll see the intro slideshow first — read through it, then click "Start the Test" to begin.

---

# 🎧 The Native Ear (机器的原生耳)

这是一个探讨机器听觉中的语言偏见、强制同化（Forced Assimilation）以及算法法医级判定（Forensic Judgment）的交互式音视频装置作品。

## 📌 项目概念

"The Native Ear" 反转了传统的人机交互关系。在这个装置中，不再是机器努力去理解人类，而是**人类被迫去迎合机器的"听觉幻觉"**。

利用 OpenAI 的 Whisper 模型，本项目模拟了机器在面对未知语言时产生的跨语种"空耳"（例如：用英文模型的偏见去强行听译日语）。项目最终会生成一份数据报告，评估人类用户为了迎合这台充满偏见的算法，在多大程度上扭曲了自己的原始发音，以及在这个过程中丢失了多少真实的语义。

## 🆕 交互式引导幻灯片

测试开始前，用户会先看到 4 页可视化引导（支持中英双语切换），内容包括：

1. **真实世界的利害关系** —— 难民的声音如何被用来判定他们的身份
2. **什么是 LADO** —— 语言来源鉴定分析，以及为什么口音 ≠ 身份
3. **机器"耳朵"如何工作** —— 空耳概念和 Whisper 的角色
4. **你要做什么** —— 三步测试流程（听 → 念 → 被审判）

每一页都配有代码生成的 SVG 插图，切换语言时插图上的文字也会跟着变。右上角的语言开关控制全部内容。

## 📂 项目结构

在运行代码之前，请确保你的本地文件夹包含以下核心内容：

- `app.py`: Streamlit 主程序（包含引导幻灯片 + 测试流程）。
- `database.json`: 预设的跨语种"空耳"剧本库。
- `summaries.json`: 中英双语场景描述与机器判决文案。
- `requirements.txt`: Python 依赖包清单。
- `audio_samples/`: 存放所有原始测试音频（.mp3）的文件夹。
- `article.pdf`: 参考文献 — Michelle Pfeifer,《The Native Ear》(2023)。
- `9_summaries.md`: 9 种问卷场景的设计文档。

## 🚀 快速上手

**1. 下载项目** 并进入文件夹。

**2. 安装依赖：**

```bash
pip install -r requirements.txt
```

**3. 启动应用：**

```bash
streamlit run app.py
```

应用会在浏览器中打开。你会先看到引导幻灯片——读完后点击「开始测试」进入正式流程。
