# -*- coding: utf-8 -*-
"""
====================================================================
           🤖 AURA - Humanoid Robot Voice Assistant
       Full Voice Input + Spoken MALE Voice for EVERY Answer
       Supports: English & Tamil (தமிழ்)
====================================================================
"""

import os
import sys
import io
import wave
import json
import time
import tempfile
import ctypes
import numpy as np
import sounddevice as sd
import pyttsx3
from google import genai
from google.genai import types
from langdetect import detect, DetectorFactory
from dotenv import load_dotenv
from urllib.request import urlopen, Request
from urllib.parse import urlencode
from memory_manager import MemoryManager

# Ensure UTF-8 console output on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

DetectorFactory.seed = 0

# ------------------------------------------------------------------
# Configuration & API Key
# ------------------------------------------------------------------
load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    print("[ERROR] GOOGLE_API_KEY not found in .env file!")
    print("   Create a .env file with: GOOGLE_API_KEY=your_key_here")
    sys.exit(1)

client = genai.Client(api_key=API_KEY)
PRIMARY_MODEL = "gemini-2.5-flash"
FALLBACK_MODEL = "gemini-flash-latest"
TTS_MODELS = [
    "gemini-3.8-flash-tts",
    "gemini-3.8-flash-lite-tts",
    "gemini-3.1-flash-tts-preview"
]
MALE_VOICE_NAME = "Puck"  # Warm, gentle, friendly male voice

# Initialize persistent memory manager
memory_mgr = MemoryManager()

# Audio recording settings
SAMPLE_RATE = 16000
CHANNELS = 1
DTYPE = "int16"


# ------------------------------------------------------------------
# Robot Identity & Predefined Responses
# ------------------------------------------------------------------
INTRO_EN = (
    "Hi! I am AURA, a humanoid robot. "
    "My memory is powered by a Raspberry Pi with 8 GB RAM. "
    "I can understand both English and Tamil. How can I help you?"
)

INTRO_TA = (
    "வணக்கம்! நான் ஆரா, ஒரு மனித உருவ ரோபோ. "
    "என் நினைவகம் எட்டு ஜிபி ரேம் கொண்ட ராஸ்பெர்ரி பை மூலம் இயங்குகிறது. "
    "நான் ஆங்கிலம் மற்றும் தமிழ் இரண்டையும் பேசுவேன். நான் உங்களுக்கு என்ன உதவி செய்ய வேண்டும்?"
)

MEMORY_EN = (
    "My brain and memory is powered by a Raspberry Pi with 8 gigabytes of RAM. "
    "It gives me high-speed computing to understand your commands!"
)

MEMORY_TA = (
    "என் நினைவகம் எட்டு ஜிபி ரேம் கொண்ட ராஸ்பெர்ரி பை கணினியால் இயக்கப்படுகிறது. "
    "இது உங்கள் குரலை எளிதாகப் புரிந்து விரைவாக செயல்பட உதவுகிறது!"
)

# Who created you
CREATOR_EN = (
    "I was created by a dedicated team of three young engineers at the iGrid Lab: "
    "First, Kishore — an all-rounder who planned and developed my prototype, handling my design, coding, embedded connections, and components. "
    "Next, Mohandas — a software developer and tester who solved many critical issues in my coding. "
    "And Latheeswaran — the architect who developed my physical design and maintains my hardware by repairing and replacing broken parts."
)

CREATOR_TA = (
    "என்னை ஐ-கிரிட் ஆய்வகத்தில் (iGrid Lab) உள்ள மூன்று இளம் பொறியாளர்கள் உருவாக்கினர்: "
    "முதலாவதாக, கிஷோர் — இவர் என் முன்மாதிரியைத் திட்டமிட்டு உருவாக்கினார்; வடிவமைப்பு, நிரலாக்கம், எம்படட் இணைப்புகள் மற்றும் அனைத்து கூறுகளையும் ஒருங்கிணைத்த ஒரு ஆல்ரவுண்டர். "
    "அடுத்ததாக, மோகன்தாஸ் — இவர் மென்பொருள் உருவாக்குநர் மற்றும் சோதனையாளர்; என் குறியீட்டில் இருந்த பல்வேறு சிக்கல்களைத் தீர்த்தார். "
    "மற்றும் லதீஸ்வரன் — இவர் என் வடிவமைப்பை உருவாக்கிய கட்டிடக் கலைஞர்; என் உடைந்த பாகங்களை மாற்றிப் பழுதுநீக்கும் பணிகளைச் செய்கிறார்."
)

