from __future__ import annotations

import asyncio
from math import gcd
import os
import tempfile
import threading
import wave
from typing import Callable

import numpy as np


CYBERSEC_SPANISH_PROMPT = (
    "Circe, ciberseguridad, incidente, aislar el servidor, desconectar de la red, "
    "preservar evidencia forense, logs, phishing, ransomware, firewall, credenciales, "
    "tokens, respaldo, backup, SOC, CSIRT."
)

_MODEL_CACHE: dict[str, object] = {}
_GLOBAL_MODEL_LOCK = threading.Lock()


def _resample_audio(audio: np.ndarray, orig_sr: int, target_sr: int) -> np.ndarray:
    if orig_sr == target_sr or audio.size == 0:
        return audio.astype(np.float32, copy=False)
    from scipy.signal import resample_poly

    divisor = gcd(int(orig_sr), int(target_sr))
    up = int(target_sr) // divisor
    down = int(orig_sr) // divisor
    return resample_poly(audio.astype(np.float32, copy=False), up, down).astype(np.float32)


def load_wav_as_float32(audio_path: str, target_sr: int = 16000) -> np.ndarray:
    """Lee un archivo WAV PCM a un arreglo float32 mono a target_sr Hz sin depender de PyAV."""
    with wave.open(audio_path, "rb") as wf:
        channels = wf.getnchannels()
        sampwidth = wf.getsampwidth()
        framerate = wf.getframerate()
        nframes = wf.getnframes()
        raw = wf.readframes(nframes)

    if not raw:
        return np.zeros(0, dtype=np.float32)

    if sampwidth == 1:
        audio = (np.frombuffer(raw, dtype=np.uint8).astype(np.float32) - 128.0) / 128.0
    elif sampwidth == 2:
        audio = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    elif sampwidth == 4:
        audio = np.frombuffer(raw, dtype=np.int32).astype(np.float32) / 2147483648.0
    else:
        raise ValueError(f"Ancho de muestra WAV no soportado: {sampwidth} bytes.")

    if channels > 1:
        audio = audio.reshape(-1, channels).mean(axis=1)

    return _resample_audio(audio, framerate, target_sr)


