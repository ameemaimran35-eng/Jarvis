"""
config.py - Configuration management for JARVIS (Module 1, 2 & 3)

Loads environment variables from the .env file using python-dotenv.
Reads and validates the Gemini API key, model selection, retry parameters,
and optional fallback model settings without hard-coding any secrets.
"""

import os
import sys

from dotenv import load_dotenv


# Load environment variables from the local .env file
load_dotenv()


# Read Gemini API key from environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Primary Gemini model (default: gemini-3.5-flash-lite for fast, free-tier responses)
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")

# Optional fallback model used if the primary model is temporarily unavailable or overloaded
GEMINI_FALLBACK_MODEL = os.getenv("GEMINI_FALLBACK_MODEL", "").strip()

# Maximum retry attempts for temporary API errors (429, 503, network drop)
try:
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
except ValueError:
    MAX_RETRIES = 3

# Base delay in seconds for exponential backoff retry logic
try:
    RETRY_BASE_DELAY = float(os.getenv("RETRY_BASE_DELAY", "1.5"))
except ValueError:
    RETRY_BASE_DELAY = 1.5


def validate_config():
    """
    Validates that the Gemini API key is configured.

    If the key is missing or left as the default placeholder,
    displays a clear error message and exits safely.
    """

    if (
        not GEMINI_API_KEY
        or GEMINI_API_KEY.strip() == ""
        or GEMINI_API_KEY.strip() == "YOUR_API_KEY_HERE"
        or GEMINI_API_KEY.strip() == "your_gemini_api_key_here"
    ):
        print("ERROR: Gemini API key is missing.\n")
        print("Please add your Gemini API key to the .env file.")
        sys.exit(1)
