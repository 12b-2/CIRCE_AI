from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class RuntimeStatus:
    stt_available: bool
    llm_available: bool
    tts_available: bool
    warnings: list[str] = None

    def __post_init__(self) -> None:
        if self.warnings is None:
            self.warnings = []


def check_local_capabilities() -> RuntimeStatus:
    warnings: list[str] = []

    try:
        import faster_whisper  # noqa: F401
        stt_available = True
    except Exception:
        stt_available = False
        warnings.append("faster-whisper no está disponible; el STT puede fallar si no se instala.")

    try:
        import requests  # noqa: F401
        stt_available = stt_available and True
    except Exception:
        warnings.append("requests no está disponible.")

    try:
        import pyttsx3  # noqa: F401
        tts_available = True
    except Exception:
        tts_available = False
        warnings.append("pyttsx3 no está disponible; la salida por voz puede fallar.")

    try:
        import ollama  # noqa: F401
        llm_available = True
    except Exception:
        llm_available = False
        warnings.append("Ollama no está instalado o no está disponible; el LLM local no podrá responder.")

    return RuntimeStatus(
        stt_available=stt_available,
        llm_available=llm_available,
        tts_available=tts_available,
        warnings=warnings,
    )
