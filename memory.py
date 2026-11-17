"""
memory.py - Local Permanent Memory System for JARVIS (Module 4)

Provides persistent JSON-based memory storage for facts and user preferences.
Supports remembering, forgetting, listing, and clearing memories with
safe file handling, corrupted file recovery, and sensitive data filtering.
"""

import json
import os
import re

MEMORY_FILE_NAME = "jarvis_memory.json"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_MEMORY_PATH = os.path.join(BASE_DIR, MEMORY_FILE_NAME)

# Sensitive patterns that should never be stored in permanent memory
SENSITIVE_PATTERNS = [
    r"\bpassword\b",
    r"\bpasscode\b",
    r"\bapi[_\s-]?key\b",
    r"\bsecret\b",
    r"\btoken\b",
    r"\bcredit[_\s-]?card\b",
    r"\bcvv\b",
    r"\bssn\b",
    r"\bpin\b",
    r"aiza[0-9a-za-z-_]{35}",
]


class MemoryManager:
    """
    Manages loading, updating, querying, and persisting user memories.
    """

    def __init__(self, file_path=DEFAULT_MEMORY_PATH):
        """
        Initializes the MemoryManager and loads existing memories.

        Args:
            file_path (str): Path to the jarvis_memory.json file.
        """
        self.file_path = file_path
        self.data = {"name": None, "facts": []}
        self.load_memory()

    def load_memory(self):
        """
        Loads memories from the JSON file safely.
        Handles missing, empty, or corrupted files gracefully.
        """
        if not os.path.exists(self.file_path):
            self.data = {"name": None, "facts": []}
            return

        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    # Empty file
                    self.data = {"name": None, "facts": []}
                    return

                loaded_data = json.loads(content)

                # Validate data structure
                if not isinstance(loaded_data, dict):
                    self.data = {"name": None, "facts": []}
                    return

                name = loaded_data.get("name")
                if not isinstance(name, str):
                    name = None

                raw_facts = loaded_data.get("facts", [])
                if not isinstance(raw_facts, list):
                    raw_facts = []

                # Clean and deduplicate facts
                cleaned_facts = [str(fact).strip() for fact in raw_facts if str(fact).strip()]

                self.data = {
                    "name": name,
                    "facts": cleaned_facts,
                }

        except (json.JSONDecodeError, OSError) as error:
            print(f"[JARVIS Memory Notice: Memory file corrupted or unreadable ({error}). Safe defaults loaded.]")
            self.data = {"name": None, "facts": []}

    def save_memory(self):
        """
        Saves the current in-memory data to the JSON file safely.
        """
        try:
            # Write to a temporary file first, then replace for atomic persistence
            temp_path = self.file_path + ".tmp"
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
            
            # Atomic file replace to prevent partial writes
            if os.path.exists(temp_path):
                os.replace(temp_path, self.file_path)
        except Exception as error:
            print(f"[JARVIS Memory Error: Failed to save memory to disk: {error}]")

    def is_sensitive(self, text):
        """
        Checks whether the given text contains passwords or sensitive credentials.

        Args:
            text (str): The text to inspect.

        Returns:
            bool: True if sensitive data is detected.
        """
        text_lower = text.lower()
        for pattern in SENSITIVE_PATTERNS:
            if re.search(pattern, text_lower):
                return True
        return False

    def remember(self, text):
        """
        Extracts and stores facts or user name from a 'remember' command.

        Args:
            text (str): The user's input string.

        Returns:
            tuple: (success (bool), response_message (str))
        """
        if self.is_sensitive(text):
            return (
                False,
                "For your privacy and security, I cannot store passwords, API keys, or sensitive credentials in permanent memory.",
            )

        cleaned = text.strip().rstrip(".!?,")

        # 1. Match: "Remember (that) my name is <name>"
        name_match = re.search(r"\bremember\s+(?:that\s+)?my\s+name\s+is\s+([A-Za-z\s'-]+)", cleaned, re.I)
        if name_match:
            new_name = name_match.group(1).strip()
            self.data["name"] = new_name
            self.save_memory()
            return True, f"I will remember that your name is {new_name}."

        # 2. Match: "Remember (that) I am <fact>" (e.g. learning Python, building JARVIS)
        iam_match = re.search(r"\bremember\s+(?:that\s+)?(?:i\s+am\s+|i'm\s+)(.+)", cleaned, re.I)
        if iam_match:
            fact_content = iam_match.group(1).strip()
            # Standardize phrasing
            full_fact = f"learning {fact_content[9:]}" if fact_content.lower().startswith("learning ") else fact_content
            if full_fact not in self.data["facts"]:
                self.data["facts"].append(full_fact)
                self.save_memory()
            return True, f"I will remember that you are {full_fact}."

        # 3. Match: "Remember (that) <fact>"
        general_match = re.search(r"\bremember\s+(?:that\s+)?(.+)", cleaned, re.I)
        if general_match:
            fact_content = general_match.group(1).strip()
            if fact_content not in self.data["facts"]:
                self.data["facts"].append(fact_content)
                self.save_memory()
            return True, f"I will remember that {fact_content}."

        return False, "I'm not sure what you would like me to remember. Please say e.g., 'Remember my name is Ameema' or 'Remember that I am learning Python'."

    def forget(self, text):
        """
        Removes a specific saved fact or name from memory.

        Args:
            text (str): The user's input string.

        Returns:
            tuple: (success (bool), response_message (str))
        """
        cleaned = text.strip().rstrip(".!?,")

        # 1. Check if user wants to forget their name
        if re.search(r"\bforget\s+(?:my\s+)?name\b", cleaned, re.I):
            if self.data.get("name"):
                old_name = self.data["name"]
                self.data["name"] = None
                self.save_memory()
                return True, f"I have forgotten your name (previously saved as {old_name})."
            return False, "I do not have your name saved in my permanent memory."

        # 2. Extract target to forget
        target_match = re.search(r"\bforget\s+(?:that\s+)?(?:i\s+am\s+|i'm\s+|my\s+)?(.+)", cleaned, re.I)
        if not target_match:
            return False, "Please specify what you would like me to forget (e.g., 'Forget my name' or 'Forget my learning goal')."

        target = target_match.group(1).strip().lower()

        # Find matching fact in facts list
        matched_index = None
        matched_fact = None

        # A. Direct substring search
        for idx, fact in enumerate(self.data["facts"]):
            fact_lower = fact.lower()
            if target in fact_lower or fact_lower in target:
                matched_index = idx
                matched_fact = fact
                break

        # B. Keyword / concept overlap if no direct substring match
        if matched_index is None:
            target_words = set(re.findall(r"\w+", target)) - {"that", "i", "am", "my", "the", "a", "an"}
            best_overlap = 0
            for idx, fact in enumerate(self.data["facts"]):
                fact_words = set(re.findall(r"\w+", fact.lower()))
                overlap = len(target_words & fact_words)
                # Map "learning goal" -> "learning"
                if "goal" in target_words and any("learn" in w for w in fact_words):
                    overlap += 2
                if overlap > best_overlap:
                    best_overlap = overlap
                    matched_index = idx
                    matched_fact = fact

        if matched_index is not None:
            self.data["facts"].pop(matched_index)
            self.save_memory()
            return True, f"I have forgotten: '{matched_fact}'."

        return False, f"I couldn't find any saved memory about '{target}'."

    def clear_all(self):
        """
        Wipes all permanent memories completely and updates the file.

        Returns:
            str: Confirmation message.
        """
        self.data = {"name": None, "facts": []}
        self.save_memory()
        return "All permanent memories have been cleared."

    def get_summary(self):
        """
        Returns a friendly human-readable summary of all saved memories.

        Returns:
            str: The formatted summary string.
        """
        name = self.data.get("name")
        facts = self.data.get("facts", [])

        if not name and not facts:
            return "I do not have any permanent memories saved about you yet."

        lines = ["Here is what I remember about you:"]
        if name:
            lines.append(f"- Name: {name}")
        for fact in facts:
            if fact.lower().startswith("learning ") or fact.lower().startswith("building "):
                lines.append(f"- You are {fact}")
            else:
                lines.append(f"- {fact}")

        return "\n".join(lines)

    def get_context_instruction(self):
        """
        Formats saved memories into a clear context prompt for Gemini.

        Returns:
            str: Context string to append to Gemini's system instruction.
        """
        name = self.data.get("name")
        facts = self.data.get("facts", [])

        if not name and not facts:
            return ""

        context_lines = ["Permanent memories about the user:"]
        if name:
            context_lines.append(f"- The user's name is {name}.")
        for fact in facts:
            if fact.lower().startswith("learning ") or fact.lower().startswith("building "):
                context_lines.append(f"- The user is {fact}.")
            else:
                context_lines.append(f"- {fact}.")

        return "\n".join(context_lines)

