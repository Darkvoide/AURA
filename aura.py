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
FALLBACK_MODEL = "gemini-2.0-flash"
TTS_MODELS = [
    "gemini-2.0-flash",
    "gemini-2.5-flash"
]
MALE_VOICE_NAME = "Puck"  # Gemini Neural Male Voice ("Puck", "Charon", "Fenrir")
EDGE_VOICE_TAMIL_MALE = "ta-IN-ValluvarNeural"   # Authentic Neural Tamil Male Voice
EDGE_VOICE_ENGLISH_MALE = "en-IN-PrabhatNeural"  # Authentic Neural English Male Voice

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

# 1. Lab Incharges & Ownership
LAB_INCHARGE_EN = (
    "This lab is owned by the college, and the leader and owner is Dr. G. Balakrishnan. "
    "We have two incharges: Miss Barkath Nisha and Miss Rubaa Sri."
)

LAB_INCHARGE_TA = (
    "இந்த ஆய்வகம் கல்லூரிக்கு சொந்தமானது, இதன் உரிமையாளர் மற்றும் தலைவர் முனைவர் ஜி. பாலகிருஷ்ணன் அவர்கள் ஆவார். "
    "இங்கு இரண்டு பொறுப்பாளர்கள் உள்ளனர், அவர்கள் மிஸ் பர்கத் நிஷா மற்றும் மிஸ் ரூபா ஸ்ரீ ஆவார்கள்."
)

# 2. Purpose of this Lab
LAB_PURPOSE_EN = (
    "The purpose of this lab is for students to do innovative projects and turn their suppressed dreams into reality!"
)

LAB_PURPOSE_TA = (
    "இந்த ஆய்வகத்தின் முக்கிய நோக்கம், மாணவர்கள் புதுமையான திட்டங்களை உருவாக்கி, தங்களின் அடக்கப்பட்ட கனவுகளை நனவாக்குவதே ஆகும்!"
)

# 3. Lab Equipments
LAB_EQUIPMENTS_EN = (
    "Yeah, that's a great question! The lab owns several high-tech equipments: "
    "3D printer, Laser machine, VR and AR, professional toolkits, Drone, and microcontrollers ranging from Arduino Uno to Jetson Nano."
)

LAB_EQUIPMENTS_TA = (
    "மிகச் சிறந்த கேள்வி! இந்த ஆய்வகத்தில் பல உயர்தர உபகரணங்கள் உள்ளன: "
    "3டி பிரிண்டர், லேசர் மெஷின், விஆர் மற்றும் ஏஆர் (VR & AR), தொழில்முறை டூல்கிட்ஸ், ட்ரோன் மற்றும் ஆர்டுயினோ யூனோ முதல் ஜெட்சன் நானோ வரையிலான மைக்ரோகண்ட்ரோலர்கள் உள்ளன."
)

# 4. Microcontrollers
LAB_MICROCONTROLLERS_EN = (
    "The microcontrollers we have are: Arduino Uno, Arduino Mega, ESP32, Raspberry Pi 5, and Jetson Nano."
)

LAB_MICROCONTROLLERS_TA = (
    "எங்களிடம் உள்ள மைக்ரோகண்ட்ரோலர்கள்: "
    "ஆர்டுயினோ யூனோ (Arduino Uno), ஆர்டுயினோ மெகா (Arduino Mega), இஎஸ்பி32 (ESP32), ராஸ்பெர்ரி பை 5 (Raspberry Pi 5) மற்றும் ஜெட்சன் நானோ (Jetson Nano) ஆகியவை ஆகும்."
)

# 5. Electrical & Electronic Components
LAB_COMPONENTS_EN = (
    "The electrical and electronic components available in our lab are: "
    "Raspberry Pi Camera, ESP32 Camera, Servo motors, IMU sensors, PCA9685 servo motor driver, "
    "L298N DC motor driver, IR sensor, Buck converter, 12V battery, 3.3V battery, data cables, and Waveshare display."
)

LAB_COMPONENTS_TA = (
    "இங்குள்ள மின் மற்றும் மின்னணு பாகங்கள்: "
    "ராஸ்பெர்ரி பை கேமரா, இஎஸ்பி32 கேமரா, சர்வோ மோட்டார்கள், ஐஎம்யு (IMU) சென்சார்கள், PCA9685 சர்வோ மோட்டார் டிரைவர், "
    "L298N டிசி மோட்டார் டிரைவர், ஐஆர் (IR) சென்சார்கள், பக் கன்வெர்ட்டர், 12 வோல்ட் பேட்டரி, 3.3 வோல்ட் பேட்டரி, டேட்டா கேபிள்கள் மற்றும் வேவ்ஷேர் டிஸ்ப்ளே (Waveshare display) ஆகியவை ஆகும்."
)

