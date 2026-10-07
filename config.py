
"""
config.py - Configuration management for JARVIS Module 1

Loads environment variables from the .env file using python-dotenv.
Reads and validates the Gemini API key without hard-coding any secrets.
"""

import os
import sys

from dotenv import load_dotenv


# Load environment variables from the local .env file
load_dotenv()


# Read Gemini API key from environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Gemini model to use (default: gemini-flash-lite-latest)
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-flash-lite-latest")


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