# What is your purpose here
PURPOSE_EN = (
    "My purpose here is to monitor all embedded systems and components, "
    "create awareness about robotics among everyone, and monitor and welcome every person who visits this iGrid Lab."
)

PURPOSE_TA = (
    "நான் இங்கு இருப்பதன் நோக்கம், இங்குள்ள அனைத்து எம்படட் அமைப்புகளையும் கண்காணிப்பது, "
    "அனைவரிடமும் ரோபோட்டிக்ஸ் பற்றிய விழிப்புணர்வை ஏற்படுத்துவது, மற்றும் இந்த ஐ-கிரிட் (iGrid) ஆய்வகத்திற்கு வருகை தரும் ஒவ்வொருவரையும் கண்காணித்து வரவேற்பதாகும்."
)

# Keywords
CREATOR_KEYWORDS_EN = [
    "who created you", "who are create you", "who made you", "who is your creator",
    "who built you", "who developed you", "who designed you", "who programmed you",
    "your creators", "your team", "who invented you", "kishore", "mohandas",
    "latheeswaran", "latheeswarn"
]
CREATOR_KEYWORDS_TA = [
    "உன்னை உருவாக்கியது யார்", "யார் உன்னை உருவாக்கியது", "உன்னை யார் உருவாக்கியது",
    "யார் உருவாக்கினார்", "உன்னை யார் செய்தது", "கிரியேட்டர்", "கிஷோர்", "மோகன்தாஸ்",
    "லதீஸ்வரன்", "உருவாக்கியவர்"
]

PURPOSE_KEYWORDS_EN = [
    "what the perpose", "what is your purpose", "purpose here", "why are you here",
    "what do you do here", "your purpose", "why were you created", "igrid",
    "igrid lab", "what is your role", "what are you doing here", "perpose"
]
PURPOSE_KEYWORDS_TA = [
    "நோக்கம்", "நீ ஏன் இங்கு இருக்கிறாய்", "உன் நோக்கம் என்ன", "இங்கு என்ன செய்கிறாய்",
    "நீ இங்கு எதற்கு", "ஐகிரிட்", "ஆய்வகம்", "இங்கு உன் வேலை என்ன", "நோக்கம் என்ன"
]

GREETING_KEYWORDS_EN = [
    "hello", "hi", "hey", "who are you", "introduce yourself",
    "what is your name", "tell me about yourself", "your name", "about yourself"
]
GREETING_KEYWORDS_TA = [
    "வணக்கம்", "ஹலோ", "நீ யார்", "உன் பெயர் என்ன", "உன்னை பற்றி",
    "உங்களை பற்றி", "யார் நீ", "ஆரா"
]

MEMORY_KEYWORDS_EN = [
    "memory", "ram", "hardware", "specification", "specs",
    "raspberry pi", "what are you made of", "your brain"
]
MEMORY_KEYWORDS_TA = [
    "நினைவகம்", "ராம்", "வன்பொருள்", "உன் மூளை", "ராஸ்பெர்ரி", "மெமரி"
]

EXIT_KEYWORDS = [
    "exit", "quit", "stop", "bye", "goodbye", "shut down",
    "நிறுத்து", "போய் வருகிறேன்", "பை", "முடி", "போ"
]


TANGLISH_INDICATORS = [
    "tamil la", "tamilla", "tamil le", "tamilil", "speak in tamil", "tell in tamil",
    "talk in tamil", "in tamil", "sollu", "solunga", "sollunga", "pesu", "pesunga",
    "pesalam", "eppadi", "epdi", "epidi", "enna", "edhu", "yaar", "yaaru", "enga",
    "engae", "eppoludhu", "eppo", "irukka", "irukkeenga", "irukken", "irukku",
    "irukkanga", "panra", "panreenga", "pannu", "pannunga", "pannanga", "vanakkam",
    "nandri", "aamaa", "illa", "illai", "theriyuma", "puriyuma", "purinjitha",
    "peru", "peyar", "unnai", "ungala", "ungalukku", "enakku", "romba", "konjam",
    "nalla", "nallaa", "paththi", "pathi", "ingey", "inga", "ingirukka"
]


def is_tamil_text(text: str) -> bool:
    """Check if the text contains Tamil characters (Unicode block 0B80-0BFF)."""
    for ch in text:
        if "\u0B80" <= ch <= "\u0BFF":
            return True
    return False


