# J.A.R.V.I.S — Module 1: Basic AI Assistant

> **Note:** Module 1 is strictly a **text-based AI assistant** running in your Windows terminal. It establishes the basic Python and Gemini AI core for future modules.

---

## 1. What is JARVIS Module 1?

Module 1 is the foundational brain of the JARVIS project. It provides:
- A clean terminal-based chat interface.
- Direct integration with Google's official Gemini AI SDK (`google-genai`).
- Session-based conversation memory (so JARVIS remembers your name and recent statements while running).
- Secure environment configuration using `python-dotenv` (keeping your API key safe and separate from source code).
- Beginner-friendly error handling for missing keys, network disconnects, and empty inputs.

---

## 2. Requirements

- **Operating System:** Windows 10 or Windows 11
- **Python Version:** Python 3.10+ (Python 3.12 recommended)
- **API Key:** A Google Gemini API Key from [Google AI Studio](https://aistudio.google.com/)
- **Internet Connection:** Required to communicate with the Gemini API

---

## 3. Project Structure

```
JARVIS/
│
├── main.py           # Main application entry point & conversation loop
├── config.py         # Loads and validates environment variables (.env)
├── .env              # Real API key file (NEVER committed to git)
├── .env.example      # Example template showing required environment variables
├── requirements.txt  # Project dependencies (google-genai, python-dotenv)
├── .gitignore        # Specifies files git should ignore (.env, venv, cache)
└── README.md         # Documentation & setup guide
```

### Purpose of Each File:
- **`main.py`**: Handles user input, prints banners, invokes the Gemini chat session, remembers conversation history, and handles exit commands.
- **`config.py`**: Loads variables from `.env`, checks that `GEMINI_API_KEY` is present, and prevents the app from running without a valid configuration.
- **`.env`**: Stores your private `GEMINI_API_KEY`. It stays on your computer and is ignored by Git.
- **`.env.example`**: A safe template for other developers showing what variables must be in `.env`.
- **`requirements.txt`**: Lists the official Python libraries needed (`google-genai` and `python-dotenv`).
- **`.gitignore`**: Prevents accidental leaks of `.env` or tracking of the `venv/` directory and compiled Python bytecode files.
- **`README.md`**: Step-by-step instructions for installation, configuration, and usage.

---

## 4. Step-by-Step Windows Setup Guide

Open PowerShell or Command Prompt in the project folder (`c:\Users\HAROON TRADERS\Desktop\jarvis`) and run:

### Step 1: Verify Python Installation
```powershell
python --version
```
*(Ensure Python 3.10 or higher is displayed)*

### Step 2: Create a Virtual Environment
```powershell
python -m venv venv
```
This creates an isolated `venv` folder where dependencies are safely installed.

### Step 3: Activate the Virtual Environment
On Windows PowerShell:
```powershell
.\venv\Scripts\Activate.ps1
```
*(If you see an execution policy warning in PowerShell, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` first)*

On Windows Command Prompt (CMD):
```cmd
venv\Scripts\activate.bat
```

When activated, you will see `(venv)` at the beginning of your command prompt.

### Step 4: Install Dependencies
```powershell
pip install -r requirements.txt
```

### Step 5: Configure Your Gemini API Key
1. Open the `.env` file in the project folder with any text editor (Notepad, VS Code, etc.).
2. Replace `YOUR_API_KEY_HERE` with your actual Gemini API key obtained from [Google AI Studio](https://aistudio.google.com/):
   ```env
   GEMINI_API_KEY=AIzaSy...your_actual_key_here...
   ```
3. Save the `.env` file.

> **Security Warning:** Never share your API key, commit `.env` to GitHub, or paste your key into public chats.

### Step 6: Run JARVIS
```powershell
python main.py
```

---

## 5. Example Interaction

```text
========================================
J.A.R.V.I.S
Basic AI Assistant
==================
# Type 'exit' to quit.

You: Hello Jarvis

JARVIS: Hello! How may I assist you today?

You: My name is Ameema.

JARVIS: Nice to meet you, Ameema. How can I help you today?

You: What is my name?

JARVIS: Your name is Ameema.

You: What is Python?

JARVIS: Python is a popular, high-level programming language known for its simplicity and readability.

You: exit
JARVIS: Goodbye. Shutting down.
```

---

## 6. Current Limitations (Module 1)

Module 1 is intentionally scoped to establish a rock-solid, lightweight foundation:
- **Session-only memory:** Conversation history is stored in memory during the running session. Exiting the program resets conversation memory.
- **Text-only:** Input and output are strictly text in the terminal.
- **Single AI Provider:** Uses official Google Gemini API only.

---

## 7. What is NOT Included (Reserved for Future Modules)

To keep Module 1 simple and beginner-friendly, the following features are intentionally **not** included:
- Voice recognition / Microphone input (Speech-to-Text)
- Text-to-Speech (TTS) / ElevenLabs
- Futuristic HUD, 3D avatar, or GUI (Tkinter, PyQt, Electron, React)
- Operating system control or automation (mouse, keyboard, files, system scripts)
- Web scraping or browser automation
- Long-term persistent databases (SQL, Vector databases)
- Autonomous coding agents or self-upgrading routines
- Multiple competing LLM providers
