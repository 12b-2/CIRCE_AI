from __future__ import annotations

import os
import tempfile
import threading
import wave
from typing import Callable

import numpy as np


class SpeechToText:
    """Motor de reconocimiento de voz (STT) modular con soporte para:
    - Grabación interactiva Start/Stop en tiempo real con medición de nivel RMS (sounddevice)
    - Grabación por duración fija para consola
    - Transcripción local con faster-whisper (Whisper CTranslate2 int8)
    """

    def __init__(self, model: str = "tiny", sample_rate: int = 16000, language: str = "es") -> None:
        self.model = model
        self.sample_rate = sample_rate
        self.language = language
        self._backend = None
        self._recording = False
        self._stream = None
        self._frames: list[np.ndarray] = []
        self._current_rms: float = 0.0
        self._lock = threading.Lock()

    @property
    def is_recording(self) -> bool:
        return self._recording

    @property
    def current_level(self) -> float:
        """Nivel normalizado (0.0 a 1.0) del micrófono en tiempo real."""
        return min(1.0, self._current_rms * 8.0)

    def _get_whisper_model(self):
        if self._backend is not None:
            return self._backend
        try:
            from faster_whisper import WhisperModel
        except ImportError as exc:
            raise RuntimeError(
                "faster-whisper no está instalado. Instálalo con: pip install -r requirements.txt"
            ) from exc

        try:
            self._backend = WhisperModel(self.model, device="cpu", compute_type="int8")
        except Exception:
            # Intentar cargar únicamente desde caché local si no hay red disponible
            self._backend = WhisperModel(
                self.model,
                device="cpu",
                compute_type="int8",
                local_files_only=True,
            )
        return self._backend

    @staticmethod
    def save_wav(output_path: str, audio_data: np.ndarray, sample_rate: int = 16000) -> str:
        """Guarda un arreglo numpy float32 (-1.0 a 1.0) como archivo WAV mono PCM 16-bit válido."""
        clipped = np.clip(audio_data, -1.0, 1.0)
        pcm16 = (clipped * 32767).astype(np.int16)
        with wave.open(output_path, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)  # 2 bytes = 16-bit PCM (corrige bug previo de sampwidth=4)
            wf.setframerate(sample_rate)
            wf.writeframes(pcm16.tobytes())
        return output_path

    async def transcribe(self, audio_path: str | None = None, text: str | None = None) -> str:
        if text is not None:
            return text.strip()

        if audio_path is None or not os.path.exists(audio_path):
            raise ValueError("Debe indicar un audio_path válido o un texto de prueba.")

        model = self._get_whisper_model()
        segments, _ = model.transcribe(
            audio_path,
            language=self.language,
            beam_size=3,
            vad_filter=True,
        )
        transcript = " ".join(segment.text for segment in segments).strip()
        return transcript

    def start_stream_recording(self, on_level: Callable[[float], None] | None = None) -> None:
        """Inicia la captura de micrófono de forma no bloqueante hasta que se llame stop_stream_recording()."""
        import sounddevice as sd

        if self._recording:
            return

        with self._lock:
            self._frames = []
            self._current_rms = 0.0
            self._recording = True

        def _callback(indata: np.ndarray, frames: int, time_info, status) -> None:
            if not self._recording:
                return
            chunk = indata.copy().reshape(-1)
            rms = float(np.sqrt(np.mean(chunk**2))) if chunk.size > 0 else 0.0
            self._current_rms = rms
            self._frames.append(chunk)
            if on_level is not None:
                try:
                    on_level(self.current_level)
                except Exception:
                    pass

        self._stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            dtype="float32",
            callback=_callback,
        )
        self._stream.start()

    def stop_stream_recording(self, output_path: str | None = None) -> str:
        """Detiene la grabación interactiva y devuelve la ruta del archivo WAV generado."""
        with self._lock:
            self._recording = False
            stream = self._stream
            self._stream = None
            frames = list(self._frames)
            self._frames = []
            self._current_rms = 0.0

        if stream is not None:
            try:
                stream.stop()
                stream.close()
            except Exception:
                pass

        if not frames:
            audio = np.zeros(int(self.sample_rate * 0.5), dtype=np.float32)
        else:
            audio = np.concatenate(frames, axis=0)

        if output_path is None:
            output_path = os.path.join(tempfile.gettempdir(), "circe_voice_capture.wav")

        return self.save_wav(output_path, audio, self.sample_rate)

    async def capture_microphone(self, duration_seconds: int = 6) -> str:
        """Captura audio durante un número fijo de segundos y devuelve la transcripción."""
        import sounddevice as sd

        output_path = os.path.join(tempfile.gettempdir(), "circe_tmp_capture.wav")
        recording = sd.rec(
            int(duration_seconds * self.sample_rate),
            samplerate=self.sample_rate,
            channels=1,
            dtype="float32",
        )
        sd.wait()
        self.save_wav(output_path, recording.reshape(-1), self.sample_rate)
        if os.path.exists(output_path):
            return await self.transcribe(audio_path=output_path)
        raise RuntimeError("No se pudo guardar la grabación.")
