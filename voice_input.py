"""
voice_input.py - Voice input module for JARVIS (Module 2)

Captures voice input from the user's microphone and converts it
to text using the SpeechRecognition library and Google Speech Recognition.
Handles microphone hardware errors and speech recognition exceptions gracefully.
"""

import sys
import speech_recognition as sr


class VoiceInputHandler:
    """
    Manages microphone configuration, ambient noise calibration,
    and speech-to-text conversion.
    """

    def __init__(self):
        """Initializes the SpeechRecognition Recognizer."""
        self.recognizer = sr.Recognizer()
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
        self.microphone = None
        self._calibrated = False

    def _get_microphone(self):
        """
        Initializes and returns the microphone instance.
        Performs initial ambient noise calibration if not already done.
        """
        if self.microphone is None:
            self.microphone = sr.Microphone()

        if not self._calibrated:
            try:
                with self.microphone as source:
                    # Quick calibration for background noise
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                self._calibrated = True
            except Exception:
                # If initial calibration encounters an issue, proceed to listen
                pass

        return self.microphone

    def listen(self, timeout=None, phrase_time_limit=None):
        """
        Listens to the microphone and converts captured speech to text.

        Returns:
            str or None: The recognized text string if successful,
                         or None if speech could not be understood.

        Raises:
            Exception: If a microphone or hardware error occurs.
        """
        mic = self._get_microphone()

        with mic as source:
            print("🎤 Listening...")
            sys.stdout.flush()
            audio = self.recognizer.listen(
                source,
                timeout=timeout,
                phrase_time_limit=phrase_time_limit,
            )

        try:
            recognized_text = self.recognizer.recognize_google(audio)
            return recognized_text.strip()
        except sr.UnknownValueError:
            print("JARVIS: Sorry, I couldn't understand that. Please try again.\n")
            return None
        except sr.RequestError as error:
            print(f"JARVIS: Speech recognition service error: {error}\n")
            return None


def capture_voice_input(voice_handler=None, timeout=None, phrase_time_limit=None):
    """
    Safely captures voice input from the microphone.

    Catches speech recognition exceptions and microphone errors
    so the application does not crash.

    Args:
        voice_handler (VoiceInputHandler, optional): Existing handler instance.
        timeout (float, optional): Maximum seconds to wait for speech to start.
        phrase_time_limit (float, optional): Maximum seconds for the phrase.

    Returns:
        tuple: (text, error_occurred)
            - text (str or None): The recognized text if successful.
            - error_occurred (bool): True if a microphone/hardware error occurred.
    """
    if voice_handler is None:
        voice_handler = VoiceInputHandler()

    try:
        text = voice_handler.listen(timeout=timeout, phrase_time_limit=phrase_time_limit)
        return text, False
    except sr.WaitTimeoutError:
        print("JARVIS: Listening timed out. Please try speaking again.\n")
        return None, False
    except KeyboardInterrupt:
        raise
    except Exception as error:
        print(f"JARVIS: Microphone error: {error}")
        print("Please check your microphone connection and permissions.\n")
        return None, True
