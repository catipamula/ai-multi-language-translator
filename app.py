"""Flask entry point for AI Multi-Language Translator."""

from __future__ import annotations

import os
import logging
from flask import Flask, jsonify, render_template, request
from dotenv import load_dotenv

from database import init_db
from models import add_history, list_history
from speech import recognize_from_microphone, synthesize_speech
from translator import translate_text
from utils import LANGUAGES, language_name


def create_app() -> Flask:
    load_dotenv()
    app = Flask(__name__)
    logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
    app.config["SECRET_KEY"] = os.getenv(
        "SECRET_KEY",
        "dev-secret-key-change-me",
    )
    init_db()

    @app.route("/")
    def index():
        return render_template(
            "index.html",
            languages=LANGUAGES,
            history=list_history(8),
        )

    @app.route("/history")
    def history_page():
        return render_template(
            "history.html",
            languages=LANGUAGES,
            history=list_history(100),
        )

    # Favorites feature removed

    @app.post("/translate")
    def translate():
        payload = request.get_json(silent=True) or {}
        app.logger.info(
            "Translation request received source=%s target=%s text_length=%s",
            payload.get("source_language", "auto"),
            payload.get("target_language", "en"),
            len(payload.get("text", "")),
        )
        try:
            result = translate_text(
                payload.get("text", ""),
                payload.get("source_language", "auto"),
                payload.get("target_language", "en"),
            )
            app.logger.info(
                "Translation successful source=%s target=%s output_length=%s",
                result.source_language,
                result.target_language,
                len(result.translated_text),
            )
            history_item = add_history(
                result.original_text,
                result.translated_text,
                result.source_language,
                result.target_language,
                result.detected_language,
            )
            return jsonify(
                {
                    "success": True,
                    "translation": result.translated_text,
                    "detected_language": result.detected_language,
                    "detected_label": language_name(result.detected_language),
                    "history": history_item,
                }
            )
        except Exception as exc:
            app.logger.exception("Translation request failed: %s", exc)
            return jsonify({"success": False, "error": str(exc)}), 400

    @app.post("/speech-to-text")
    def speech_to_text():
        payload = request.get_json(silent=True) or {}
        try:
            text = recognize_from_microphone(payload.get("language", "auto"))
            return jsonify({"success": True, "text": text})
        except Exception as exc:
            return jsonify({"success": False, "error": str(exc)}), 400

    @app.post("/text-to-speech")
    def text_to_speech():
        payload = request.get_json(silent=True) or {}
        try:
            audio = synthesize_speech(
                payload.get("text", ""),
                payload.get("language", "en"),
                payload.get("voice", "female"),
            )
            return jsonify({"success": True, **audio})
        except Exception as exc:
            app.logger.exception("Text-to-speech request failed: %s", exc)
            return jsonify({"success": False, "error": str(exc)}), 400

    @app.get("/api/history")
    @app.get("/history-data")
    def history_data():
        return jsonify({"success": True, "history": list_history(50)})

    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        app.logger.exception("Unhandled exception: %s", error)
        return jsonify({"success": False, "error": "An internal server error occurred."}), 500

    # Favorite API endpoints removed

    # Download/export history feature removed

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True, threaded=True)