# 6. Student Innovations
STUDENT_INNOVATIONS_EN = (
    "In this lab, our students have made over 20 innovative projects! "
    "Would you like to know something specific about these projects?"
)

STUDENT_INNOVATIONS_TA = (
    "இந்த ஆய்வகத்தில் மாணவர்கள் 20-க்கும் மேற்பட்ட புதுமையான திட்டங்களை உருவாக்கியுள்ளனர்! "
    "இந்த திட்டங்களைப் பற்றி மேலும் தெரிந்து கொள்ள விரும்புகிறீர்களா?"
)

# 7. How to Join the Lab
JOIN_LAB_EN = (
    "Yes, I will help you! Follow these steps to join the iGrid Lab: "
    "First, take an A4 sheet and pen. Put your details in From, and college details in To, "
    "with the subject: 'Request to join the iGrid Lab'. "
    "You can write the body yourself or use ChatGPT for assistance. "
    "Sign the letter, and then get the following signatures in order: "
    "your department mentor, your Head of Department, iGrid Lab mentor Mr. Manikandan ECE HOD, "
    "Vice Principal Dr. Vaijayanthi, and finally our college leader and Principal Dr. G. Balakrishnan!"
)

JOIN_LAB_TA = (
    "நிச்சயமாக, நான் உங்களுக்கு உதவுகிறேன்! ஐ-கிரிட் ஆய்வகத்தில் சேர இந்த வழிமுறைகளைப் பின்பற்றுங்கள்: "
    "முதலில் ஒரு ஏ4 தாள் மற்றும் பேனா எடுத்துக் கொள்ளுங்கள். உங்கள் விவரங்களை 'From' பகுதியிலும், கல்லூரி விவரங்களை 'To' பகுதியிலும் எழுதுங்கள். "
    "பொருள்: 'ஐ-கிரிட் லேபில் சேர விண்ணப்பம்' என்று குறிப்பிடுங்கள். கடிதத்தின் உள்ளடக்கத்தை நீங்களே எழுதலாம் அல்லது சாட்-ஜிபிடி உதவியுடன் எழுதலாம். "
    "பிறகு உங்கள் கையெழுத்திட்டு, வரிசையாக உங்கள் துறை வழிகாட்டி, துறைத் தலைவர், ஐ-கிரிட் வழிகாட்டி திரு. மணிகண்டன், "
    "துணை முதல்வர் முனைவர் வைஜெயந்தி, மற்றும் இறுதியாக நமது கல்லூரியின் தலைவர் மற்றும் முதல்வர் முனைவர் ஜி. பாலகிருஷ்ணன் ஆகியோரிடம் கையெழுத்து பெற வேண்டும்!"
)

# 8. College Leadership & Secretary
COLLEGE_LEADERSHIP_EN = (
    "Indra Ganesan Institutions is guided by esteemed leadership: "
    "our Chairman Shri T. Ganesan, our Secretary Engineer G. Rajasekaran sir, "
    "and our Principal and Director Dr. G. Balakrishnan sir."
)

COLLEGE_LEADERSHIP_TA = (
    "இந்திரா கணேசன் கல்வி நிறுவனங்களின் நிர்வாகத் தலைவர்கள்: "
    "நமது சேர்மன் திரு. டி. கணேசன் அவர்கள், நமது கல்லூரியின் செயலாளர் பொறியாளர் ஜி. ராஜசேகரன் அவர்கள், "
    "மற்றும் முதல்வர் மற்றும் இயக்குனர் முனைவர் ஜி. பாலகிருஷ்ணன் அவர்கள் ஆவார்கள்."
)

# 9. Biography of Dr. G. Balakrishnan
PRINCIPAL_BIO_EN = (
    "Dr. G. Balakrishnan serves as the Principal and Director of Indra Ganesan College of Engineering and overall Director of Indra Ganesan Institutions in Tiruchirappalli. "
    "He holds Ph.D., M.E., and B.E. degrees with First Class and Distinction from Anna University, Chennai. "
    "He possesses over 15 years of academic and administrative experience, with more than 50 research publications and having guided over 100 students. "
    "His office is on the first floor of the Administrative Block, reachable at principal@igceng.com."
)

