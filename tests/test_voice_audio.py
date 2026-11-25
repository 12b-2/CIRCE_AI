from __future__ import annotations

import ast
import asyncio
import os
import tempfile
import wave

import numpy as np

from circe_app.audio.stt import SpeechToText, load_wav_as_float32
from circe_app.audio.tts import (
    DEFAULT_NEURAL_VOICE,
    SPANISH_NEURAL_VOICES,
    TextToSpeech,
    clean_text_for_speech,
)


def test_clean_text_for_speech_removes_ui_symbols() -> None:
    raw = "✓ ¡Decisión Correcta! · +20 XP ⚡ ❤ **Aíslo el servidor** ➔"
    cleaned = clean_text_for_speech(raw)
    assert "·" not in cleaned
    assert " ." not in cleaned
    assert "⚡" not in cleaned
    assert "**" not in cleaned
    assert "Aíslo el servidor" in cleaned
    assert "vidas" in cleaned


def test_tts_retries_edge_before_falling_back(monkeypatch, tmp_path) -> None:
    tts = TextToSpeech(engine_name="auto", cache_dir=str(tmp_path))
    attempts = {"count": 0}
    espeak_called: list[str] = []

    def fake_once(gen, text, voice, edge_rate, stdin_cmd, cache_path):
        attempts["count"] += 1
        return (attempts["count"] >= 2, False)

    monkeypatch.setattr(tts, "_resolve_backend", lambda: "edge-tts")
    monkeypatch.setattr(tts, "_speak_edge_tts_once", fake_once)
    monkeypatch.setattr(
        tts,
        "_speak_espeak",
        lambda gen, text, backend: espeak_called.append(text),
    )

    tts.speak("Nivel 1. Detección y contención.", blocking=True)
    assert attempts["count"] == 2
    assert espeak_called == []


def test_tts_default_neural_voice_and_rate() -> None:
    tts = TextToSpeech(engine_name="auto")
    assert tts.voice == DEFAULT_NEURAL_VOICE
    assert tts._edge_rate_str() == "+0%"
    tts.rate = 198
    assert tts._edge_rate_str() == "+20%"
    tts.set_voice("es-ES-ElviraNeural")
    assert tts.voice == "es-ES-ElviraNeural"
    assert "Elvira" in tts.get_voice_display_name()
    assert len(SPANISH_NEURAL_VOICES) >= 4


def test_tts_auto_fallback_when_edge_fails(monkeypatch) -> None:
    called: list[str] = []
    tts = TextToSpeech(engine_name="auto")

    monkeypatch.setattr(tts, "_resolve_backend", lambda: "edge-tts")
    monkeypatch.setattr(tts, "_speak_edge_tts", lambda gen, text: False)
    monkeypatch.setattr(tts, "_speak_piper", lambda gen, text: False)
    monkeypatch.setattr(
        tts,
        "_speak_espeak",
        lambda gen, text, backend: called.append(f"{backend}:{text}"),
    )

    tts.speak("Probando respaldo offline.", blocking=True)
    assert len(called) == 1
    assert "Probando respaldo offline." in called[0]
    assert not tts.is_speaking


def test_load_wav_as_float32_resamples_without_pyav() -> None:
    tmp_wav = os.path.join(tempfile.gettempdir(), "test_circe_resample_44k.wav")
    sr = 44100
    t = np.linspace(0, 0.5, int(sr * 0.5), endpoint=False)
    mono = (0.3 * np.sin(2 * np.pi * 440 * t)).astype(np.float32)
    stereo = np.stack([mono, mono], axis=1)
    pcm16 = (np.clip(stereo, -1.0, 1.0) * 32767).astype(np.int16)

    with wave.open(tmp_wav, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(pcm16.tobytes())

    try:
        audio = load_wav_as_float32(tmp_wav, target_sr=16000)
        assert audio.dtype == np.float32
        assert audio.ndim == 1
        assert 7900 <= len(audio) <= 8100
    finally:
        if os.path.exists(tmp_wav):
            os.remove(tmp_wav)


def test_stt_transcribe_wav_and_numpy_without_pyav_error() -> None:
    stt = SpeechToText(model="tiny", sample_rate=16000, language="es")
    tmp_wav = os.path.join(tempfile.gettempdir(), "test_circe_stt_silence.wav")
    # Silencio y tono breve: no debe fallar con TypeError de PyAV metadata_errors
    silence = np.zeros(16000, dtype=np.float32)
    SpeechToText.save_wav(tmp_wav, silence, sample_rate=16000)
    try:
        res_path = asyncio.run(stt.transcribe(audio_path=tmp_wav))
        assert res_path == ""

        tone = (0.05 * np.sin(np.linspace(0, 2 * np.pi * 300, 16000))).astype(np.float32)
        SpeechToText.save_wav(tmp_wav, tone, sample_rate=16000)
        res_tone = asyncio.run(stt.transcribe(audio_path=tmp_wav))
        assert isinstance(res_tone, str)

        res_mem = asyncio.run(stt.transcribe(audio_data=tone))
        assert isinstance(res_mem, str)
    finally:
        if os.path.exists(tmp_wav):
            os.remove(tmp_wav)


def test_gui_except_lambdas_bind_exception_variable() -> None:
    """Garantiza que ningún lambda dentro de except capture la variable exc sin valor por defecto."""
    gui_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "circe_app", "ui", "gui_app.py"
    )
    with open(gui_path, "r", encoding="utf-8") as fh:
        tree = ast.parse(fh.read(), filename=gui_path)

    for node in ast.walk(tree):
        if isinstance(node, ast.ExceptHandler) and node.name:
            exc_name = node.name
            for sub in ast.walk(node):
                if isinstance(sub, ast.Lambda):
                    param_names = {a.arg for a in sub.args.args}
                    for inner in ast.walk(sub.body):
                        if isinstance(inner, ast.Name) and inner.id == exc_name:
                            assert exc_name in param_names, (
                                f"Lambda en línea {sub.lineno} usa '{exc_name}' sin vincularlo por defecto"
                            )
