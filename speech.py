"""Speech recognition and text-to-speech helpers."""

from __future__ import annotations

import base64
import tempfile
from pathlib import Path

from utils import SPEECH_RECOGNITION_CODES, validate_language


class SpeechError(RuntimeError):
    """Raised when speech input or output fails."""


def recognize_from_microphone(language: str) -> str:
    try:
        import speech_recognition as sr
    except ImportError as exc:
        raise SpeechError(
            "Install SpeechRecognition and PyAudio to use the microphone."
        ) from exc

    if language == "auto":
        language = "en"
    if not validate_language(language):
        raise ValueError("Unsupported speech recognition language.")

    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.6)
        audio = recognizer.listen(source, timeout=8, phrase_time_limit=14)

    try:
        return recognizer.recognize_google(
            audio,
            language=SPEECH_RECOGNITION_CODES.get(language, "en-US"),
        )
    except sr.UnknownValueError as exc:
        raise SpeechError("I could not understand that audio.") from exc
    except sr.RequestError as exc:
        raise SpeechError("Speech recognition service is unavailable.") from exc


def synthesize_speech(text: str, language: str, voice: str = "female") -> dict:
    cleaned = text.strip()
    if not cleaned:
        raise ValueError("Text is required for speech output.")
    if language == "auto":
        language = "en"
    if not validate_language(language):
        raise ValueError("Unsupported speech language.")

    try:
        from gtts import gTTS

        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_file:
            temp_path = Path(temp_file.name)
        try:
            gTTS(text=cleaned, lang=language, slow=False).save(str(temp_path))
            audio_bytes = temp_path.read_bytes()
        finally:
            temp_path.unlink(missing_ok=True)
        return {
            "audio": base64.b64encode(audio_bytes).decode("utf-8"),
            "mime_type": "audio/mpeg",
            "engine": "gTTS",
        }
    except Exception:
        return synthesize_offline(cleaned, voice)


def synthesize_offline(text: str, voice: str = "female") -> dict:
    try:
        import pyttsx3
    except ImportError as exc:
        raise SpeechError("Install pyttsx3 to use offline voice output.") from exc

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
        temp_path = Path(temp_file.name)

    try:
        engine = pyttsx3.init()
        voices = engine.getProperty("voices")
        selected_voice = _select_voice(voices, voice)
        if selected_voice:
            engine.setProperty("voice", selected_voice.id)
        engine.save_to_file(text, str(temp_path))
        engine.runAndWait()
        audio_bytes = temp_path.read_bytes()
    finally:
        temp_path.unlink(missing_ok=True)
    return {
        "audio": base64.b64encode(audio_bytes).decode("utf-8"),
        "mime_type": "audio/wav",
        "engine": "pyttsx3",
    }


def _select_voice(voices: list, preference: str):
    preferred = preference.lower()
    for item in voices:
        name = item.name.lower()
        if preferred in name:
            return item
    if voices:
        return voices[0]
    return None
