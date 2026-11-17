# J.A.R.V.I.S — AI Assistant

> **Current Milestone: Module 4 (Permanent Memory System)**  
> JARVIS is an interactive, voice-enabled, terminal AI assistant powered by Google Gemini API featuring local, persistent JSON memory.

---

## 1. What is JARVIS?

JARVIS is built incrementally across modular milestones:
- **Module 1 (Text Core):** Terminal-based chat, Gemini API integration, and in-memory session history.
- **Module 2 (Voice Input):** Microphone speech capture using SpeechRecognition and PyAudio, with seamless fallback to text on microphone issues.
- **Module 3 (Performance & Launch):** Real-time streaming responses, automatic retries with exponential backoff for 503/429 errors, fast model selection (`gemini-3.5-flash-lite`), and a one-click launcher (`start_jarvis.bat`).
- **Module 4 (Permanent Memory System):**
  - **Local JSON Storage:** Saves your name and explicit facts in `jarvis_memory.json`.
  - **Memory Persistence:** Remembers your facts across application restarts.
  - **Natural Commands:** Remember, forget, query, and clear memories using natural voice or text commands.
  - **Context Augmentation:** Seamlessly injects saved facts into Gemini's context so questions like *"What is my name?"* or *"What am I building?"* are answered naturally.
  - **Privacy & Safety:** Keeps memories local, ignores passwords/credentials, and never uploads files to the cloud.

---

## 2. Requirements

- **Operating System:** Windows 10 or Windows 11
- **Python Version:** Python 3.10+ (Python 3.12 recommended)
- **API Key:** A Google Gemini API Key from [Google AI Studio](https://aistudio.google.com/)
- **Microphone:** Required for default voice mode (or use `--text` for keyboard input)
- **Internet Connection:** Required for Google Gemini and Speech-to-Text APIs

---

## 3. Project Structure

```
c:\Users\HAROON TRADERS\Desktop\jarvis\
│
├── start_jarvis.bat     # Windows one-click launcher (Module 3 & 4)
├── main.py              # Main application entry point, conversation loops & streaming
├── memory.py            # Local permanent memory system (Module 4)
├── jarvis_memory.json   # Local persistent memory store (created automatically)
├── config.py            # Environment configuration, validation & model settings
├── voice_input.py       # Microphone handler & speech-to-text engine (Module 2)
├── .env                 # Real API key file (NEVER committed to git)
├── .env.example         # Example template showing configuration options
├── requirements.txt     # Project dependencies
├── .gitignore           # Ignores .env, jarvis_memory.json, venv/, __pycache__
└── README.md            # Comprehensive documentation & setup guide
```

---

## 4. How to Launch JARVIS

### Option A: Using the One-Click Launcher (Recommended)

1. **Default Voice Mode:**
   - Double-click **`start_jarvis.bat`** in Windows File Explorer, or run in terminal:
     ```cmd
     start_jarvis.bat
     ```
2. **Text Mode:**
   - Run in PowerShell or Command Prompt:
     ```cmd
     start_jarvis.bat --text
     ```

### Option B: Using the Python Virtual Environment Directly

1. **Voice Mode (Default):**
   ```powershell
   ./venv/Scripts/python.exe main.py
   ```
2. **Text Mode:**
   ```powershell
   ./venv/Scripts/python.exe main.py --text
   ```

### Exit Commands
At any time in voice mode or text mode, simply say or type:
- `exit`
- `quit`
- `bye`
- `goodbye`

---

## 5. Permanent Memory Commands (Module 4)

Permanent memory works in **both Voice Mode and Text Mode**. JARVIS only saves information when explicitly asked.

| Action | Example Command | Expected Response |
| :--- | :--- | :--- |
| **Save Name** | `Remember my name is Ameema.` | *"JARVIS: I will remember that your name is Ameema."* |
| **Save Fact** | `Remember that I am learning Python.` | *"JARVIS: I will remember that you are learning Python."* |
| **Save Project** | `Remember that I am building JARVIS.` | *"JARVIS: I will remember that you are building JARVIS."* |
| **Ask Stored Name** | `What is my name?` | *(Gemini answers)* *"JARVIS: Your name is Ameema."* |
| **List Memories** | `What do you remember about me?` | Displays formatted list of all saved facts. |
| **Forget Fact** | `Forget my learning goal.` | *"JARVIS: I have forgotten: 'learning Python'."* |
| **Forget Name** | `Forget my name.` | *"JARVIS: I have forgotten your name."* |
| **Clear All Memories** | `Clear all my memory.` | Asks for confirmation (`yes/no`) before wiping. |

---

## 6. Privacy & Safety Features

- **Local Storage Only:** All memories reside solely inside `jarvis_memory.json` on your computer.
- **Sensitive Information Filter:** If you accidentally ask JARVIS to remember a password, API key, token, or credit card, JARVIS refuses to save it to protect your privacy.
- **Git Protection:** `jarvis_memory.json` is automatically listed in `.gitignore` so your personal details are never uploaded to GitHub.
- **Corrupted File Recovery:** If `jarvis_memory.json` is accidentally corrupted or empty, JARVIS loads safe defaults without crashing.

---

## 7. Example Interaction (Across Application Restarts)

### Session 1: Saving Memories
```text
You: Remember my name is Ameema.
JARVIS: I will remember that your name is Ameema.

You: Remember that I am learning Python.
JARVIS: I will remember that you are learning Python.

You: exit
JARVIS: Goodbye. Shutting down.
```

*(You close the application, shut down your computer, and return the next day)*

### Session 2: Instant Memory Recall
```text
You: What is my name?
JARVIS is thinking...
JARVIS: Your name is Ameema. How may I assist you today?

You: What do you remember about me?
JARVIS: Here is what I remember about you:
- Name: Ameema
- You are learning Python

You: exit
JARVIS: Goodbye. Shutting down.
```

---

## 8. What is NOT Included (Reserved for Future Modules)

- Text-to-Speech (JARVIS speaking aloud through computer speakers)
- Wake-word detection ("Hey JARVIS")
- Operating system automation (mouse, keyboard, or local files)
- Graphical user interface (GUI) or HUD