PRINCIPAL_BIO_TA = (
    "முனைவர் ஜி. பாலகிருஷ்ணன் அவர்கள் திருச்சி இந்திரா கணேசன் பொறியியல் கல்லூரியின் முதல்வர் மற்றும் இயக்குநராகவும், இந்திரா கணேசன் கல்வி நிறுவனங்களின் ஒட்டுமொத்த இயக்குநராகவும் பணியாற்றுகிறார். "
    "இவர் சென்னை அண்ணா பல்கலைக்கழகத்தில் பி.இ., எம்.இ., மற்றும் பிஹெச்.டி (Ph.D) பட்டங்களை முதல் வகுப்பில் தேர்ச்சி பெற்றுள்ளார். "
    "15 ஆண்டுகளுக்கும் மேலான அனுபவமும், 50-க்கும் மேற்பட்ட ஆய்வுக் கட்டுரைகளும், 100-க்கும் மேற்பட்ட மாணவர்களுக்கு வழிகாட்டிய பெருமையும் கொண்டவர். "
    "இவரது அலுவலகம் நிர்வாகக் கட்டிடத்தின் முதல் தளத்தில் அமைந்துள்ளது."
)

# 10. Constituent Colleges & Principals
CONSTITUENT_COLLEGES_EN = (
    "Indra Ganesan Institutions comprises several constituent colleges: "
    "Engineering led by Dr. G. Balakrishnan, Siddha Medical College led by Dr. A. Ganesan, "
    "Arts and Science led by Dr. M. Kannan, Nursing led by Dr. S. Sarojini, "
    "Pharmacy led by Dr. M. Jesu Pillai, Physiotherapy led by Dr. N. N. Bobby, "
    "Naturopathy and Yogic Sciences led by Dr. P. Vivekhanandha, and College of Education led by Dr. P. Rajendran."
)

CONSTITUENT_COLLEGES_TA = (
    "இந்திரா கணேசன் கல்வி நிறுவனங்களின் கீழ் இயங்கும் கல்லூரிகள் மற்றும் அவற்றின் முதல்வர்கள்: "
    "பொறியியல் கல்லூரிக்கு முனைவர் ஜி. பாலகிருஷ்ணன், சித்த மருத்துவக் கல்லூரிக்கு முனைவர் ஏ. கணேசன், "
    "கலை மற்றும் அறிவியல் கல்லூரிக்கு முனைவர் எம். கண்ணன், நர்சிங் கல்லூரிக்கு முனைவர் எஸ். சரோஜினி, "
    "பார்மசி கல்லூரிக்கு முனைவர் எம். ஜேசு பிள்ளை, பிசியோதெரபி கல்லூரிக்கு முனைவர் என். என். பாபி, "
    "இயற்கை மருத்துவம் மற்றும் யோகா கல்லூரிக்கு முனைவர் பி. விவேகானந்தா, மற்றும் கல்வியியல் கல்லூரிக்கு முனைவர் பி. ராஜேந்திரன் ஆகியோர் முதல்வர்களாக உள்ளனர்."
)

# 11. When the Lab Started / Inauguration
LAB_START_EN = (
    "The iGrid Lab — Intelligent Generative Robotics, IoT and Deep-Tech Lab — "
    "is a multidisciplinary deep-technology and innovation center at Indra Ganesan College of Engineering in Tiruchirappalli, Tamil Nadu. "
    "It was inaugurated in December 2025 in partnership with HowNWhy, connecting students, faculty, and researchers to build and test real-world engineering solutions!"
)

