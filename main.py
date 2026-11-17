"""
main.py - Entry point for JARVIS AI Assistant (Module 4: Permanent Memory)

An interactive AI assistant terminal application powered by Google Gemini API
featuring real-time streaming, resilient retry logic, safe fallback model support,
local JSON-based permanent memory (Module 4), microphone voice input (Module 2),
and terminal text mode (Module 1).
"""

import random
import re
import sys
import time

from google import genai
from google.genai import types
from google.genai.errors import APIError

import config
from memory import MemoryManager
from voice_input import VoiceInputHandler, capture_voice_input


def print_banner(voice_mode=True):
    """Prints the application startup banner."""
    print("========================================")
    print("J.A.R.V.I.S")
    if voice_mode:
        print("Voice AI Assistant (Module 4: Permanent Memory)")
        print("==================")
        print("# Speak into your microphone to talk with JARVIS.")
        print("# Commands: 'Remember...', 'Forget...', 'What do you remember about me?'")
        print("# Say 'exit', 'quit', or 'bye' to quit.\n")
    else:
        print("Basic AI Assistant (Text Mode - Module 4)")
        print("==================")
        print("# Type your message to chat with JARVIS.")
        print("# Commands: 'Remember...', 'Forget...', 'Clear all my memory'")
        print("# Type 'exit' to quit.\n")


def get_system_instruction(memory_context=""):
    """
    Returns the persona and behavioral guidelines for JARVIS,
    augmented with any permanent memories about the user.
    """
    base_instruction = (
        "You are JARVIS, a helpful, polite, concise, and professional AI assistant. "
        "Answer questions clearly, directly, and courteously. "
        "You are an artificial intelligence and do not pretend to possess "
        "human consciousness, self-awareness, or sentience."
    )
    if memory_context:
        return f"{base_instruction}\n\n{memory_context}"
    return base_instruction


def is_transient_error(error):
    """
    Checks if an API error or exception is temporary and eligible for retry.

    Transient conditions include:
    - HTTP 429: Rate limit or temporary resource exhaustion
    - HTTP 500, 502, 503, 504: Server overload or temporary service outages
    - Network connectivity drops, timeouts, and connection resets
    """
    code = getattr(error, "code", None)
    if code in (429, 500, 502, 503, 504):
        return True

    err_str = str(error).lower()
    transient_indicators = [
        "503", "unavailable", "high demand", "overloaded",
        "429", "resource_exhausted", "rate limit",
        "500", "internal server error", "502", "bad gateway",
        "504", "gateway timeout", "timeout", "timed out",
        "connection reset", "connection error", "remoteprotocolerror",
        "network error", "temporary failure"
    ]
    if any(indicator in err_str for indicator in transient_indicators):
        return True

    if isinstance(error, (ConnectionError, TimeoutError)):
        return True

    return False


def is_permanent_error(error):
    """
    Checks if an API error is permanent and should NOT be retried.

    Permanent errors include invalid API keys, authentication rejections,
    and invalid requests (HTTP 400, 401, 403, 404).
    """
    code = getattr(error, "code", None)
    if code in (400, 401, 403, 404):
        return True

    err_str = str(error)
    if "API_KEY_INVALID" in err_str or "API key not valid" in err_str:
        return True

    return False


def get_retry_delay(error, attempt, base_delay=1.5):
    """
    Calculates the backoff delay with jitter, respecting Retry-After headers if present.

    Formula: base_delay * (2 ** attempt) + random_jitter
    """
    response = getattr(error, "response", None)
    if response and hasattr(response, "headers"):
        headers = response.headers or {}
        retry_after = headers.get("retry-after") or headers.get("Retry-After")
        if retry_after:
            try:
                delay = float(retry_after)
                if 0 < delay <= 30:
                    return delay
            except (ValueError, TypeError):
                pass

    backoff = base_delay * (2 ** attempt)
    jitter = random.uniform(0.1, 0.7)
    return backoff + jitter


