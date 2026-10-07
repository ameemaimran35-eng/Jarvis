"""
main.py - Entry point for JARVIS AI Assistant (Module 1)

A text-based interactive AI assistant terminal application powered
by the official Google Gemini API (google-genai Python SDK).
"""

import sys
from google import genai
from google.genai import types
from google.genai.errors import APIError

import config


def print_banner():
    """Prints the application startup banner."""
    print("========================================")
    print("J.A.R.V.I.S")
    print("Basic AI Assistant")
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


def main():
    """Runs the main conversation loop."""
    # 1. Validate configuration before running
    config.validate_config()

    # 2. Show startup banner
    print_banner()

    # 3. Create client and chat session with conversation context
    try:
        client, chat = initialize_jarvis()
    except Exception as error:
        print("JARVIS: Sorry, I couldn't connect to the AI service right now.")
        print(f"Technical error: {error}\n")
        sys.exit(1)

    # 4. Interactive conversation loop
    while True:
        try:
            user_input = input("You: ")
        except (KeyboardInterrupt, EOFError):
            print("\nJARVIS: Goodbye. Shutting down.")
            break

        # Check for empty input (user just pressed Enter)
        cleaned_input = user_input.strip()
        if not cleaned_input:
            print("Please enter a message.\n")
            continue

        # Check for exit commands
        if cleaned_input.lower() in ["exit", "quit", "bye"]:
            print("JARVIS: Goodbye. Shutting down.")
            break

        # Send message to Gemini and display the response
        try:
            response = chat.send_message(cleaned_input)
            print(f"\nJARVIS: {response.text}\n")
        except APIError as error:
            # Extract a concise, readable error message
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


if __name__ == "__main__":
    main()
