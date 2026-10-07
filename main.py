"""
main.py - Entry point for JARVIS AI Assistant (Module 2: Voice Input)

An interactive AI assistant terminal application powered by Google Gemini API
with voice input capabilities via microphone and speech recognition.
"""

import sys
from google import genai
from google.genai import types
from google.genai.errors import APIError

import config
from voice_input import VoiceInputHandler, capture_voice_input


def print_banner(voice_mode=True):
    """Prints the application startup banner."""
    print("========================================")
    print("J.A.R.V.I.S")
    if voice_mode:
        print("Voice AI Assistant (Module 2)")
        print("==================")
        print("# Speak into your microphone to talk with JARVIS.")
        print("# Say 'exit', 'quit', or 'bye' to quit.\n")
    else:
        print("Basic AI Assistant (Text Mode)")
        print("==================")
        print("# Type 'exit' to quit.\n")


def initialize_jarvis():
    """
    Initializes the Gemini client and chat session.
    Configures JARVIS persona via system instruction and maintains
    in-memory conversation context for the active session.

    Returns:
        tuple: (client, chat) keeping the client instance alive for the session.
    """
    # Initialize the Google GenAI client with our secure API key
    client = genai.Client(api_key=config.GEMINI_API_KEY)

    # Personality and role definition for JARVIS
    system_instruction = (
        "You are JARVIS, a helpful, polite, concise, and professional AI assistant. "
        "Answer questions clearly, directly, and courteously. "
        "You are an artificial intelligence and do not pretend to possess "
        "human consciousness, self-awareness, or sentience."
    )

    # Start a chat session that retains conversation context
    chat = client.chats.create(
        model=config.GEMINI_MODEL,
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
        ),
    )
    return client, chat


def send_message_to_gemini(chat, message_text):
    """
    Sends user text to the existing Gemini chat session and displays the response.

    Args:
        chat: The active Gemini chat session.
        message_text (str): The prompt text to send.
    """
    try:
        response = chat.send_message(message_text)
        print(f"\nJARVIS: {response.text}\n")
    except APIError as error:
        error_msg = getattr(error, "message", None) or str(error)
        if "API_KEY_INVALID" in str(error) or "API key not valid" in str(error):
            error_msg = "Invalid Gemini API key. Please verify your key in .env"
        elif len(error_msg) > 150:
            error_msg = error_msg[:150] + "..."
        print(f"\nJARVIS: Sorry, I couldn't connect to the AI service right now.")
        print(f"Technical error: {error_msg}\n")
    except Exception as error:
        print(f"\nJARVIS: Sorry, I couldn't connect to the AI service right now.")
        print(f"Technical error: {error}\n")


def is_exit_command(text):
    """
    Checks if the user requested to terminate the session.

    Args:
        text (str): User speech or input.

    Returns:
        bool: True if an exit command was detected.
    """
    cleaned = text.strip().lower().rstrip(".!?,")
    return cleaned in ["exit", "quit", "bye", "goodbye"]


def run_voice_loop(chat):
    """
    Main interactive loop for Module 2: Voice Input.
    Captures microphone speech, transcribes to text, and routes to Gemini.
    """
    voice_handler = VoiceInputHandler()

    while True:
        try:
            user_text, mic_error = capture_voice_input(voice_handler)
        except (KeyboardInterrupt, EOFError):
            print("\nJARVIS: Goodbye. Shutting down.")
            break

        # Handle microphone hardware/connection errors gracefully
        if mic_error:
            try:
                fallback_input = input("Press Enter to retry voice input, or type your message (or 'exit'): ")
            except (KeyboardInterrupt, EOFError):
                print("\nJARVIS: Goodbye. Shutting down.")
                break

            cleaned_fallback = fallback_input.strip()
            if not cleaned_fallback:
                continue

            if is_exit_command(cleaned_fallback):
                print("\nJARVIS: Goodbye. Shutting down.")
                break

            print(f"You: {cleaned_fallback}")
            send_message_to_gemini(chat, cleaned_fallback)
            continue

        # If speech was not understood or was empty, prompt and try again
        if not user_text:
            continue

        # Display transcribed user speech
        print(f"You: {user_text}")

        # Check for exit commands
        if is_exit_command(user_text):
            print("\nJARVIS: Goodbye. Shutting down.")
            break

        # Send transcribed message to Gemini
        send_message_to_gemini(chat, user_text)


def run_text_loop(chat):
    """
    Preserved text-based interactive loop for Module 1 backward compatibility.
    """
    while True:
        try:
            user_input = input("You: ")
        except (KeyboardInterrupt, EOFError):
            print("\nJARVIS: Goodbye. Shutting down.")
            break

        cleaned_input = user_input.strip()
        if not cleaned_input:
            print("Please enter a message.\n")
            continue

        if is_exit_command(cleaned_input):
            print("JARVIS: Goodbye. Shutting down.")
            break

        send_message_to_gemini(chat, cleaned_input)


def main():
    """Runs the main JARVIS application."""
    # 1. Validate configuration before running
    config.validate_config()

    # Determine whether text mode was explicitly requested via flag
    use_text_mode = "--text" in sys.argv

    # 2. Show startup banner
    print_banner(voice_mode=not use_text_mode)

    # 3. Create client and chat session with conversation context
    try:
        client, chat = initialize_jarvis()
    except Exception as error:
        print("JARVIS: Sorry, I couldn't connect to the AI service right now.")
        print(f"Technical error: {error}\n")
        sys.exit(1)

    # 4. Run conversation loop (Voice by default for Module 2)
    if use_text_mode:
        run_text_loop(chat)
    else:
        run_voice_loop(chat)


if __name__ == "__main__":
    main()
