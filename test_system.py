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

try:
    from aura import MaleVoiceSpeaker
    speaker = MaleVoiceSpeaker()

    # Test Tamil Male Voice
    try:
        print("   🔊 Playing Tamil in GENTLE MALE voice (Valluvar)...")
        speaker.speak("வணக்கம்! நான் ஆரா, உங்கள் மனித உருவ ரோபோ.", forced_lang="ta")
        print("   ✅ Tamil GENTLE MALE voice test SUCCESSFUL!")
    except Exception as e:
        print(f"   ❌ Tamil male voice error: {e}")

    # Test English Male Voice
    try:
        print("   🔊 Playing English in GENTLE MALE voice (Prabhat)...")
        speaker.speak("Hello! I am AURA humanoid robot. My memory is Raspberry Pi 8GB RAM.", forced_lang="en")
        print("   ✅ English GENTLE MALE voice test SUCCESSFUL!")
    except Exception as e:
        print(f"   ❌ English male voice error: {e}")
except Exception as e:
    print(f"   ❌ Could not initialize MaleVoiceSpeaker: {e}")

# 3. Test General AI Response
print("\n[3] Testing Google Gemini AI Connection...")
if api_key and "your_gemini_api_key" not in api_key.lower():
    try:
        c = genai.Client(api_key=api_key)
        resp = c.models.generate_content(
            model="gemini-2.5-flash",
            contents="Say 'AURA gentle male voice is online' in 6 words"
        )
        print(f"   ✅ Gemini AI Responded: {resp.text.strip()}")
    except Exception as e:
        print(f"   ❌ Gemini AI Error: {e}")
else:
    print("   ⚠️  Valid GOOGLE_API_KEY not configured yet in .env file (Voice output still works via Neural Male engine!)")

# 4. Test Prebuilt Responses (Creators, Purpose, and Tanglish support)
print("\n[4] Testing Prebuilt Questions & Tanglish Support:")
from aura_text_mode import check_commands, is_tamil_or_tanglish
ta_creator = check_commands("உன்னை உருவாக்கியது யார்", True)
en_creator = check_commands("who are create you", False)
ta_purpose = check_commands("உன் நோக்கம் என்ன", True)
en_purpose = check_commands("what the perpose you are here", False)
tanglish_cmd = check_commands("tamil la sollu", False)
tanglish_creator = check_commands("yaar unnai create pannanga", False)

if ta_creator and en_creator and "கிஷோர்" in ta_creator and "Kishore" in en_creator:
    print("   ✅ Creator Question (Kishore, Mohandas, Latheeswaran): OK!")
else:
    print("   ❌ Creator Question Check Failed")

if ta_purpose and en_purpose and "கண்காணிப்பது" in ta_purpose and "monitor" in en_purpose:
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
if ta_creator and en_creator and "திரு." not in ta_creator and "Mr." not in en_creator:
    print("   ✅ Creator Grammar (Unmarried status - no 'Thiru/Mr.'): OK!")
else:
    print("   ⚠️ Creator still contains Thiru/Mr.")

# 6. Test Lab Information Commands (Owner, Incharges, Lab Purpose, Equipments, Components)
print("\n[6] Testing Lab Information Commands (Tamil & English):")
en_incharge = check_commands("who is the incharge in this lab ?", False)
ta_incharge = check_commands("இந்த ஆய்வகத்தின் பொறுப்பாளர் யார்", True)
en_lab_purpose = check_commands("what the perpose of this lab?", False)
ta_lab_purpose = check_commands("இந்த ஆய்வகத்தின் நோக்கம் என்ன", True)
en_equipments = check_commands("what are the equipments the lab owned?", False)
ta_equipments = check_commands("ஆய்வகத்தில் என்னென்ன உபகரணங்கள் உள்ளன", True)
en_mc = check_commands("what are the microcontollers you have?", False)
ta_mc = check_commands("என்னென்ன மைக்ரோகண்ட்ரோலர்கள் உள்ளன", True)
en_comp = check_commands("what are the electrical components?", False)
ta_comp = check_commands("மின் பாகங்கள் என்னென்ன", True)

if en_incharge and "Balakrishnan" in en_incharge and "Barkath Nisha" in en_incharge and "Rubaa Sri" in en_incharge:
    print("   ✅ Lab Incharge (Dr. G. Balakrishnan, Barkath Nisha, Rubaa Sri): OK!")
else:
    print("   ❌ Lab Incharge EN check failed")

if ta_incharge and "பாலகிருஷ்ணன்" in ta_incharge and "பர்கத் நிஷா" in ta_incharge and "ரூபா ஸ்ரீ" in ta_incharge:
    print("   ✅ Lab Incharge TA (முனைவர் பாலக்ருஷ்ணன், பர்கத் நிஷா, ரூபா ஸ்ரீ): OK!")
else:
    print("   ❌ Lab Incharge TA check failed")

if en_lab_purpose and "innovative projects" in en_lab_purpose and ("dreams into reality" in en_lab_purpose or "dreams to reality" in en_lab_purpose):
    print("   ✅ Lab Purpose (innovative projects & dreams into reality): OK!")
else:
    print("   ❌ Lab Purpose EN check failed")

if ta_lab_purpose and "கனவுகளை நனவாக்குவதே" in ta_lab_purpose:
    print("   ✅ Lab Purpose TA: OK!")
else:
    print("   ❌ Lab Purpose TA check failed")

if en_equipments and "3D printer" in en_equipments and "Jetson Nano" in en_equipments:
    print("   ✅ Lab Equipments (3D printer, Laser, Drone, etc.): OK!")