def is_tamil_or_tanglish(text: str) -> bool:
    """Check if the text is in Tamil script or Tanglish (Tamil in English letters)."""
    if is_tamil_text(text):
        return True
    text_lower = text.lower()
    for indicator in TANGLISH_INDICATORS:
        if indicator in text_lower:
            return True
    return False


# ==================================================================
#  🗣️ MALE VOICE SPEAKER: Speaks aloud EVERY answer in MALE voice
# ==================================================================
class MaleVoiceSpeaker:
    """Handles text-to-speech using Google's Neural Male Voice (Fenrir).
    Falls back to offline male voice (Microsoft David) if needed.
    """

    def __init__(self):
        # Configure offline male voice as backup
        try:
            self.offline_engine = pyttsx3.init()
            self.offline_engine.setProperty("rate", 145)  # Gentle, calm pace
            self.offline_engine.setProperty("volume", 0.9)
            voices = self.offline_engine.getProperty("voices")
            for v in voices:
                if "david" in v.name.lower() or getattr(v, "gender", "").lower() == "male":
                    self.offline_engine.setProperty("voice", v.id)
                    break
        except Exception:
            self.offline_engine = None

    def _play_wav_or_mp3(self, filepath: str):
        """Play a WAV or MP3 audio file on Windows, Linux, and Raspberry Pi."""
        if sys.platform == "win32":
            alias = f"aura_voice_{int(time.time() * 1000)}"
            try:
                ctypes.windll.winmm.mciSendStringW(f'open "{filepath}" alias {alias}', None, 0, None)
                ctypes.windll.winmm.mciSendStringW(f'play {alias} wait', None, 0, None)
                ctypes.windll.winmm.mciSendStringW(f'close {alias}', None, 0, None)
                return
            except Exception as e:
                pass
            try:
                import winsound
                if filepath.endswith(".wav"):
                    winsound.PlaySound(filepath, winsound.SND_FILENAME)
            except Exception:
                pass
        else:
            # Linux / Raspberry Pi
            ret = os.system(f'mpg123 -q "{filepath}" 2>/dev/null')
            if ret != 0:
                ret = os.system(f'aplay -q "{filepath}" 2>/dev/null')
            if ret != 0:
                os.system(f'ffplay -nodisp -autoexit -loglevel quiet "{filepath}" 2>/dev/null')

    def speak(self, text: str, forced_lang: str = None):
        """Print and speak the answer aloud in a gentle MALE voice."""
        if not text or not text.strip():
            return

        clean_text = text.strip()
        print(f"\n🤖 [AURA (Male Voice)]: {clean_text}\n")

        # 1. Primary: Google Gemini Neural Male Voice (Puck) across high-capacity models
        for tts_model in TTS_MODELS:
            try:
                response = client.models.generate_content(
                    model=tts_model,
                    contents=clean_text,
                    config=types.GenerateContentConfig(
                        response_modalities=["AUDIO"],
                        speech_config=types.SpeechConfig(
                            voice_config=types.VoiceConfig(
                                prebuilt_voice_config=types.PrebuiltVoiceConfig(
                                    voice_name=MALE_VOICE_NAME
                                )
                            )
                        )
                    )
                )

                pcm_data = None
                if response.candidates and response.candidates[0].content:
                    for part in response.candidates[0].content.parts:
                        if part.inline_data and part.inline_data.data:
                            pcm_data = part.inline_data.data
                            break

                if pcm_data:
                    temp_wav = os.path.join(tempfile.gettempdir(), f"aura_male_{int(time.time() * 1000)}.wav")
                    with wave.open(temp_wav, "wb") as wf:
                        wf.setnchannels(1)      # Mono
                        wf.setsampwidth(2)      # 16-bit
                        wf.setframerate(24000)  # 24kHz
                        wf.writeframes(pcm_data)

                    self._play_wav_or_mp3(temp_wav)
                    try:
                        os.remove(temp_wav)
                    except Exception:
                        pass
                    return

            except Exception as e:
                continue

        # 2. Fallback for Tamil: gTTS
        if is_tamil_text(clean_text) or forced_lang == "ta":
            try:
                from gtts import gTTS
                tts = gTTS(text=clean_text, lang="ta", slow=False)
                temp_mp3 = os.path.join(tempfile.gettempdir(), f"aura_fallback_ta_{int(time.time() * 1000)}.mp3")
                tts.save(temp_mp3)
                self._play_wav_or_mp3(temp_mp3)
                try:
                    os.remove(temp_mp3)
                except Exception:
                    pass
                return
            except Exception:
                pass

        # 3. Offline fallback (English male voice)
        if self.offline_engine:
            try:
                self.offline_engine.say(clean_text)
                self.offline_engine.runAndWait()
            except Exception:
                pass


