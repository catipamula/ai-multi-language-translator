"""Translation service with automatic fallback providers."""

from __future__ import annotations

import os
from contextlib import contextmanager
from dataclasses import dataclass

from utils import mymemory_language, validate_language


@dataclass(frozen=True)
class TranslationResult:
    original_text: str
    translated_text: str
    source_language: str
    target_language: str
    detected_language: str


class TranslationError(RuntimeError):
    """Raised when all configured translation providers fail."""


PROXY_ENV_KEYS = (
    "HTTP_PROXY",
    "HTTPS_PROXY",
    "ALL_PROXY",
    "http_proxy",
    "https_proxy",
    "all_proxy",
)


@contextmanager
def without_broken_local_proxy():
    """Disable dead local proxy values that prevent translation HTTP requests."""

    removed = {}
    for key in PROXY_ENV_KEYS:
        value = os.environ.get(key)
        if value and "127.0.0.1:9" in value:
            removed[key] = value
            os.environ.pop(key, None)
    try:
        yield
    finally:
        os.environ.update(removed)


def detect_language(text: str) -> str:
    try:
        from langdetect import DetectorFactory, detect

        DetectorFactory.seed = 0
        return detect(text)
    except Exception:
        return "unknown"


def translate_text(text: str, source: str, target: str) -> TranslationResult:
    cleaned = text.strip()
    if not cleaned:
        raise ValueError("Text is required for translation.")
    if not validate_language(source, allow_auto=True):
        raise ValueError("Unsupported source language.")
    if not validate_language(target):
        raise ValueError("Unsupported target language.")

    detected = detect_language(cleaned) if source == "auto" else source
    provider_source = "auto" if source == "auto" else source
    errors: list[str] = []

    try:
        from deep_translator import GoogleTranslator, MyMemoryTranslator
    except ImportError as exc:
        raise TranslationError(
            "Install deep-translator to enable live translation."
        ) from exc

    for provider in (
        lambda: GoogleTranslator(source=provider_source, target=target),
        lambda: MyMemoryTranslator(
            source=mymemory_language(detected if source == "auto" else source),
            target=mymemory_language(target),
        ),
    ):
        try:
            with without_broken_local_proxy():
                translated = provider().translate(cleaned)
            if not translated:
                raise TranslationError("Translation provider returned empty text.")
            return TranslationResult(
                original_text=cleaned,
                translated_text=translated,
                source_language=source,
                target_language=target,
                detected_language=detected,
            )
        except Exception as exc:
            errors.append(str(exc))

    raise TranslationError("Translation service unavailable. " + " | ".join(errors))
