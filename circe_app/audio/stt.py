from __future__ import annotations

import os
from typing import Any


class SpeechToText:
    def __init__(self, model: str = "tiny") -> None:
        self.model = model
        self._backend = None

    async def transcribe(self, audio_path: str | None = None, text: str | None = None) -> str:
        if text is not None:
            return text

        if audio_path is None:
            raise ValueError("Debe indicar un audio_path o un texto de prueba.")

        try:
            from faster_whisper import WhisperModel
        except ImportError as exc:
            raise RuntimeError("faster-whisper no está instalado. Instálalo con pip install -r requirements.txt") from exc

        if self._backend is None:
            self._backend = WhisperModel(self.model, device="cpu", compute_type="int8")

        segments, _ = self._backend.transcribe(audio_path, language="es")
        return " ".join(segment.text for segment in segments).strip()

    async def capture_microphone(self) -> str:
        import sounddevice as sd
        import wave

        sample_rate = 16000
        duration_seconds = 8
        output_path = "tmp_capture.wav"

        recording = sd.rec(
            int(duration_seconds * sample_rate),
            samplerate=sample_rate,
            channels=1,
            dtype="float32",
        )
        sd.wait()

        wf = wave.open(output_path, "wb")
        wf.setnchannels(1)
        wf.setsampwidth(4)
        wf.setframerate(sample_rate)
        wf.writeframes((recording * 32767).astype("int16").tobytes())
        wf.close()

        if os.path.exists(output_path):
            return await self.transcribe(audio_path=output_path)
        raise RuntimeError("No se pudo guardar la grabación.")