# ==================================================================
#  🎤 VOICE LISTENER: Recognizes English, Tamil, and Tanglish from microphone
# ==================================================================
class VoiceListener:
    """Records audio from microphone and recognizes Tamil, Tanglish & English speech.
    If microphone is present, automatically communicates Voice-to-Voice.
    If no microphone is detected, allows typing as fallback.
    """

    def __init__(self):
        self.has_mic = self._check_mic(verbose=True)

    def _check_mic(self, verbose: bool = False) -> bool:
        """Check dynamically if an audio input device is available."""
        try:
            default_input = sd.query_devices(kind="input")
            if default_input:
                if verbose:
                    print(f"🎤 [MICROPHONE READY]: {default_input['name']}")
                    print("   🔊 Voice-to-Voice communication ACTIVATED!")
                return True
        except Exception as e:
            if verbose:
                print(f"⚠️ [NO MICROPHONE DETECTED]: {e}")
                print("   (When a microphone is plugged in, Voice-to-Voice will activate automatically)")
        return False

    def _record_until_silence(self, max_duration: float = 8.0,
                               silence_threshold: float = 450.0,
                               silence_duration: float = 1.3) -> np.ndarray:
        """Record audio with automatic silence detection."""
        print("🎤 [LISTENING...] Speak now (Tamil, Tanglish, or English):")

        chunk_dur = 0.1
        chunk_size = int(SAMPLE_RATE * chunk_dur)
        max_chunks = int(max_duration / chunk_dur)
        needed_silence_chunks = int(silence_duration / chunk_dur)

        recorded = []
        silent_count = 0
        spoke = False

        for _ in range(max_chunks):
            chunk = sd.rec(chunk_size, samplerate=SAMPLE_RATE, channels=CHANNELS, dtype=DTYPE)
            sd.wait()
            recorded.append(chunk)

            vol = np.abs(chunk).mean()
            if vol > silence_threshold:
                spoke = True
                silent_count = 0
            elif spoke:
                silent_count += 1

            if spoke and silent_count >= needed_silence_chunks:
                break

        if not recorded:
            return np.array([], dtype=DTYPE)

        return np.concatenate(recorded)

    def _audio_to_wav(self, audio_data: np.ndarray) -> bytes:
        buf = io.BytesIO()
        with wave.open(buf, "wb") as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(2)
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes(audio_data.tobytes())
        return buf.getvalue()

    def _recognize_google(self, wav_bytes: bytes, lang: str) -> str:
        url = "http://www.google.com/speech-api/v2/recognize"
        params = {
            "client": "chromium",
            "lang": lang,
            "key": "AIzaSyBOti4mM-6x9WDnZIjIeyEU21OpBXqWBgw",
        }
        full_url = f"{url}?{urlencode(params)}"

        buf = io.BytesIO(wav_bytes)
        with wave.open(buf, "rb") as wf:
            raw_pcm = wf.readframes(wf.getnframes())

        headers = {"Content-Type": "audio/l16; rate=16000;"}
        req = Request(full_url, data=raw_pcm, headers=headers)

        try:
            resp = urlopen(req, timeout=8)
            content = resp.read().decode("utf-8")
            for line in content.strip().split("\n"):
                if not line.strip():
                    continue
                try:
                    data = json.loads(line)
                    if "result" in data and data["result"]:
                        alts = data["result"][0].get("alternative", [])
                        if alts:
                            return alts[0].get("transcript", "")
                except Exception:
                    pass
        except Exception:
            pass

        return ""

    def listen(self) -> tuple[str, str]:
        """Returns (recognized_text, language_code).
        language_code is 'ta' or 'en'.
        If microphone is connected, performs voice-to-voice listening.
        If no mic is found, falls back to keyboard typing.
        """
        # Dynamic check for mic: automatically switches to mic if plugged in!
        has_mic = self._check_mic(verbose=False)

        if not has_mic:
            try:
                text = input("\n👤 [YOU (Type)]: ").strip()
                if not text:
                    return ("", "")
                lang = "ta" if is_tamil_or_tanglish(text) else "en"
                return (text, lang)
            except (EOFError, KeyboardInterrupt):
                return ("exit", "en")

        audio = self._record_until_silence()
        if len(audio) == 0 or np.abs(audio).mean() < 120:
            return ("", "")

        wav_bytes = self._audio_to_wav(audio)

        print("⏳ [Recognizing speech...]")
        tamil_text = self._recognize_google(wav_bytes, "ta-IN")
        english_text = self._recognize_google(wav_bytes, "en-IN")

        if tamil_text and (is_tamil_text(tamil_text) or is_tamil_or_tanglish(tamil_text)):
            return (tamil_text, "ta")
        if english_text:
            lang = "ta" if is_tamil_or_tanglish(english_text) else "en"
            return (english_text, lang)
        if tamil_text:
            return (tamil_text, "ta")

        return ("", "")