class SpeechToText:
    """Motor de reconocimiento de voz (STT) modular con soporte para:
    - Grabación interactiva Start/Stop en tiempo real con medición de nivel RMS (sounddevice)
    - Grabación por duración fija para consola
    - Transcripción local rápida con faster-whisper (Whisper CTranslate2 int8),
      cargando audio WAV/numpy directamente sin depender de PyAV.
    """

    def __init__(self, model: str = "tiny", sample_rate: int = 16000, language: str = "es") -> None:
        self.model = model
        self.sample_rate = sample_rate
        self.language = language
        self._backend = None
        self._model_lock = threading.Lock()
        self._recording = False
        self._stream = None
        self._stream_sample_rate = sample_rate
        self._frames: list[np.ndarray] = []
        self._last_audio: np.ndarray | None = None
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
        with _GLOBAL_MODEL_LOCK:
            cached = _MODEL_CACHE.get(self.model)
            if cached is not None:
                self._backend = cached
                return self._backend
            try:
                from faster_whisper import WhisperModel
            except ImportError as exc:
                raise RuntimeError(
                    "faster-whisper no está instalado. Instálalo con: pip install -r requirements.txt"
                ) from exc

            cpu_threads = min(4, os.cpu_count() or 4)
            # Cargar primero desde caché local para evitar latencia de red en cada arranque
            try:
                backend = WhisperModel(
                    self.model,
                    device="cpu",
                    compute_type="int8",
                    cpu_threads=cpu_threads,
                    local_files_only=True,
                )
            except Exception:
                backend = WhisperModel(
                    self.model,
                    device="cpu",
                    compute_type="int8",
                    cpu_threads=cpu_threads,
                )
            _MODEL_CACHE[self.model] = backend
            self._backend = backend
            return self._backend

    def warm_up(self) -> bool:
        """Precarga el modelo Whisper en segundo plano para transcripción instantánea."""
        try:
            self._get_whisper_model()
            return True
        except Exception:
            return False

    @staticmethod
    def save_wav(output_path: str, audio_data: np.ndarray, sample_rate: int = 16000) -> str:
        """Guarda un arreglo numpy float32 (-1.0 a 1.0) como archivo WAV mono PCM 16-bit válido."""
        clipped = np.clip(audio_data, -1.0, 1.0)
        pcm16 = (clipped * 32767).astype(np.int16)
        with wave.open(output_path, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)  # 2 bytes = 16-bit PCM
            wf.setframerate(sample_rate)
            wf.writeframes(pcm16.tobytes())
        return output_path

    def _transcribe_array_sync(self, audio: np.ndarray) -> str:
        if audio.size == 0:
            return ""
        audio_f32 = np.ascontiguousarray(audio, dtype=np.float32)
        rms = float(np.sqrt(np.mean(audio_f32**2)))
        if rms < 1e-4:
            return ""

        model = self._get_whisper_model()
        segments, _ = model.transcribe(
            audio_f32,
            language=self.language,
            beam_size=1,
            vad_filter=True,
            condition_on_previous_text=False,
            initial_prompt=CYBERSEC_SPANISH_PROMPT,
        )
        transcript = " ".join(segment.text for segment in segments).strip()

        # Si el filtro VAD descartó todo pero hubo señal de voz (micrófono bajo), reintentar sin VAD
        if not transcript and rms >= 0.0025:
            segments, _ = model.transcribe(
                audio_f32,
                language=self.language,
                beam_size=1,
                vad_filter=False,
                condition_on_previous_text=False,
                initial_prompt=CYBERSEC_SPANISH_PROMPT,
            )
            transcript = " ".join(segment.text for segment in segments).strip()

        return transcript

    async def transcribe(
        self,
        audio_path: str | None = None,
        text: str | None = None,
        audio_data: np.ndarray | None = None,
    ) -> str:
        if text is not None:
            return text.strip()

        if audio_data is not None:
            return await asyncio.to_thread(self._transcribe_array_sync, audio_data)

        if audio_path is None or not os.path.exists(audio_path):
            raise ValueError("Debe indicar un audio_path válido, audio_data o un texto de prueba.")

        audio = await asyncio.to_thread(load_wav_as_float32, audio_path, self.sample_rate)
        return await asyncio.to_thread(self._transcribe_array_sync, audio)

    def start_stream_recording(self, on_level: Callable[[float], None] | None = None) -> None:
        """Inicia la captura de micrófono de forma no bloqueante hasta que se llame stop_stream_recording()."""
        import sounddevice as sd

        if self._recording:
            return

        with self._lock:
            self._frames = []
            self._last_audio = None
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

        try:
            self._stream_sample_rate = self.sample_rate
            self._stream = sd.InputStream(
                samplerate=self.sample_rate,
                channels=1,
                dtype="float32",
                callback=_callback,
            )
            self._stream.start()
        except Exception:
            # Algunos micrófonos/ALSA solo admiten su tasa nativa (ej. 44100/48000 Hz)
            try:
                dev = sd.query_devices(kind="input")
                native_sr = int(dev.get("default_samplerate", 44100))
                self._stream_sample_rate = native_sr
                self._stream = sd.InputStream(
                    samplerate=native_sr,
                    channels=1,
                    dtype="float32",
                    callback=_callback,
                )
                self._stream.start()
            except Exception:
                with self._lock:
                    self._recording = False
                    self._stream = None
                raise

    def stop_stream_recording(self, output_path: str | None = None) -> str:
        """Detiene la grabación interactiva y devuelve la ruta del archivo WAV generado."""
        with self._lock:
            self._recording = False
            stream = self._stream
            self._stream = None
            frames = list(self._frames)
            self._frames = []
            self._current_rms = 0.0
            captured_sr = self._stream_sample_rate

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
            if captured_sr != self.sample_rate:
                audio = _resample_audio(audio, captured_sr, self.sample_rate)

        self._last_audio = audio

        if output_path is None:
            output_path = os.path.join(tempfile.gettempdir(), "circe_voice_capture.wav")

        return self.save_wav(output_path, audio, self.sample_rate)

    @property
    def last_recorded_audio(self) -> np.ndarray | None:
        return self._last_audio

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
        audio = recording.reshape(-1)
        self.save_wav(output_path, audio, self.sample_rate)
        if os.path.exists(output_path):
            return await self.transcribe(audio_data=audio)
        raise RuntimeError("No se pudo guardar la grabación.")
