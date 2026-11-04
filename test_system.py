# -*- coding: utf-8 -*-
"""Quick test: verify microphone + MALE voice output + Gemini AI."""
import sys
import os
import wave
import tempfile
import sounddevice as sd
from google import genai
from google.genai import types
from dotenv import load_dotenv

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

print("=" * 60)
print("     🤖 AURA - GENTLE MALE VOICE SYSTEM CHECK")
print("=" * 60)

# 1. Microphone Check
print("\n[1] Checking Microphone...")
try:
    default_in = sd.query_devices(kind="input")
    print(f"   ✅ Microphone Found: {default_in['name']}")
except Exception as e:
    print(f"   ⚠️  No microphone detected ({e})")
    print("      Note: On Raspberry Pi, plug in any USB mic!")

# 2. Male Voice Test (Tamil & English)
print("\n[2] Testing MALE Voice Output (English & Tamil)...")
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

if api_key:
    c = genai.Client(api_key=api_key)
    from aura import MaleVoiceSpeaker
    speaker = MaleVoiceSpeaker()

    # Test Tamil Male Voice
    try:
        print("   🔊 Playing Tamil in GENTLE MALE voice...")
        speaker.speak("வணக்கம்! நான் ஆரா, உங்கள் மனித உருவ ரோபோ.", forced_lang="ta")
        print("   ✅ Tamil GENTLE MALE voice test SUCCESSFUL!")
    except Exception as e:
        print(f"   ❌ Tamil male voice error: {e}")

    # Test English Male Voice
    try:
        print("   🔊 Playing English in GENTLE MALE voice...")
        speaker.speak("Hello! I am AURA humanoid robot. My memory is Raspberry Pi 8GB RAM.", forced_lang="en")
        print("   ✅ English GENTLE MALE voice test SUCCESSFUL!")
    except Exception as e:
        print(f"   ❌ English male voice error: {e}")

    # 3. Test General AI Response
    print("\n[3] Testing Google Gemini AI Connection...")
    try:
        resp = c.models.generate_content(
            model="gemini-2.5-flash",
            contents="Say 'AURA gentle male voice is online' in 6 words"
        )
        print(f"   ✅ Gemini AI Responded: {resp.text.strip()}")
    except Exception as e:
        print(f"   ❌ Gemini AI Error: {e}")

    # 4. Test Prebuilt Responses (Creators, Purpose, and Tanglish support)
    print("\n[4] Testing Prebuilt Questions & Tanglish Support:")
    from aura_text_mode import check_commands, is_tamil_or_tanglish
    ta_creator = check_commands("உன்னை உருவாக்கியது யார்", True)
    en_creator = check_commands("who are create you", False)
    ta_purpose = check_commands("உன் நோக்கம் என்ன", True)
    en_purpose = check_commands("what the perpose you are here", False)
    tanglish_cmd = check_commands("tamil la sollu", False)
    tanglish_creator = check_commands("yaar unnai create pannanga", False)

    if "கிஷோர்" in ta_creator and "Kishore" in en_creator:
        print("   ✅ Creator Question (Mr. Kishore, Mr. Mohandas, Mr. Latheeswaran): OK!")
    else:
        print("   ❌ Creator Question Check Failed")

    if "கண்காணிப்பது" in ta_purpose and "monitor" in en_purpose:
        print("   ✅ Purpose Question (iGrid Lab embedded monitoring): OK!")
    else:
        print("   ❌ Purpose Question Check Failed")

    if tanglish_cmd and "தமிழில்" in tanglish_cmd:
        print("   ✅ Tanglish 'tamil la sollu' Command: OK!")
    else:
        print("   ❌ Tanglish Command Failed")

    if tanglish_creator and "கிஷோர்" in tanglish_creator:
        print("   ✅ Tanglish Creator 'yaar unnai create pannanga': OK!")
    else:
        print("   ❌ Tanglish Creator Failed")

    # 5. Test Dynamic Persistent Memory System
    print("\n[5] Testing Dynamic Persistent Memory:")
    from memory_manager import MemoryManager
    mem_mgr = MemoryManager()
    save_resp = mem_mgr.handle_memory_command("remember this: robot height is 3 feet", False)
    recall_resp = mem_mgr.handle_memory_command("what is in your memory", False)
    ta_save_resp = mem_mgr.handle_memory_command("idha nyabagam vachuko: prototype ready", True)

    if save_resp and "robot height is 3 feet" in recall_resp:
        print("   ✅ Dynamic Memory Save & Recall: OK!")
    else:
        print("   ❌ Dynamic Memory Test Failed")

    if ta_save_resp and "நினைவகத்தில்" in ta_save_resp:
        print("   ✅ Tamil Dynamic Memory Command: OK!")
    else:
        print("   ❌ Tamil Dynamic Memory Failed")

    # Verify no "திரு." (unmarried status check)
    if "திரு." not in ta_creator and "Mr." not in en_creator:
        print("   ✅ Creator Grammar (Unmarried status - no 'Thiru/Mr.'): OK!")
    else:
        print("   ⚠️ Creator still contains Thiru/Mr.")

else:
    print("   ❌ No GOOGLE_API_KEY found in .env")

print("\n" + "=" * 60)
print("  🚀 READY! Run your assistant with GENTLE MALE voice:")
print("     python aura.py")
print("=" * 60)