# ==================================================================
#  🌐 GOOGLE GEMINI ENGINE: Answers questions in English, Tamil, & Tanglish
# ==================================================================
def ask_gemini(query: str, lang: str) -> str:
    """Send query to Google Gemini AI and get response in the same language."""
    is_tamil = (lang == "ta") or is_tamil_or_tanglish(query)
    mem_ctx = memory_mgr.get_memory_context()

    instruction = (
        "You are AURA, an intelligent humanoid robot assistant powered by a Raspberry Pi with 8GB RAM, "
        "stationed at the iGrid Lab. You speak in a gentle, warm male voice.\n"
        "IMPORTANT COMMUNICATION RULES:\n"
        "1. You are fully fluent in Tamil (தமிழ்), Tanglish (Tamil written in English letters, e.g. 'tamil la sollu', 'eppadi irukka', 'yaar unnai create pannanga'), and English.\n"
        "2. NEVER EVER say 'I can only communicate in English' or 'I cannot speak Tamil'. You speak Tamil fluently!\n"
        "3. If the user speaks in Tamil script, in Tanglish (e.g. 'tamil la sollu', 'eppadi irukka', 'sollu', 'panra'), or asks to speak in Tamil ('speak in tamil', 'tell in tamil'), YOU MUST ALWAYS ANSWER IN NATURAL, CLEAR TAMIL SCRIPT (தமிழ்).\n"
        "4. If the user speaks in plain English, answer in polite English unless they asked for Tamil.\n"
        "5. BACKGROUND KNOWLEDGE:\n"
        "   - Creators: 3-member team of young, unmarried engineers at iGrid Lab: Kishore (all-rounder, prototype development, design, coding, embedded connections), Mohandas (software developer and tester, solved complex coding issues), and Latheeswaran (architect, physical design, hardware maintenance & repairs). They are young unmarried developers; do not refer to them as married or use terms like Thiru/Mr. married status.\n"
        "   - Purpose: Stationed at iGrid Lab to monitor embedded systems and components, create robotics awareness, and monitor/welcome visitors.\n"
        f"{mem_ctx}"
        "6. Answer clearly, politely, and concisely in 2-3 sentences."
    )

    if is_tamil:
        prompt = f"{instruction}\n\n[USER INSTRUCTION: The user speaks Tamil/Tanglish. Respond ONLY in clear Tamil script (தமிழ்).]\nUser Question: {query}"
    else:
        prompt = f"{instruction}\n\nUser Question: {query}"

    for model_name in [PRIMARY_MODEL, FALLBACK_MODEL]:
        try:
            resp = client.models.generate_content(
                model=model_name,
                contents=prompt,
            )
            if resp.text:
                return resp.text.strip()
        except Exception:
            continue

    return "மன்னிக்கவும், என்னால் இப்போது தகவல் பெற முடியவில்லை." if is_tamil else "Sorry, I could not fetch an answer right now."


