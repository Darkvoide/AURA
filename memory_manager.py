# -*- coding: utf-8 -*-
"""
====================================================================
           🧠 AURA - Dynamic Long-Term Memory System
   Saves facts, notes, and user instructions directly into memory
   for future recall across sessions.
====================================================================
"""

import os
import json
import time

MEMORY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "robot_memory.json")

# Keywords that indicate the user wants to store something in memory
MEMORY_SAVE_TRIGGERS = [
    "remember this", "remember that", "save this to memory", "save to memory",
    "store in memory", "store this in memory", "note this down",
    "idha nyabagam vachuko", "nyabagam vachuko", "idha memory la ethiko",
    "memory la ethiko", "memory la store pannu", "memory la save pannu",
    "idha memory la vachuko", "idha marakkadha", "memory la pottuko",
    "future la nyabagam vachuko"
]

MEMORY_RECALL_TRIGGERS = [
    "what do you remember", "what is in your memory", "show your memory",
    "memory la enna irukku", "un நினைவகத்தில் என்ன இருக்கிறது",
    "un memory la enna irukku", "enna nyabagam irukku"
]

MEMORY_CLEAR_TRIGGERS = [
    "clear memory", "forget everything", "reset memory", "delete memory",
    "memory ah clear pannu", "memory ah reset pannu", "ellathayum maranthudu"
]


class MemoryManager:
    """Manages persistent robot memory stored in a local JSON file."""

    def __init__(self, filepath: str = MEMORY_FILE):
        self.filepath = filepath
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        if not os.path.exists(self.filepath):
            initial_data = {
                "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "facts": [
                    {
                        "note": "Creators are Kishore, Mohandas, and Latheeswaran at iGrid Lab. They are young, unmarried engineers.",
                        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                    }
                ]
            }
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(initial_data, f, ensure_ascii=False, indent=2)

    def _load_data(self) -> dict:
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {"facts": []}

    def _save_data(self, data: dict):
        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[Memory Save Error]: {e}")

    def add_memory(self, note: str) -> bool:
        """Add a new fact or instruction to memory."""
        if not note or not note.strip():
            return False
        clean_note = note.strip()
        data = self._load_data()
        if "facts" not in data:
            data["facts"] = []
        data["facts"].append({
            "note": clean_note,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        })
        self._save_data(data)
        return True

    def get_all_memories(self) -> list[str]:
        """Return list of all stored memory strings."""
        data = self._load_data()
        return [item["note"] for item in data.get("facts", []) if "note" in item]

    def clear_memories(self) -> bool:
        """Reset learned memories."""
        data = {
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "facts": [
                {
                    "note": "Creators are Kishore, Mohandas, and Latheeswaran at iGrid Lab. They are young, unmarried engineers.",
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                }
            ]
        }
        self._save_data(data)
        return True

    def get_memory_context(self) -> str:
        """Format stored memories for Gemini prompt context."""
        memories = self.get_all_memories()
        if not memories:
            return ""
        bullet_points = "\n".join([f"- {m}" for m in memories])
        return f"\nDYNAMIC USER-TAUGHT MEMORIES (Things taught to you to remember):\n{bullet_points}\n"

    def handle_memory_command(self, text: str, is_tamil: bool) -> str | None:
        """Check if user is instructing AURA to remember, recall, or clear memory."""
        text_lower = text.lower().strip()

        # 1. Clear Memory
        for trig in MEMORY_CLEAR_TRIGGERS:
            if trig in text_lower:
                self.clear_memories()
                if is_tamil:
                    return "நான் என் நினைவகத்தில் உள்ள புதிய தகவல்களை அழித்துவிட்டேன். இப்போது நினைவகம் ரீசெட் செய்யப்பட்டுள்ளது."
                return "I have cleared my dynamic memories. My memory has been reset."

        # 2. Recall Memory
        for trig in MEMORY_RECALL_TRIGGERS:
            if trig in text_lower:
                memories = self.get_all_memories()
                if not memories:
                    if is_tamil:
                        return "என் நினைவகத்தில் தற்போது கூடுதல் தகவல்கள் எதுவும் சேமிக்கப்படவில்லை."
                    return "There are no user-taught memories stored right now."
                if is_tamil:
                    mem_list = ", ".join(memories)
                    return f"என் நினைவகத்தில் சேமிக்கப்பட்டுள்ள தகவல்கள்: {mem_list}."
                mem_list = "; ".join(memories)
                return f"Here is what I have stored in my memory: {mem_list}."

        # 3. Save to Memory
        for trig in MEMORY_SAVE_TRIGGERS:
            if trig in text_lower:
                # Extract the actual fact following the trigger
                idx = text_lower.find(trig)
                fact = text[idx + len(trig):].strip(" :,-_")
                if not fact:
                    # Maybe the fact came before the trigger
                    fact = text[:idx].strip(" :,-_")

                if fact:
                    self.add_memory(fact)
                    if is_tamil:
                        return f"சரி! '{fact}' என்ற தகவலை நான் நேரடியாக என் நினைவகத்தில் (Memory) சேமித்துக் கொண்டேன். எதிர்காலத்தில் இதை நினைவில் வைத்திருப்பேன்!"
                    return f"Understood! I have saved '{fact}' directly to my persistent memory. I will remember this for the future!"
                else:
                    if is_tamil:
                        return "நான் என்ன தகவலை நினைவகத்தில் சேமிக்க வேண்டும் என்று கூறுங்கள்."
                    return "Please tell me what information you would like me to remember."

        return None

