"""Shared constants and response helpers."""

from __future__ import annotations

LANGUAGES = {
    "auto": "Auto Detect",
    "en": "English",
    "te": "Telugu",
    "hi": "Hindi",
    "ta": "Tamil",
    "kn": "Kannada",
    "ml": "Malayalam",
    "mr": "Marathi",
    "bn": "Bengali",
    "ur": "Urdu",
    "fr": "French",
}

SPEECH_RECOGNITION_CODES = {
    "en": "en-US",
    "te": "te-IN",
    "hi": "hi-IN",
    "ta": "ta-IN",
    "kn": "kn-IN",
    "ml": "ml-IN",
    "mr": "mr-IN",
    "bn": "bn-IN",
    "ur": "ur-PK",
    "fr": "fr-FR",
}

MYMEMORY_LANGUAGES = {
    "en": "english",
    "te": "telugu",
    "hi": "hindi",
    "ta": "tamil india",
    "kn": "kannada",
    "ml": "malayalam",
    "mr": "marathi",
    "bn": "bengali",
    "ur": "urdu",
    "fr": "french",
}


def language_name(code: str | None) -> str:
    if not code:
        return "Unknown"
    return LANGUAGES.get(code, code.upper())


def validate_language(code: str, allow_auto: bool = False) -> bool:
    if code == "auto":
        return allow_auto
    return code in LANGUAGES and code != "auto"


def mymemory_language(code: str) -> str:
    return MYMEMORY_LANGUAGES.get(code, language_name(code).lower())