def initialize_jarvis(model_name=None, memory_manager=None):
    """
    Initializes the Gemini client, loads permanent memory, and creates the chat session.

    Args:
        model_name (str, optional): The Gemini model ID to use. Defaults to config.GEMINI_MODEL.
        memory_manager (MemoryManager, optional): Existing MemoryManager instance.

    Returns:
        tuple: (client, chat, memory_manager)
    """
    selected_model = model_name or config.GEMINI_MODEL
    client = genai.Client(api_key=config.GEMINI_API_KEY)

    if memory_manager is None:
        memory_manager = MemoryManager()

    memory_context = memory_manager.get_context_instruction()
    system_instruction = get_system_instruction(memory_context)

    # Retry startup initialization if a transient network hiccup occurs
    for attempt in range(config.MAX_RETRIES):
        try:
            chat = client.chats.create(
                model=selected_model,
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction,
                ),
            )
            return client, chat, memory_manager
        except Exception as error:
            if is_permanent_error(error):
                raise
            if attempt < config.MAX_RETRIES - 1 and is_transient_error(error):
                delay = get_retry_delay(error, attempt, config.RETRY_BASE_DELAY)
                time.sleep(delay)
                continue
            raise


def stream_from_chat(chat, message_text):
    """
    Streams the response from an active chat session chunk-by-chunk.

    Yields each text fragment as it arrives from the Gemini API.
    Prints the 'JARVIS: ' prefix only when the first valid token arrives.

    Args:
        chat: The active Gemini Chat session.
        message_text (str): The prompt text to send.

    Returns:
        tuple: (full_text, chunk_count)
    """
    stream = chat.send_message_stream(message_text)
    full_text = []
    chunk_count = 0
    prefix_printed = False

    for chunk in stream:
        chunk_text = getattr(chunk, "text", None)
        if chunk_text:
            if not prefix_printed:
                print("JARVIS: ", end="", flush=True)
                prefix_printed = True
            chunk_count += 1
            full_text.append(chunk_text)
            print(chunk_text, end="", flush=True)

    return "".join(full_text), chunk_count


def send_message_to_gemini(chat, message_text, is_voice_mode=False, client=None):
    """
    Sends user text to Gemini with real-time response streaming, visual feedback,
    exponential backoff retry for transient errors, and fallback model support.

    Args:
        chat: The active Gemini chat session.
        message_text (str): The user's input prompt.
        is_voice_mode (bool): Whether the request originated from voice mode.
        client (genai.Client, optional): The active GenAI client for fallback model creation.

    Returns:
        tuple: (success (bool), active_chat)
    """
    max_retries = config.MAX_RETRIES
    base_delay = config.RETRY_BASE_DELAY

    # 1. Immediate visual feedback before network roundtrip begins
    if is_voice_mode:
        print("JARVIS is processing your request...")
    else:
        print("JARVIS is thinking...")

    # 2. Primary model retry loop
    for attempt in range(max_retries):
        try:
            _, chunk_count = stream_from_chat(chat, message_text)

            if chunk_count == 0:
                print("JARVIS: [I received your message, but the response was blank.]")

            # Clean trailing newline after stream finishes
            print("\n")
            return True, chat

        except Exception as error:
            # Clean up the line after any partial/failed print
            print()

            # Permanent failure check (e.g., bad API key, invalid request)
            if is_permanent_error(error):
                if "API_KEY_INVALID" in str(error) or "API key not valid" in str(error):
                    print("JARVIS: Invalid Gemini API key. Please verify your key in .env\n")
                else:
                    print(f"JARVIS: Configuration error: {error}\n")
                return False, chat

            # Transient failure check (429, 503, network drop)
            if is_transient_error(error) and attempt < max_retries - 1:
                delay = get_retry_delay(error, attempt, base_delay)
                error_label = "server is busy" if "503" in str(error) or "overload" in str(error).lower() else "connection issue"
                if "429" in str(error):
                    error_label = "rate limit reached"

                print(f"JARVIS: Gemini {error_label}. Retrying in {delay:.1f}s (attempt {attempt + 1}/{max_retries})...")
                time.sleep(delay)
                continue

            # If all retries for primary model exhausted, check if fallback model is configured
            if config.GEMINI_FALLBACK_MODEL and client is not None:
                fallback_model = config.GEMINI_FALLBACK_MODEL
                if fallback_model != getattr(chat, "_model", None):
                    print(f"JARVIS: Primary model unavailable. Switching to fallback model '{fallback_model}'...")
                    try:
                        fallback_chat = client.chats.create(
                            model=fallback_model,
                            history=chat.get_history(),
                            config=types.GenerateContentConfig(
                                system_instruction=getattr(chat, "_config", None).system_instruction if getattr(chat, "_config", None) else get_system_instruction(),
                            ),
                        )
                        _, chunk_count = stream_from_chat(fallback_chat, message_text)
                        if chunk_count == 0:
                            print("JARVIS: [I received your message, but the response was blank.]")
                        print("\n")
                        return True, fallback_chat
                    except Exception as fallback_error:
                        print(f"\nJARVIS: Fallback model also failed: {fallback_error}")

            # Explain the failure clearly to the user
            if "429" in str(error):
                print("JARVIS: The API rate limit or quota has been reached. Please wait a moment before trying again.\n")
            elif "503" in str(error) or "overload" in str(error).lower():
                print("JARVIS: The AI service is currently overloaded with high demand. Please try again shortly.\n")
            else:
                error_msg = getattr(error, "message", None) or str(error)
                if len(error_msg) > 150:
                    error_msg = error_msg[:150] + "..."
                print("JARVIS: Sorry, I couldn't reach the AI service right now.")
                print(f"Technical details: {error_msg}\n")

            return False, chat

    return False, chat