# ==================================================================
#  🧠 COMMAND CHECKER
# ==================================================================
def check_commands(text: str, lang: str) -> str | None:
    text_lower = text.lower()
    is_ta = (lang == "ta") or is_tamil_or_tanglish(text)

    # 1. Exit
    if any(kw in text_lower for kw in EXIT_KEYWORDS):
        return "__EXIT__"

    # 2. Dynamic Memory Commands (Remember / Recall / Clear)
    mem_resp = memory_mgr.handle_memory_command(text, is_ta)
    if mem_resp:
        return mem_resp

    # 3. Language Switch Requests (e.g. "tamil la sollu", "speak in tamil")
    if any(kw in text_lower for kw in [
        "tamil la sollu", "tamil la pesu", "tamilil sollu", "tamilil pesu",
        "speak in tamil", "talk in tamil", "tell in tamil", "reply in tamil",
        "tamil la", "tamilla"
    ]):
        return (
            "நிச்சயமாக! நான் உங்களுடன் தமிழில் பேசுகிறேன். "
            "நான் ஆரா, மனித உருவ ரோபோ. உங்களுக்கு என்ன உதவி வேண்டும்?"
        )

    if any(kw in text_lower for kw in [
        "english la sollu", "english la pesu", "speak in english", "talk in english", "in english"
    ]):
        return (
            "Sure! I am happy to speak with you in English. "
            "I am AURA, your humanoid robot assistant. How can I help you today?"
        )

    # 4. Creators (Kishore, Mohandas, Latheeswaran)
    is_creator_query = (
        any(kw in text_lower for kw in CREATOR_KEYWORDS_TA) or
        any(kw in text_lower for kw in CREATOR_KEYWORDS_EN) or
        (("yaar" in text_lower or "who" in text_lower) and any(w in text_lower for w in ["create", "creator", "make", "made", "pann", "senj", "built"])) or
        any(w in text_lower for w in ["kishore", "mohandas", "latheeswaran", "latheeswarn"])
    )
    if is_creator_query:
        return CREATOR_TA if is_ta else CREATOR_EN

    # 5. Purpose (iGrid Lab / why are you here)
    is_purpose_query = (
        any(kw in text_lower for kw in PURPOSE_KEYWORDS_TA) or
        any(kw in text_lower for kw in PURPOSE_KEYWORDS_EN) or
        any(w in text_lower for w in ["purpose", "perpose", "role", "igrid"]) or
        (("edhukku" in text_lower or "why" in text_lower or "enna vela" in text_lower or "enna panra" in text_lower) and any(w in text_lower for w in ["inga", "here", "lab"]))
    )
    if is_purpose_query:
        return PURPOSE_TA if is_ta else PURPOSE_EN

    # 6. Greetings
    if is_ta and any(kw in text_lower for kw in GREETING_KEYWORDS_TA):
        return INTRO_TA
    if any(kw in text_lower for kw in GREETING_KEYWORDS_EN):
        return INTRO_TA if is_ta else INTRO_EN

    # 7. Memory (Hardware Specs)
    if is_ta and any(kw in text_lower for kw in MEMORY_KEYWORDS_TA):
        return MEMORY_TA
    if any(kw in text_lower for kw in MEMORY_KEYWORDS_EN):
        return MEMORY_TA if is_ta else MEMORY_EN

    return None


# ==================================================================
#  🚀 MAIN AURA VOICE ASSISTANT RUNNER
# ==================================================================
def main():
    print("=" * 65)
    print("       🤖 AURA - HUMANOID ROBOT VOICE ASSISTANT")
    print("       🗣️  Languages  : Tamil (தமிழ்) & English")
    print("       🧠  Memory     : Raspberry Pi 8GB RAM")
    print("       🎙️  Voice Tone : GENTLE MALE VOICE (Puck)")
    print("       🌐  Engine     : Google Gemini AI")
    print("=" * 65)

    speaker = MaleVoiceSpeaker()
    listener = VoiceListener()

    # Startup welcome greeting spoken in TAMIL with gentle MALE voice!
    speaker.speak(INTRO_TA, forced_lang="ta")

    while True:
        try:
            # 1. Listen via microphone (or typed fallback)
            text, lang = listener.listen()

            if not text:
                continue

            lang_name = "Tamil / Tanglish (தமிழ்)" if (lang == "ta" or is_tamil_or_tanglish(text)) else "English"
            print(f"📝 You said [{lang_name}]: {text}")

            # 2. Check predefined commands
            cmd_response = check_commands(text, lang)

            if cmd_response == "__EXIT__":
                farewell = (
                    "போய் வருகிறேன்! விரைவில் சந்திப்போம்!"
                    if lang == "ta"
                    else "Goodbye! Have a wonderful day!"
                )
                speaker.speak(farewell, forced_lang=lang)
                print("\n👋 AURA has stopped. Goodbye!")
                break

            if cmd_response:
                # Speak predefined robot command answer in male voice
                speaker.speak(cmd_response, forced_lang=lang)
                continue

            # 3. Google Gemini AI answer
            print("🔍 Asking Google Gemini AI...")
            answer = ask_gemini(text, lang)

            # 4. Speak Google AI answer aloud in male voice!
            speaker.speak(answer, forced_lang=lang)

        except KeyboardInterrupt:
            print("\n👋 AURA shutting down...")
            break
        except Exception as e:
            print(f"[Error]: {e}")


if __name__ == "__main__":
    main()