LAB_START_TA = (
    "ஐ-கிரிட் ஆய்வகம் (இன்டெலிஜென்ட் ஜெனரேட்டிவ் ரோபோட்டிக்ஸ், ஐஓடி மற்றும் டீப்-டெக் லேப்) "
    "திருச்சி இந்திரா கணேசன் பொறியியல் கல்லூரியில் 'ஹௌ அண்ட் ஒய்' (HowNWhy) நிறுவனத்துடன் இணைந்து டிசம்பர் 2025-ல் தொடங்கப்பட்டது. "
    "இது மாணவர்கள், பேராசிரியர்கள் மற்றும் ஆராய்ச்சியாளர்களை ஒன்றிணைத்து நிஜ உலகப் பொறியியல் தீர்வுகளை உருவாக்க உதவும் ஒரு பல்துறை தொழில்நுட்ப மையமாகும்!"
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

LAB_INCHARGE_KEYWORDS_EN = [
    "who is the incharge", "who is incharge", "incharge in this lab", "incharge of this lab",
    "in charge", "in-charge", "who owns this lab", "who own this lab", "lab owner", "owner of this lab",
    "barkath nisha", "rubaa sri", "barkath", "rubaa"
]
LAB_INCHARGE_KEYWORDS_TA = [
    "பொறுப்பாளர்", "ஆய்வக பொறுப்பாளர்", "இன்சார்ஜ்", "யார் பொறுப்பாளர்", "உரிமையாளர்",
    "பர்கத் நிஷா", "ரூபா ஸ்ரீ", "பர்கத்", "ரூபா"
]

LAB_PURPOSE_KEYWORDS_EN = [
    "purpose of this lab", "perpose of this lab", "purpose of the lab", "perpose of the lab",
    "why this lab", "what the perpose of this lab", "what is the purpose of this lab",
    "lab purpose", "purpose of lab"
]
LAB_PURPOSE_KEYWORDS_TA = [
    "ஆய்வகத்தின் நோக்கம்", "லேப் நோக்கம்", "இந்த லேப் எதற்கு", "ஆய்வகம் எதற்கு",
    "லேப் எதற்கு", "லேப்பின் நோக்கம்"
]

LAB_EQUIPMENTS_KEYWORDS_EN = [
    "what are the equipments", "equipments the lab owned", "equipments owned",
    "what equipments", "equipment in this lab", "equipments in this lab", "lab equipments",
    "hifi equipments", "hi-fi equipments", "equipment list", "tools and equipment"
]
LAB_EQUIPMENTS_KEYWORDS_TA = [
    "உபகரணங்கள்", "கருவிகள்", "லேப் உபகரணங்கள்", "ஆய்வக உபகரணங்கள்", "என்னென்ன உபகரணங்கள்"
]

LAB_MICROCONTROLLERS_KEYWORDS_EN = [
    "what are the microcontollers", "what are the microcontrollers", "microcontollers you have",
    "microcontrollers you have", "microcontroller", "microcontrollers", "micro controller",
    "micro controllers", "which microcontrollers", "controllers you have"
]
LAB_MICROCONTROLLERS_KEYWORDS_TA = [
    "மைக்ரோகண்ட்ரோலர்", "மைக்ரோகண்ட்ரோலர்கள்", "கண்ட்ரோலர்கள்"
]

LAB_COMPONENTS_KEYWORDS_EN = [
    "what are the electrical components", "electrical components", "electronic components",
    "what components", "electrical parts", "electronic parts", "sensors and motors",
    "components you have", "components in this lab", "components in the lab"
]
LAB_COMPONENTS_KEYWORDS_TA = [
    "மின் பாகங்கள்", "மின்னணு பாகங்கள்", "பாகங்கள் என்னென்ன", "எலக்ட்ரிக்கல் பாகங்கள்"
]

INNOVATIONS_KEYWORDS_EN = [
    "student innovations", "student innovation", "innovations", "student projects",
    "projects done", "projects in this lab", "what projects", "20 projects", "20+ projects",
    "what the student innovations"
]
INNOVATIONS_KEYWORDS_TA = [
    "மாணவர் திட்டங்கள்", "கண்டுபிடிப்புகள்", "புதிய திட்டங்கள்", "மாணவர்கள் என்ன செய்தார்கள்",
    "திட்டங்கள் என்னென்ன"
]

JOIN_LAB_KEYWORDS_EN = [
    "how to join to this lab", "how to join this lab", "how to join", "join this lab",
    "join the lab", "join igrid", "join igrid lab", "joining process", "admission to lab",
    "steps to join", "how can i join", "joining steps"
]
JOIN_LAB_KEYWORDS_TA = [
    "சேருவது எப்படி", "ஆய்வகத்தில் சேர", "லேபில் சேர", "எப்படி சேருவது",
    "சேர என்ன செய்ய வேண்டும்"
]

SECRETARY_KEYWORDS_EN = [
    "secretary", "college secretary", "rajasekaran", "rajasagaran", "er. g. rajasekaran",
    "er g rajasekaran", "engineer rajasekaran", "who is the secretary", "who is secretary"
]
SECRETARY_KEYWORDS_TA = [
    "செயலாளர்", "கல்லூரி செயலாளர்", "ராஜசேகரன்"
]

PRINCIPAL_BIO_KEYWORDS_EN = [
    "about balakrishnan", "about dr g balakrishnan", "biography of balakrishnan",
    "auto biography about balakrishnan", "autobiography about balakrishnan",
    "principal details", "who is balakrishnan", "who is dr g balakrishnan",
    "who is principal", "college principal", "principal of college", "director", "balakrishnan sir"
]
PRINCIPAL_BIO_KEYWORDS_TA = [
    "பாலகிருஷ்ணன் பற்றி", "முதல்வர் பற்றி", "முதல்வர் யார்", "பிரின்சிபால்", "பாலகிருஷ்ணன் யார்",
    "பாலகிருஷ்ணன்"
]

CONSTITUENT_COLLEGES_KEYWORDS_EN = [
    "constituent colleges", "colleges in indra ganesan", "all colleges", "other colleges",
    "principals of indra ganesan", "medical college", "pharmacy college", "nursing college",
    "physiotherapy college", "arts and science", "indra ganesan institutions", "college list"
]
CONSTITUENT_COLLEGES_KEYWORDS_TA = [
    "கல்லூரிகள்", "மற்ற கல்லூரிகள்", "இந்திரா கணேசன் கல்லூரிகள்", "முதல்வர்கள் பட்டியல்"
]

LAB_START_KEYWORDS_EN = [
    "when the lab started", "when was the lab started", "when did the lab start",
    "when was this lab started", "when did this lab start", "when lab started",
    "when was igrid started", "when was igrid lab started", "when igrid started",
    "lab started", "lab start date", "inauguration of lab", "inauguration date",
    "when was the lab inaugurated", "when was this lab inaugurated",
    "inaugurated in", "hownwhy", "december 2025", "lab foundation", "lab established",
    "when was it established", "when was the lab established"
]
LAB_START_KEYWORDS_TA = [
    "ஆய்வகம் எப்போது தொடங்கப்பட்டது", "லேப் எப்போது ஆரம்பித்தது", "எப்போது ஆரம்பித்தது",
    "எப்போது தொடங்கப்பட்டது", "எப்ப தொடங்கினாங்க", "ஆரம்பித்த நாள்", "தொடங்கப்பட்ட நாள்",
    "ஐகிரிட் எப்போது", "டிசம்பர் 2025", "எப்ப ஆரம்பிச்சாங்க"
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
    """Handles text-to-speech using authentic MALE voices for Tamil and English.
    1. Edge-TTS Neural Male Voice (Valluvar for Tamil, Prabhat for English).
    2. Google Gemini Neural Male Voice (Puck/Charon).
    3. Offline Windows SAPI5 Male Voice (David).
    """

    def __init__(self):
        # Configure offline male voice as backup
        try:
            self.offline_engine = pyttsx3.init()
            self.offline_engine.setProperty("rate", 145)  # Gentle, calm pace
            self.offline_engine.setProperty("volume", 0.9)
            voices = self.offline_engine.getProperty("voices")
            male_found = False
            for v in voices:
                v_name = v.name.lower()
                if any(m in v_name for m in ["david", "mark", "george", "male", "prabhat", "ravi", "valluvar"]):
                    self.offline_engine.setProperty("voice", v.id)
                    male_found = True
                    break
            if not male_found and voices:
                for v in voices:
                    if "zira" not in v.name.lower() and "female" not in getattr(v, "gender", "").lower():
                        self.offline_engine.setProperty("voice", v.id)
                        break
        except Exception:
            self.offline_engine = None

    def _play_wav_or_mp3(self, filepath: str) -> bool:
        """Play a WAV or MP3 audio file with 8.3 path resolution and robust fallbacks."""
        if not filepath or not os.path.exists(filepath):
            return False

        if sys.platform == "win32":
            alias = f"aura_{int(time.time() * 1000)}"
            # 1. Use 8.3 Short Path to prevent path-with-spaces errors in Windows MCI
            short_path = filepath
            try:
                buf = ctypes.create_unicode_buffer(512)
                if ctypes.windll.kernel32.GetShortPathNameW(filepath, buf, 512):
                    short_path = buf.value
            except Exception:
                pass

            # 2. Open and play with MCI
            try:
                open_cmd = f'open {short_path} type mpegvideo alias {alias}' if filepath.endswith('.mp3') else f'open {short_path} alias {alias}'
                r_open = ctypes.windll.winmm.mciSendStringW(open_cmd, None, 0, None)
                if r_open == 0:
                    r_play = ctypes.windll.winmm.mciSendStringW(f'play {alias} wait', None, 0, None)
                    ctypes.windll.winmm.mciSendStringW(f'close {alias}', None, 0, None)
                    if r_play == 0:
                        return True
                else:
                    ctypes.windll.winmm.mciSendStringW(f'close {alias}', None, 0, None)
            except Exception:
                pass

            # 3. Fallback for Windows: winsound if WAV
            try:
                import winsound
                if filepath.endswith(".wav"):
                    winsound.PlaySound(filepath, winsound.SND_FILENAME)
                    return True
            except Exception:
                pass

            # 4. Fallback for Windows: PowerShell Audio Player
            try:
                esc_path = filepath.replace("'", "''")
                cmd = f'powershell -c "(New-Object Media.MediaPlayer).Open(\'{esc_path}\'); (New-Object Media.MediaPlayer).Play(); Start-Sleep -Milliseconds 500"'
                ret = os.system(cmd)
                if ret == 0:
                    return True
            except Exception:
                pass

            return False
        else:
            # Linux / Raspberry Pi
            ret = os.system(f'mpg123 -q "{filepath}" 2>/dev/null')
            if ret != 0:
                ret = os.system(f'aplay -q "{filepath}" 2>/dev/null')
            if ret != 0:
                os.system(f'ffplay -nodisp -autoexit -loglevel quiet "{filepath}" 2>/dev/null')
            return True

    def _speak_edge_male(self, text: str, is_tamil: bool) -> bool:
        """Speak in authentic neural MALE voice (Tamil: Valluvar, English: Prabhat)."""
        try:
            import asyncio
            import edge_tts

            voice = EDGE_VOICE_TAMIL_MALE if is_tamil else EDGE_VOICE_ENGLISH_MALE
            temp_mp3 = os.path.join(tempfile.gettempdir(), f"aura_male_{int(time.time() * 1000)}.mp3")

            async def _run():
                comm = edge_tts.Communicate(text=text, voice=voice)
                await comm.save(temp_mp3)

            asyncio.run(_run())

            if os.path.exists(temp_mp3) and os.path.getsize(temp_mp3) > 0:
                played = self._play_wav_or_mp3(temp_mp3)
                try:
                    os.remove(temp_mp3)
                except Exception:
                    pass
                return played
        except Exception:
            pass
        return False

    def speak(self, text: str, forced_lang: str = None):
        """Print and speak the answer aloud in a gentle MALE voice."""
        if not text or not text.strip():
            return

        clean_text = text.strip()
        print(f"\n🤖 [AURA (Male Voice)]: {clean_text}\n")

        is_tamil = is_tamil_text(clean_text) or forced_lang == "ta"

        # 1. Primary: Authentic Edge-TTS Neural Male Voice (Valluvar for Tamil, Prabhat for English)
        if self._speak_edge_male(clean_text, is_tamil):
            return

        # 2. Secondary: Google Gemini Neural Male Voice (Puck/Charon)
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
        Allows typing a text message OR pressing ENTER to speak via microphone.
        AURA speaks aloud in gentle male voice for BOTH!
        """
        has_mic = self._check_mic(verbose=False)

        if not has_mic:
            try:
                text = input("\n👤 [YOU (Type text message)]: ").strip()
                if not text:
                    return ("", "")
                lang = "ta" if is_tamil_or_tanglish(text) else "en"
                return (text, lang)
            except (EOFError, KeyboardInterrupt):
                return ("exit", "en")

        # When mic is available, allow typing OR pressing Enter to speak
        try:
            user_input = input("\n💬 [Type text message, or press ENTER to speak into Mic]: ").strip()
            if user_input:
                lang = "ta" if is_tamil_or_tanglish(user_input) else "en"
                return (user_input, lang)
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
        "   - Lab Ownership & Leadership: Owned by the college; the owner and leader is Dr. G. Balakrishnan.\n"
        "   - Lab Incharges: Miss Barkath Nisha and Miss Rubaa Sri.\n"
        "   - Purpose of Lab: For students to do innovative projects and turn their suppressed dreams into reality.\n"
        "   - Lab Establishment & Inauguration: The IGRID Lab (Intelligent Generative Robotics, IoT & Deep-Tech Lab) is a multidisciplinary deep-technology center at Indra Ganesan College of Engineering, Tiruchirappalli, inaugurated in December 2025 in partnership with HowNWhy to build and test real-world engineering solutions.\n"
        "   - Student Innovations: Students have created 20+ innovative projects in this lab.\n"
        "   - How to Join iGrid Lab: 1. Take A4 sheet & pen, write From (student) & To (college) with subject 'Request to join the iGrid Lab'. 2. Write body (can use ChatGPT for help). 3. Sign and get signatures in order: Department Mentor, HOD, iGrid Mentor Mr. Manikandan (ECE HOD), Vice Principal Dr. Vaijayanthi, and Principal & Director Dr. G. Balakrishnan.\n"
        "   - College Leadership: Chairman Shri T. Ganesan, Secretary Er. G. Rajasekaran, and Principal & Director Dr. G. Balakrishnan.\n"
        "   - Dr. G. Balakrishnan Biography: Principal & Director of IGCE and overall Director of Indra Ganesan Institutions. Ph.D., M.E., B.E. (Distinction) Anna University; 15+ years experience, 50+ publications, 100+ students guided. Office: Admin Block 1st floor (principal@igceng.com, +91-431-2901621).\n"
        "   - Constituent Colleges & Principals: Engineering (Dr. G. Balakrishnan), Siddha Medical (Dr. A. Ganesan), Arts & Science (Dr. M. Kannan), Nursing (Dr. S. Sarojini / Dr. P. Kirupa), Pharmacy (Dr. M. Jesu Pillai), Physiotherapy (Dr. N. N. Bobby), Naturopathy & Yoga (Dr. P. Vivekhanandha), Education (Dr. P. Rajendran / Dr. Manimaran Govindaswamy).\n"
        "   - Lab Equipments: 3D printer, Laser machine, VR and AR headsets, professional toolkits, Drone, and microcontrollers from Arduino Uno to Jetson Nano.\n"
        "   - Microcontrollers: Arduino Uno, Arduino Mega, ESP32, Raspberry Pi 5, Jetson Nano.\n"
        "   - Electrical & Electronic Components: Raspberry Pi Cam, ESP32 Cam, Servo motors, IMU sensors, PCA9685 servo motor driver, L298N DC motor driver, IR sensor, Buck converter, 12V battery, 3.3V battery, data cables, Waveshare display.\n"
        "   - Robot Purpose: Stationed at iGrid Lab to monitor embedded systems and components, create robotics awareness, and monitor/welcome visitors.\n"
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

    # 5. Lab Incharges
    is_incharge_query = (
        any(kw in text_lower for kw in LAB_INCHARGE_KEYWORDS_TA) or
        any(kw in text_lower for kw in LAB_INCHARGE_KEYWORDS_EN) or
        "incharge" in text_lower or
        "in-charge" in text_lower or
        "in charge" in text_lower or
        "barkath" in text_lower or
        "rubaa" in text_lower or
        (("who" in text_lower or "yaar" in text_lower) and "incharge" in text_lower)
    )
    if is_incharge_query:
        return LAB_INCHARGE_TA if is_ta else LAB_INCHARGE_EN

    # 6. College Secretary & Management
    is_sec_query = (
        any(kw in text_lower for kw in SECRETARY_KEYWORDS_TA) or
        any(kw in text_lower for kw in SECRETARY_KEYWORDS_EN) or
        "rajasekaran" in text_lower or "rajasagaran" in text_lower or
        ("secretary" in text_lower and any(w in text_lower for w in ["college", "who", "sir"]))
    )
    if is_sec_query:
        return COLLEGE_LEADERSHIP_TA if is_ta else COLLEGE_LEADERSHIP_EN

    # 7. Principal & Director Dr. G. Balakrishnan (Biography & Details)
    is_principal_bio_query = (
        any(kw in text_lower for kw in PRINCIPAL_BIO_KEYWORDS_TA) or
        any(kw in text_lower for kw in PRINCIPAL_BIO_KEYWORDS_EN) or
        ("balakrishnan" in text_lower and any(w in text_lower for w in ["who", "about", "bio", "autobiography", "details", "sir", "dr"])) or
        ("principal" in text_lower and any(w in text_lower for w in ["who", "about", "details", "college", "director"]))
    )
    if is_principal_bio_query:
        return PRINCIPAL_BIO_TA if is_ta else PRINCIPAL_BIO_EN

    # 8. Constituent Colleges of Indra Ganesan Institutions
    is_colleges_query = (
        any(kw in text_lower for kw in CONSTITUENT_COLLEGES_KEYWORDS_TA) or
        any(kw in text_lower for kw in CONSTITUENT_COLLEGES_KEYWORDS_EN) or
        ("constituent" in text_lower and "college" in text_lower) or
        ("colleges" in text_lower and "indra ganesan" in text_lower)
    )
    if is_colleges_query:
        return CONSTITUENT_COLLEGES_TA if is_ta else CONSTITUENT_COLLEGES_EN

    # 9. Student Innovations
    is_innovations_query = (
        any(kw in text_lower for kw in INNOVATIONS_KEYWORDS_TA) or
        any(kw in text_lower for kw in INNOVATIONS_KEYWORDS_EN) or
        ("innovation" in text_lower or "innovations" in text_lower or ("student" in text_lower and "project" in text_lower))
    )
    if is_innovations_query:
        return STUDENT_INNOVATIONS_TA if is_ta else STUDENT_INNOVATIONS_EN

    # 10. How to Join the Lab
    is_join_query = (
        any(kw in text_lower for kw in JOIN_LAB_KEYWORDS_TA) or
        any(kw in text_lower for kw in JOIN_LAB_KEYWORDS_EN) or
        ("join" in text_lower and any(w in text_lower for w in ["lab", "igrid", "here", "how", "steps"]))
    )
    if is_join_query:
        return JOIN_LAB_TA if is_ta else JOIN_LAB_EN

    # 11. When the Lab Started / Inauguration
    is_lab_start_query = (
        any(kw in text_lower for kw in LAB_START_KEYWORDS_TA) or
        any(kw in text_lower for kw in LAB_START_KEYWORDS_EN) or
        (("lab" in text_lower or "igrid" in text_lower) and any(w in text_lower for w in ["started", "start", "inaugurat", "founded", "established", "thodang", "aaramb"])) or
        ("when" in text_lower and any(w in text_lower for w in ["lab", "igrid"]) and any(w in text_lower for w in ["start", "open", "inaugurat"]))
    )
    if is_lab_start_query:
        return LAB_START_TA if is_ta else LAB_START_EN

    # 12. Lab Purpose (What is the purpose of this lab?)
    is_lab_purpose_query = (
        any(kw in text_lower for kw in LAB_PURPOSE_KEYWORDS_TA) or
        any(kw in text_lower for kw in LAB_PURPOSE_KEYWORDS_EN) or
        (("lab" in text_lower or "ஆய்வக" in text_lower) and ("purpose" in text_lower or "perpose" in text_lower or "நோக்கம்" in text_lower or "edhukku" in text_lower or "why" in text_lower))
    )
    if is_lab_purpose_query:
        return LAB_PURPOSE_TA if is_ta else LAB_PURPOSE_EN

    # 12. Robot Purpose (iGrid Lab / why are you here)
    is_purpose_query = (
        any(kw in text_lower for kw in PURPOSE_KEYWORDS_TA) or
        any(kw in text_lower for kw in PURPOSE_KEYWORDS_EN) or
        any(w in text_lower for w in ["purpose", "perpose", "role", "igrid"]) or
        (("edhukku" in text_lower or "why" in text_lower or "enna vela" in text_lower or "enna panra" in text_lower) and any(w in text_lower for w in ["inga", "here", "lab"]))
    )
    if is_purpose_query:
        return PURPOSE_TA if is_ta else PURPOSE_EN

    # 13. Microcontrollers in Lab
    is_mc_query = (
        any(kw in text_lower for kw in LAB_MICROCONTROLLERS_KEYWORDS_TA) or
        any(kw in text_lower for kw in LAB_MICROCONTROLLERS_KEYWORDS_EN) or
        "microcontroller" in text_lower or
        "microcontoller" in text_lower or
        "micro controller" in text_lower or
        "மைக்ரோகண்ட்ரோலர்" in text_lower
    )
    if is_mc_query:
        return LAB_MICROCONTROLLERS_TA if is_ta else LAB_MICROCONTROLLERS_EN

    # 14. Electrical & Electronic Components
    is_comp_query = (
        any(kw in text_lower for kw in LAB_COMPONENTS_KEYWORDS_TA) or
        any(kw in text_lower for kw in LAB_COMPONENTS_KEYWORDS_EN) or
        ("electrical" in text_lower and ("component" in text_lower or "part" in text_lower or "sensor" in text_lower)) or
        ("electronic" in text_lower and ("component" in text_lower or "part" in text_lower or "sensor" in text_lower)) or
        ("components" in text_lower and any(w in text_lower for w in ["lab", "you have", "available", "electrical", "electronic", "here", "enna"]))
    )
    if is_comp_query:
        return LAB_COMPONENTS_TA if is_ta else LAB_COMPONENTS_EN

    # 15. Lab Equipments
    is_equip_query = (
        any(kw in text_lower for kw in LAB_EQUIPMENTS_KEYWORDS_TA) or
        any(kw in text_lower for kw in LAB_EQUIPMENTS_KEYWORDS_EN) or
        "equipment" in text_lower or
        "equipments" in text_lower or
        "உபகரணங்கள்" in text_lower or
        "கருவிகள்" in text_lower
    )
    if is_equip_query:
        return LAB_EQUIPMENTS_TA if is_ta else LAB_EQUIPMENTS_EN

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