def is_exit_command(text):
    """
    Checks if the user requested to terminate the session.

    Args:
        text (str): User speech or typed input.

    Returns:
        bool: True if an exit command was detected.
    """
    cleaned = text.strip().lower().rstrip(".!?,")
    return cleaned in ["exit", "quit", "bye", "goodbye"]


def handle_memory_command(user_text, memory_manager, chat, client, is_voice_mode=False, voice_handler=None):
    """
    Inspects user input for permanent memory commands (remember, forget, clear, query).

    Args:
        user_text (str): The raw user input.
        memory_manager (MemoryManager): The active memory manager.
        chat: The active Gemini chat session.
        client: The active GenAI client.
        is_voice_mode (bool): Whether input came from voice mode.
        voice_handler (VoiceInputHandler, optional): Voice handler for voice confirmations.

    Returns:
        tuple: (handled (bool), active_chat)
    """
    cleaned = user_text.strip().rstrip(".!?,")
    cleaned_lower = cleaned.lower()

    # 1. Query: What do you remember / know about me?
    query_patterns = [
        r"^what\s+do\s+you\s+(?:remember|know)\s+about\s+me$",
        r"^what\s+is\s+in\s+your\s+memory$",
        r"^show\s+(?:my\s+)?memories$",
        r"^list\s+(?:my\s+)?memories$",
    ]
    if any(re.match(p, cleaned_lower) for p in query_patterns):
        summary = memory_manager.get_summary()
        print(f"\nJARVIS: {summary}\n")
        return True, chat

    # 2. Clear all memories (with explicit confirmation)
    clear_patterns = [
        r"^clear\s+all\s+my\s+memory$",
        r"^clear\s+all\s+memory$",
        r"^clear\s+my\s+memory$",
        r"^delete\s+all\s+memories$",
        r"^wipe\s+memory$",
    ]
    if any(re.match(p, cleaned_lower) for p in clear_patterns):
        print("\nJARVIS: Are you sure you want to clear all permanent memories? (yes/no)")
        
        # Capture confirmation
        confirmed = False
        if is_voice_mode and voice_handler:
            confirm_text, _ = capture_voice_input(voice_handler, timeout=5)
            if confirm_text:
                print(f"You: {confirm_text}")
                confirmed = confirm_text.strip().lower().rstrip(".!?,") in ["yes", "y", "confirm", "yeah", "sure"]
            else:
                try:
                    text_input = input("Confirmation (yes/no): ")
                    confirmed = text_input.strip().lower() in ["yes", "y", "confirm", "yeah", "sure"]
                except (KeyboardInterrupt, EOFError):
                    confirmed = False
        else:
            try:
                text_input = input("Confirmation (yes/no): ")
                confirmed = text_input.strip().lower() in ["yes", "y", "confirm", "yeah", "sure"]
            except (KeyboardInterrupt, EOFError):
                confirmed = False

        if confirmed:
            msg = memory_manager.clear_all()
            print(f"JARVIS: {msg}\n")
            # Update Gemini chat system instruction without memories
            new_instruction = get_system_instruction("")
            try:
                chat = client.chats.create(
                    model=getattr(chat, "_model", config.GEMINI_MODEL),
                    history=chat.get_history(),
                    config=types.GenerateContentConfig(system_instruction=new_instruction),
                )
            except Exception:
                pass
        else:
            print("JARVIS: Memory clear cancelled. Your saved memories have been kept safe.\n")

        return True, chat

    # 3. Remember command: "Remember..."
    if re.search(r"\bremember\b", cleaned_lower):
        success, response_msg = memory_manager.remember(cleaned)
        print(f"\nJARVIS: {response_msg}\n")

        if success and client is not None:
            # Synchronize active chat context with the new permanent memory
            new_instruction = get_system_instruction(memory_manager.get_context_instruction())
            try:
                chat = client.chats.create(
                    model=getattr(chat, "_model", config.GEMINI_MODEL),
                    history=chat.get_history(),
                    config=types.GenerateContentConfig(system_instruction=new_instruction),
                )
            except Exception:
                pass

        return True, chat

    # 4. Forget command: "Forget..."
    if re.search(r"\bforget\b", cleaned_lower):
        success, response_msg = memory_manager.forget(cleaned)
        print(f"\nJARVIS: {response_msg}\n")

        if success and client is not None:
            # Synchronize active chat context with updated memory
            new_instruction = get_system_instruction(memory_manager.get_context_instruction())
            try:
                chat = client.chats.create(
                    model=getattr(chat, "_model", config.GEMINI_MODEL),
                    history=chat.get_history(),
                    config=types.GenerateContentConfig(system_instruction=new_instruction),
                )
            except Exception:
                pass

        return True, chat

    # Not a memory command; pass through to Gemini
    return False, chat


