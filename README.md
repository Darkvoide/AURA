# 🤖 AURA — Humanoid Robot Voice Assistant

> **A**rtificial **U**nified **R**obot **A**ssistant  
> Bilingual voice assistant supporting **English** and **Tamil (தமிழ்)** with **voice output for EVERY answer**.

---

## ✨ Features

- 🎤 **Voice Recognition**: Listens via microphone and recognizes English, Tamil, and Tanglish speech.
- 🧠 **Dynamic Long-Term Memory**: You can teach AURA new facts anytime! Say *"idha memory la ethiko: [fact]"* or *"remember this: [fact]"*. AURA saves them directly to `robot_memory.json` and uses them in future conversations.
- 🗣️ **Spoken Gentle Male Voice for EVERY Answer**: Speaks aloud every answer in a warm, gentle, calm male voice (`Puck` via Gemini 3.8 Flash TTS) for both Tamil and English.
- 👥 **Corrected Creator Grammar**: Respectfully recognizes Kishore, Mohandas, and Latheeswaran as young unmarried engineers at iGrid Lab.
- 🌐 **Tri-Lingual Support**: Understands **Tamil (தமிழ்)**, **Tanglish** (e.g. *"tamil la sollu"*, *"eppadi irukka"*), and **English**.
- 🎙️ **Automatic Voice-to-Voice**: When a microphone is plugged in, AURA automatically enables hands-free voice-to-voice communication. If no mic is detected, it falls back to typed input while still speaking every answer aloud.
- 🤖 **Robot Identity Commands**:
  - *"Hi I am AURA humanoid robot"*
  - *"My memory is Raspberry Pi 8GB RAM"*
  - *(Works in both English and Tamil!)*
- 🌐 **Google Gemini AI Engine**: Answers any question using Google Gemini AI (`gemini-2.5-flash`).
- 🔄 **Tamil & English Auto-Detection**: Answers in Tamil if you speak in Tamil; answers in English if you speak in English.

---

## 🚀 Quick Start

### 1. Run the Voice Assistant (Full Voice Mode)
```bash
python aura.py
```
*AURA will greet you aloud, listen to your microphone, and speak every answer out loud!*

### 2. Run in Text Mode (with Spoken Voice Output)
```bash
python aura_text_mode.py
```
*Type your questions in English or Tamil — AURA still **speaks every answer out loud**!*

### 3. Run System Check
```bash
python test_system.py
```
*Tests your microphone, Tamil voice, English voice, and Google Gemini AI connection.*

---

## 🗣️ Voice Commands to Try

| You Say (English) | You Say (Tamil) | AURA Speaks Aloud |
| :--- | :--- | :--- |
| **"Hi" / "Who are you?"** | **"வணக்கம்" / "நீ யார்?"** | Introduces itself as AURA humanoid robot |
| **"What is your memory?"** | **"உன் நினைவகம் என்ன?"** | "My memory is Raspberry Pi with 8 GB RAM..." |
| **"Who created you?"** | **"உன்னை உருவாக்கியது யார்?"** | Introduces Kishore, Mohandas, and Latheeswaran as young unmarried engineers |
| **"Remember this: [fact]"** | **"இதை memory-ல ஏத்திக்கோ: [fact]"** | Directly saves new facts into persistent memory (`robot_memory.json`) |
| **"What do you remember?"** | **"Memory-ல என்ன இருக்கு?"** | Recalls all dynamic learned memories |
| **"What is your purpose here?"** | **"உன் நோக்கம் என்ன?"** | Explains its role monitoring embedded systems and visitors at iGrid Lab |
| **"What is quantum computing?"** | **"சூரியன் என்றால் என்ன?"** | Answers query from Google Gemini AI in voice |
| **"Bye" / "Exit"** | **"நிறுத்து" / "போய் வருகிறேன்"** | Says goodbye in voice and shuts down |

---

## 🍓 Running on Raspberry Pi

1. Connect your USB microphone and speaker to your Raspberry Pi.
2. Install audio utilities:
   ```bash
   sudo apt-get update
   sudo apt-get install -y mpg123 espeak alsa-utils libportaudio2
   ```
3. Install Python requirements:
   ```bash
   pip install -r requirements.txt
   ```
4. Start AURA:
   ```bash
   python aura.py
   ```
