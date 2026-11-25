from __future__ import annotations

import shutil
from dataclasses import dataclass, field

import requests


@dataclass
class RuntimeStatus:
    stt_available: bool
    llm_available: bool
    tts_available: bool
    mic_available: bool = True
    warnings: list[str] = field(default_factory=list)


def check_local_capabilities(ollama_url: str = "http://localhost:11434") -> RuntimeStatus:
    warnings: list[str] = []

    try:
        import faster_whisper  # noqa: F401
        stt_available = True
    except Exception:
        stt_available = False
        warnings.append("faster-whisper no está instalado; el reconocimiento de voz (STT) requiere instalarlo.")

    try:
        import sounddevice as sd
        devices = sd.query_devices()
        mic_available = len(devices) > 0
    except Exception:
        mic_available = False
        warnings.append("No se detectaron dispositivos de audio activos con sounddevice.")

    tts_available = False
    try:
        import edge_tts  # noqa: F401
        if shutil.which("mpg123") or shutil.which("ffplay"):
            tts_available = True
    except Exception:
        pass
    if not tts_available:
        tts_available = bool(
            shutil.which("piper") or shutil.which("espeak-ng") or shutil.which("espeak")
        )
    if not tts_available:
        try:
            import pyttsx3  # noqa: F401
            tts_available = True
        except Exception:
            tts_available = False
            warnings.append("No se encontró motor TTS (edge-tts / piper / espeak-ng / pyttsx3).")

    try:
        resp = requests.get(f"{ollama_url.rstrip('/')}/api/tags", timeout=1.0)
        llm_available = resp.status_code == 200
        if not llm_available:
            warnings.append("Servidor Ollama no responde; se utilizará el Evaluador Semántico Local.")
    except Exception:
        llm_available = False
        warnings.append("Ollama local no está en ejecución; usando Evaluador Semántico Local integrado.")

    return RuntimeStatus(
        stt_available=stt_available,
        llm_available=llm_available,
        tts_available=tts_available,
        mic_available=mic_available,
        warnings=warnings,
    )