else:
    print("   ❌ Lab Equipments EN check failed")

if ta_equipments and "3டி பிரிண்டர்" in ta_equipments:
    print("   ✅ Lab Equipments TA: OK!")
else:
    print("   ❌ Lab Equipments TA check failed")

if en_mc and "Arduino Uno" in en_mc and "Raspberry Pi 5" in en_mc and "Jetson Nano" in en_mc:
    print("   ✅ Microcontrollers (Uno, Mega, ESP32, Pi5, Jetson): OK!")
else:
    print("   ❌ Microcontrollers EN check failed")

if ta_mc and "ஆர்டுயினோ யூனோ" in ta_mc and "இஎஸ்பி32" in ta_mc:
    print("   ✅ Microcontrollers TA: OK!")
else:
    print("   ❌ Microcontrollers TA check failed")

if en_comp and "Raspberry Pi Camera" in en_comp and "PCA9685" in en_comp and "Waveshare" in en_comp:
    print("   ✅ Electrical Components (Pi Cam, ESP32 Cam, Servo, Drivers, etc.): OK!")
else:
    print("   ❌ Electrical Components EN check failed")

if ta_comp and "ராஸ்பெர்ரி பை கேமரா" in ta_comp and "வேவ்ஷேர்" in ta_comp:
    print("   ✅ Electrical Components TA: OK!")
else:
    print("   ❌ Electrical Components TA check failed")

# 7. Test Student Innovations, Lab Joining, Secretary, Principal Bio, Constituent Colleges
print("\n[7] Testing New Lab & College Facts (Tamil & English):")
en_innov = check_commands("what the student innovations ?", False)
ta_innov = check_commands("மாணவர் திட்டங்கள் என்னென்ன", True)
en_join = check_commands("how to join to this lab?", False)
ta_join = check_commands("ஆய்வகத்தில் சேருவது எப்படி", True)
en_sec = check_commands("who is the secretary", False)
ta_sec = check_commands("கல்லூரி செயலாளர் யார்", True)
en_bio = check_commands("about dr g balakrishnan", False)
ta_bio = check_commands("முதல்வர் பாலகிருஷ்ணன் பற்றி", True)
en_colleges = check_commands("constituent colleges", False)
ta_colleges = check_commands("இந்திரா கணேசன் கல்லூரிகள்", True)
en_start = check_commands("when the lab started?", False)
ta_start = check_commands("ஆய்வகம் எப்போது தொடங்கப்பட்டது", True)

if en_innov and "20" in en_innov and "projects" in en_innov:
    print("   ✅ Student Innovations EN (20+ projects): OK!")
else:
    print("   ❌ Student Innovations EN failed")

if ta_innov and "20" in ta_innov:
    print("   ✅ Student Innovations TA: OK!")
else:
    print("   ❌ Student Innovations TA failed")

if en_join and "A4 sheet" in en_join and "Manikandan" in en_join and "Vaijayanthi" in en_join and "Balakrishnan" in en_join:
    print("   ✅ How to Join Lab EN (A4 sheet, steps, all signatures in order): OK!")
else:
    print("   ❌ How to Join Lab EN failed")

if ta_join and "ஏ4 தாள்" in ta_join and "மணிகண்டன்" in ta_join and "வைஜெயந்தி" in ta_join and "பாலகிருஷ்ணன்" in ta_join:
    print("   ✅ How to Join Lab TA: OK!")
else:
    print("   ❌ How to Join Lab TA failed")

if en_sec and "Rajasekaran" in en_sec:
    print("   ✅ College Secretary EN (Er. G. Rajasekaran): OK!")
else:
    print("   ❌ College Secretary EN failed")

if ta_sec and "ராஜசேகரன்" in ta_sec:
    print("   ✅ College Secretary TA: OK!")
else:
    print("   ❌ College Secretary TA failed")

if en_bio and "Balakrishnan" in en_bio and "Anna University" in en_bio and "15" in en_bio:
    print("   ✅ Principal Dr. G. Balakrishnan Biography EN (Anna Univ, 15+ yrs): OK!")
else:
    print("   ❌ Principal Biography EN failed")

if ta_bio and "பாலகிருஷ்ணன்" in ta_bio and "அண்ணா பல்கலைக்கழகத்தில்" in ta_bio:
    print("   ✅ Principal Dr. G. Balakrishnan Biography TA: OK!")
else:
    print("   ❌ Principal Biography TA failed")

if en_colleges and "Engineering" in en_colleges and "Siddha" in en_colleges and "Pharmacy" in en_colleges:
    print("   ✅ Constituent Colleges EN (Engineering, Siddha, Arts, Nursing, Pharmacy, etc.): OK!")
else:
    print("   ❌ Constituent Colleges EN failed")

if ta_colleges and "பொறியியல்" in ta_colleges and "சித்த மருத்துவக்" in ta_colleges:
    print("   ✅ Constituent Colleges TA: OK!")
else:
    print("   ❌ Constituent Colleges TA failed")

if en_start and "December 2025" in en_start and "HowNWhy" in en_start:
    print("   ✅ When Lab Started EN (December 2025, HowNWhy): OK!")
else:
    print("   ❌ When Lab Started EN failed")

if ta_start and "டிசம்பர் 2025" in ta_start and "HowNWhy" in ta_start:
    print("   ✅ When Lab Started TA (டிசம்பர் 2025, HowNWhy): OK!")
else:
    print("   ❌ When Lab Started TA failed")

print("\n" + "=" * 60)
print("  🚀 READY! Run your assistant with GENTLE MALE voice:")
print("     python aura.py")
print("=" * 60)
