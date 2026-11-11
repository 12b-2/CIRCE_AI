from __future__ import annotations

import os


class TextToSpeech:
    def __init__(self, engine_name: str = "pyttsx3") -> None:
        self.engine_name = engine_name
        self._engine = None

    def speak(self, text: str) -> None:
        if not text or not text.strip():
            return
        if self.engine_name == "pyttsx3":
            try:
                import pyttsx3
            except ImportError as exc:
                raise RuntimeError("pyttsx3 no está instalado. Instálalo con pip install -r requirements.txt") from exc

            if self._engine is None:
                self._engine = pyttsx3.init()
            self._engine.say(text)
            self._engine.runAndWait()
            return

        raise ValueError(f"Motor TTS no soportado: {self.engine_name}")
