# -*- coding: utf-8 -*-
"""
====================================================================
           🤖 AURA - Text Mode (with MALE Voice Output)
       Type your questions, and AURA speaks aloud in a MALE voice!
       Supports: English & Tamil (தமிழ்)
====================================================================
"""

import os
import sys
import wave
import time
import tempfile
import pyttsx3
from google import genai
from google.genai import types
from dotenv import load_dotenv
from memory_manager import MemoryManager

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

load_dotenv()
API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    print("[ERROR] GOOGLE_API_KEY not found in .env file!")
    sys.exit(1)

client = genai.Client(api_key=API_KEY)
PRIMARY_MODEL = "gemini-2.5-flash"
FALLBACK_MODEL = "gemini-flash-latest"
TTS_MODELS = [
    "gemini-3.8-flash-tts",
    "gemini-3.8-flash-lite-tts",
    "gemini-3.1-flash-tts-preview"
]
MALE_VOICE_NAME = "Puck"  # Gentle, warm male voice

# Initialize persistent memory manager
memory_mgr = MemoryManager()

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
    "First, Kishore — he planned and developed my prototype as an all-rounder handling my design, coding, embedded connections, and components. "
    "Next, Mohandas — he is a software developer and tester who solved many critical issues in my coding. "
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
    "what is your name", "tell me about yourself", "your name"
]
GREETING_KEYWORDS_TA = [
    "வணக்கம்", "ஹலோ", "நீ யார்", "உன் பெயர் என்ன", "உன்னை பற்றி", "ஆரா"
]

MEMORY_KEYWORDS_EN = [
    "memory", "ram", "hardware", "specification", "specs",
    "raspberry pi", "what are you made of", "your brain"
]
MEMORY_KEYWORDS_TA = [
    "நினைவகம்", "ராம்", "வன்பொருள்", "உன் மூளை", "ராஸ்பெர்ரி", "மெமரி"
]

EXIT_KEYWORDS = ["exit", "quit", "stop", "bye", "goodbye", "நிறுத்து", "போய் வருகிறேன்", "பை"]


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
    for ch in text:
        if "\u0B80" <= ch <= "\u0BFF":
            return True
    return False


def is_tamil_or_tanglish(text: str) -> bool:
    if is_tamil_text(text):
        return True
    text_lower = text.lower()
    for indicator in TANGLISH_INDICATORS:
        if indicator in text_lower:
            return True
    return False


class MaleVoiceSpeaker:
    def __init__(self):
        try:
            self.offline_engine = pyttsx3.init()
            self.offline_engine.setProperty("rate", 145)
            self.offline_engine.setProperty("volume", 0.9)
            voices = self.offline_engine.getProperty("voices")
            for v in voices:
                if "david" in v.name.lower() or getattr(v, "gender", "").lower() == "male":
                    self.offline_engine.setProperty("voice", v.id)
                    break
        except Exception:
            self.offline_engine = None

    def _play_wav_or_mp3(self, filepath: str):
        if sys.platform == "win32":
            alias = f"aura_voice_{int(time.time() * 1000)}"
            try:
                ctypes.windll.winmm.mciSendStringW(f'open "{filepath}" alias {alias}', None, 0, None)
                ctypes.windll.winmm.mciSendStringW(f'play {alias} wait', None, 0, None)
                ctypes.windll.winmm.mciSendStringW(f'close {alias}', None, 0, None)
                return
            except Exception:
                pass
            try:
                import winsound
                if filepath.endswith(".wav"):
                    winsound.PlaySound(filepath, winsound.SND_FILENAME)
            except Exception:
                pass
        else:
            ret = os.system(f'mpg123 -q "{filepath}" 2>/dev/null')
            if ret != 0:
                os.system(f'aplay -q "{filepath}" 2>/dev/null')

    def speak(self, text: str, forced_lang: str = None):
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
            except Exception:
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

        # 3. Fallback for English: pyttsx3 offline male voice
        if self.offline_engine:
            try:
                self.offline_engine.say(clean_text)
                self.offline_engine.runAndWait()
            except Exception:
                pass


def ask_gemini(query: str, is_tamil: bool) -> str:
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

    if is_tamil or is_tamil_or_tanglish(query):
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

    return "மன்னிக்கவும், என்னால் இப்போது தகவல் பெற முடியவில்லை." if (is_tamil or is_tamil_or_tanglish(query)) else "Sorry, I could not fetch an answer right now."


def check_commands(text: str, is_tamil: bool) -> str | None:
    text_lower = text.lower()
    is_ta = is_tamil or is_tamil_or_tanglish(text)

    # 1. Exit
    if any(kw in text_lower for kw in EXIT_KEYWORDS):
        return "__EXIT__"

    # 2. Dynamic Memory Commands (Remember / Recall / Clear)
    mem_resp = memory_mgr.handle_memory_command(text, is_ta)
    if mem_resp:
        return mem_resp

    # 3. Language Switch Requests
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

    # 4. Creators
    is_creator_query = (
        any(kw in text_lower for kw in CREATOR_KEYWORDS_TA) or
        any(kw in text_lower for kw in CREATOR_KEYWORDS_EN) or
        (("yaar" in text_lower or "who" in text_lower) and any(w in text_lower for w in ["create", "creator", "make", "made", "pann", "senj", "built"])) or
        any(w in text_lower for w in ["kishore", "mohandas", "latheeswaran", "latheeswarn"])
    )
    if is_creator_query:
        return CREATOR_TA if is_ta else CREATOR_EN

    # 5. Purpose
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


def main():
    print("=" * 65)
    print("       🤖 AURA - TEXT MODE WITH SPOKEN MALE VOICE")
    print("       🗣️  Languages  : Tamil (தமிழ்), Tanglish & English")
    print("       🎙️  Voice Tone : GENTLE MALE VOICE (Puck)")
    print("       Type in English or Tamil, AURA will speak every answer!")
    print("       Type 'exit' or 'bye' to quit")
    print("=" * 65)

    speaker = MaleVoiceSpeaker()
    # Speak welcome greeting in TAMIL with gentle MALE voice!
    speaker.speak(INTRO_TA, forced_lang="ta")

    while True:
        try:
            user_input = input("\n👤 [YOU]: ").strip()
            if not user_input:
                continue

            is_tamil = is_tamil_or_tanglish(user_input)
            lang = "ta" if is_tamil else "en"
            lang_label = "Tamil / Tanglish (தமிழ்)" if is_tamil else "English"
            print(f"📝 You said [{lang_label}]: {user_input}")

            cmd = check_commands(user_input, is_tamil)
            if cmd == "__EXIT__":
                farewell = "போய் வருகிறேன்! விரைவில் சந்திப்போம்!" if is_tamil else "Goodbye! See you soon!"
                speaker.speak(farewell, forced_lang=lang)
                break

            if cmd:
                speaker.speak(cmd, forced_lang=lang)
                continue

            print("🔍 Asking Google Gemini AI...")
            answer = ask_gemini(user_input, is_tamil)
            speaker.speak(answer, forced_lang=lang)

        except (EOFError, KeyboardInterrupt):
            print("\n👋 Goodbye!")
            break


if __name__ == "__main__":
    main()