def run_voice_loop(chat, client=None, memory_manager=None):
    """
    Main interactive loop for Voice Input.
    Captures microphone speech, handles memory commands, and streams Gemini responses.

    Args:
        chat: The active Gemini chat session.
        client (genai.Client, optional): The active GenAI client.
        memory_manager (MemoryManager, optional): Active memory manager.
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

            # Check for memory command
            handled, chat = handle_memory_command(
                cleaned_fallback, memory_manager, chat, client, is_voice_mode=False
            )
            if handled:
                continue

            _, chat = send_message_to_gemini(chat, cleaned_fallback, is_voice_mode=False, client=client)
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

        # Check for memory commands (remember, forget, clear, query)
        handled, chat = handle_memory_command(
            user_text, memory_manager, chat, client, is_voice_mode=True, voice_handler=voice_handler
        )
        if handled:
            continue

        # Send transcribed message to Gemini with voice mode indicator
        _, chat = send_message_to_gemini(chat, user_text, is_voice_mode=True, client=client)


def run_text_loop(chat, client=None, memory_manager=None):
    """
    Interactive loop for Text Mode.
    Accepts keyboard text, processes memory commands, and streams Gemini responses.

    Args:
        chat: The active Gemini chat session.
        client (genai.Client, optional): The active GenAI client.
        memory_manager (MemoryManager, optional): Active memory manager.
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

        # Check for memory command (remember, forget, clear, query)
        handled, chat = handle_memory_command(
            cleaned_input, memory_manager, chat, client, is_voice_mode=False
        )
        if handled:
            continue

        _, chat = send_message_to_gemini(chat, cleaned_input, is_voice_mode=False, client=client)


def main():
    """Runs the main JARVIS application."""
    # 1. Validate configuration before running
    config.validate_config()

    # Determine whether text mode was explicitly requested via flag
    use_text_mode = "--text" in sys.argv

    # 2. Show startup banner
    print_banner(voice_mode=not use_text_mode)

    # 3. Create client, load permanent memory, and initialize chat session
    try:
        memory_manager = MemoryManager()
        client, chat, memory_manager = initialize_jarvis(memory_manager=memory_manager)
    except Exception as error:
        print("JARVIS: Sorry, I couldn't connect to the AI service right now.")
        print(f"Technical error: {error}\n")
        sys.exit(1)

    # 4. Run conversation loop (Voice by default, Text mode with --text)
    if use_text_mode:
        run_text_loop(chat, client=client, memory_manager=memory_manager)
    else:
        run_voice_loop(chat, client=client, memory_manager=memory_manager)


if __name__ == "__main__":
    main()
