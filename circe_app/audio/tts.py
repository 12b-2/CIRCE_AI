from __future__ import annotations

import asyncio
import hashlib
import os
import re
import shutil
import subprocess
import tempfile
import threading
import time
from typing import Callable


SPANISH_NEURAL_VOICES: list[tuple[str, str]] = [
    ("es-MX-DaliaNeural", "Dalia · México (Femenina)"),
    ("es-CO-SalomeNeural", "Salomé · Colombia (Femenina)"),
    ("es-ES-ElviraNeural", "Elvira · España (Femenina)"),
    ("es-AR-ElenaNeural", "Elena · Argentina (Femenina)"),
    ("es-MX-JorgeNeural", "Jorge · México (Masculina)"),
]

DEFAULT_NEURAL_VOICE = "es-MX-DaliaNeural"

# Lock global para evitar carreras en la calibración DRM.clock_skew_seconds de edge-tts
_EDGE_SYNTH_LOCK = threading.Lock()


def _has_edge_tts() -> bool:
    try:
        import edge_tts  # noqa: F401
        return True
    except Exception:
        return False


def _find_mp3_player() -> tuple[str, list[str], list[str]] | None:
    """Devuelve (nombre, cmd_archivo, cmd_stdin) para reproducir MP3 con baja latencia."""
    mpg123 = shutil.which("mpg123")
    if mpg123:
        return ("mpg123", [mpg123, "-q"], [mpg123, "-q", "-"])
    ffplay = shutil.which("ffplay")
    if ffplay:
        return (
            "ffplay",
            [ffplay, "-nodisp", "-autoexit", "-loglevel", "quiet"],
            [ffplay, "-nodisp", "-autoexit", "-loglevel", "quiet", "-i", "pipe:0"],
        )
    return None


def _find_piper_model() -> str | None:
    env_model = os.getenv("CIRCE_PIPER_MODEL", "").strip()
    if env_model and os.path.isfile(env_model):
        return env_model
    search_dirs = [
        os.path.join(os.path.expanduser("~"), ".local", "share", "piper"),
        os.path.join(os.path.expanduser("~"), ".cache", "piper"),
    ]
    for folder in search_dirs:
        if os.path.isdir(folder):
            for fname in sorted(os.listdir(folder)):
                if fname.endswith(".onnx") and fname.startswith("es"):
                    return os.path.join(folder, fname)
    return None


def clean_text_for_speech(text: str) -> str:
    """Normaliza símbolos, emojis y formato markdown para una locución natural en español."""
    if not text:
        return ""
    cleaned = (
        text.replace("·", ". ")
        .replace("⚡", "")
        .replace("❤", "vidas ")
        .replace("➔", "")
        .replace("✓", "")
        .replace("✗", "")
        .replace("◔", "")
        .replace("🎙", "")
        .replace("🔊", "")
        .replace("🔇", "")
        .replace("⚠", "")
        .replace("✨", "")
        .replace("**", "")
        .replace("__", "")
        .replace("`", "")
    )
    cleaned = re.sub(r"\s+", " ", cleaned)
    cleaned = re.sub(r"\s+([.,;:!?])", r"\1", cleaned)
    cleaned = re.sub(r"\.{2,}", ".", cleaned)
    return cleaned.strip()


class TextToSpeech:
    """Motor de síntesis de voz (TTS) modular, humanizado y no bloqueante en español.

    Prioridad en modo 'auto':
      1. edge-tts (voces neuronales en español de alta naturalidad, con streaming y caché en disco)
      2. piper (modelo neuronal local offline si está instalado)
      3. espeak-ng / espeak / pyttsx3 (respaldo offline garantizado)
    """

    def __init__(
        self,
        engine_name: str = "auto",
        rate: int = 165,
        voice: str = DEFAULT_NEURAL_VOICE,
        cache_dir: str | None = None,
    ) -> None:
        self.engine_name = engine_name
        self.rate = rate
        self.voice = voice or DEFAULT_NEURAL_VOICE
        self.enabled: bool = True
        self._engine = None
        self._active_proc: subprocess.Popen | None = None
        self._lock = threading.Lock()
        self._is_speaking = False
        self._generation = 0
        self._last_backend: str = ""
        self._cache_dir = cache_dir or self._init_cache_dir()

    @staticmethod
    def _init_cache_dir() -> str:
        preferred = os.path.join(os.path.expanduser("~"), ".cache", "circe_tts")
        try:
            os.makedirs(preferred, exist_ok=True)
            return preferred
        except OSError:
            fallback = os.path.join(tempfile.gettempdir(), "circe_tts_cache")
            os.makedirs(fallback, exist_ok=True)
            return fallback

    @property
    def is_speaking(self) -> bool:
        return self._is_speaking

    @property
    def last_backend(self) -> str:
        return self._last_backend or self._resolve_backend()

    def set_voice(self, voice: str) -> None:
        if voice and voice.strip():
            self.voice = voice.strip()

    def get_voice_display_name(self) -> str:
        for vid, label in SPANISH_NEURAL_VOICES:
            if vid == self.voice:
                return label
        return self.voice

    def _edge_voice_name(self) -> str:
        if "Neural" in self.voice:
            return self.voice
        return DEFAULT_NEURAL_VOICE

    def _edge_rate_str(self) -> str:
        pct = int(round(((self.rate - 165) / 165.0) * 100))
        pct = max(-35, min(50, pct))
        return f"{pct:+d}%"

    def _espeak_voice_name(self) -> str:
        if "Neural" in self.voice or not self.voice:
            return "es-419+f3"
        return self.voice

    def _cache_path_for(self, clean_text: str, voice: str, edge_rate: str) -> str:
        digest = hashlib.sha256(f"{voice}|{edge_rate}|{clean_text}".encode("utf-8")).hexdigest()[:24]
        return os.path.join(self._cache_dir, f"{digest}.mp3")

    def _resolve_backend(self) -> str:
        if self.engine_name == "auto":
            if _has_edge_tts() and _find_mp3_player() is not None:
                return "edge-tts"
            if shutil.which("piper") and _find_piper_model():
                return "piper"
            if shutil.which("espeak-ng"):
                return "espeak-ng"
            if shutil.which("espeak"):
                return "espeak"
            return "pyttsx3"
        if self.engine_name == "pyttsx3" and shutil.which("espeak-ng"):
            return "espeak-ng"
        return self.engine_name

    def _is_cancelled(self, gen: int) -> bool:
        with self._lock:
            return gen != self._generation

    def _terminate_proc(self, proc: subprocess.Popen | None) -> None:
        if proc is None:
            return
        if proc.poll() is None:
            try:
                proc.terminate()
                proc.wait(timeout=0.4)
            except Exception:
                try:
                    proc.kill()
                except Exception:
                    pass

    def stop(self) -> None:
        """Detiene inmediatamente cualquier locución o streaming activo."""
        with self._lock:
            self._generation += 1
            proc = self._active_proc
            self._active_proc = None
            self._is_speaking = False
        self._terminate_proc(proc)

    def prefetch(self, text: str) -> None:
        """Pre-genera audio en caché en segundo plano sin competir con la locución activa."""
        if not self.enabled or not text or not text.strip():
            return
        if self._resolve_backend() != "edge-tts":
            return
        clean_text = clean_text_for_speech(text)
        if not clean_text:
            return
        voice = self._edge_voice_name()
        edge_rate = self._edge_rate_str()
        cache_path = self._cache_path_for(clean_text, voice, edge_rate)
        if os.path.isfile(cache_path) and os.path.getsize(cache_path) > 0:
            return

        def _worker() -> None:
            # No bloquear ni competir con una locución activa: esperar si otro hilo sintetiza
            if not _EDGE_SYNTH_LOCK.acquire(timeout=15.0):
                return
            part_path = f"{cache_path}.{threading.get_ident()}.part"
            try:
                if os.path.isfile(cache_path) and os.path.getsize(cache_path) > 0:
                    return
                import edge_tts

                async def _dl() -> None:
                    comm = edge_tts.Communicate(clean_text, voice=voice, rate=edge_rate)
                    with open(part_path, "wb") as fh:
                        async for chunk in comm.stream():
                            if chunk.get("type") == "audio":
                                fh.write(chunk["data"])

                asyncio.run(asyncio.wait_for(_dl(), timeout=15.0))
                if os.path.isfile(part_path) and os.path.getsize(part_path) > 0:
                    os.replace(part_path, cache_path)
            except Exception:
                try:
                    if os.path.exists(part_path):
                        os.remove(part_path)
                except OSError:
                    pass
            finally:
                _EDGE_SYNTH_LOCK.release()

        threading.Thread(target=_worker, daemon=True).start()

    def speak(
        self,
        text: str,
        blocking: bool = False,
        on_done: Callable[[], None] | None = None,
    ) -> None:
        """Sintetiza el texto en voz alta en español.
        Por defecto se ejecuta en un hilo en segundo plano para no bloquear la GUI.
        """
        if not self.enabled or not text or not text.strip():
            if on_done:
                on_done()
            return

        clean_text = clean_text_for_speech(text)
        if not clean_text:
            if on_done:
                on_done()
            return

        with self._lock:
            self._generation += 1
            gen = self._generation
            prev_proc = self._active_proc
            self._active_proc = None
            self._is_speaking = True
        self._terminate_proc(prev_proc)

        if blocking:
            self._speak_worker(gen, clean_text, on_done)
        else:
            thread = threading.Thread(
                target=self._speak_worker,
                args=(gen, clean_text, on_done),
                daemon=True,
            )
            thread.start()

    def _speak_worker(
        self,
        gen: int,
        text: str,
        on_done: Callable[[], None] | None = None,
    ) -> None:
        backend = self._resolve_backend()
        try:
            if self._is_cancelled(gen):
                return

            if backend == "edge-tts":
                ok = self._speak_edge_tts(gen, text)
                if ok or self._is_cancelled(gen):
                    return
                if self.engine_name == "auto":
                    # Respaldo automático offline si no hay red o el servicio falló tras reintentar
                    if shutil.which("piper") and _find_piper_model():
                        if self._speak_piper(gen, text) or self._is_cancelled(gen):
                            return
                    if shutil.which("espeak-ng"):
                        self._speak_espeak(gen, text, "espeak-ng")
                        return
                    if shutil.which("espeak"):
                        self._speak_espeak(gen, text, "espeak")
                        return
                    self._speak_pyttsx3(text)
                return

            if backend == "piper":
                if self._speak_piper(gen, text) or self._is_cancelled(gen):
                    return
                if self.engine_name == "auto" and shutil.which("espeak-ng"):
                    self._speak_espeak(gen, text, "espeak-ng")
                return

            if backend in ("espeak-ng", "espeak"):
                self._speak_espeak(gen, text, backend)
                return

            if backend == "pyttsx3":
                self._speak_pyttsx3(text)
                return

            raise ValueError(f"Motor TTS no soportado: {self.engine_name}")
        except Exception:
            pass
        finally:
            with self._lock:
                if gen == self._generation:
                    self._is_speaking = False
            if on_done and not self._is_cancelled(gen):
                try:
                    on_done()
                except Exception:
                    pass

    def _register_proc(self, gen: int, proc: subprocess.Popen) -> bool:
        with self._lock:
            if gen != self._generation:
                self._terminate_proc(proc)
                return False
            self._active_proc = proc
            return True

    def _play_cached_mp3(self, gen: int, file_cmd: list[str], cache_path: str) -> bool:
        if self._is_cancelled(gen):
            return True
        proc = subprocess.Popen(
            file_cmd + [cache_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        if not self._register_proc(gen, proc):
            return True
        self._last_backend = "edge-tts"
        proc.wait()
        return True

    def _speak_edge_tts_once(
        self,
        gen: int,
        text: str,
        voice: str,
        edge_rate: str,
        stdin_cmd: list[str],
        cache_path: str,
    ) -> tuple[bool, bool]:
        """Intenta sintetizar y reproducir una vez con edge-tts.
        Devuelve (exito_o_iniciado, error_de_red_permanente).
        """
        part_path = f"{cache_path}.{threading.get_ident()}.part"
        started_audio = False
        player_proc: subprocess.Popen | None = None

        async def _stream_and_play() -> bool:
            nonlocal started_audio, player_proc
            import edge_tts

            comm = edge_tts.Communicate(text, voice=voice, rate=edge_rate)
            stream_iter = comm.stream().__aiter__()
            with open(part_path, "wb") as fh:
                while True:
                    if self._is_cancelled(gen):
                        return False
                    timeout = 12.0 if not started_audio else 15.0
                    try:
                        chunk = await asyncio.wait_for(stream_iter.__anext__(), timeout=timeout)
                    except StopAsyncIteration:
                        break
                    if chunk.get("type") != "audio":
                        continue
                    data = chunk["data"]
                    if not data:
                        continue
                    fh.write(data)
                    if player_proc is None:
                        player_proc = subprocess.Popen(
                            stdin_cmd,
                            stdin=subprocess.PIPE,
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL,
                        )
                        if not self._register_proc(gen, player_proc):
                            return False
                        started_audio = True
                        self._last_backend = "edge-tts"
                    if player_proc.stdin is not None:
                        try:
                            player_proc.stdin.write(data)
                            player_proc.stdin.flush()
                        except BrokenPipeError:
                            return False
            return started_audio

        try:
            with _EDGE_SYNTH_LOCK:
                if self._is_cancelled(gen):
                    return (True, False)
                completed = asyncio.run(_stream_and_play())
            if player_proc is not None and player_proc.stdin is not None:
                try:
                    player_proc.stdin.close()
                except Exception:
                    pass
            if completed and not self._is_cancelled(gen):
                if os.path.isfile(part_path) and os.path.getsize(part_path) > 0:
                    try:
                        os.replace(part_path, cache_path)
                    except OSError:
                        pass
                if player_proc is not None:
                    player_proc.wait()
                return (True, False)
            return (started_audio or self._is_cancelled(gen), False)
        except Exception as exc:
            if player_proc is not None:
                self._terminate_proc(player_proc)
            # Errores de DNS / sin red: no perder tiempo reintentando
            err_name = type(exc).__name__
            is_offline = err_name in ("ClientConnectorDNSError", "ClientConnectorError", "gaierror")
            return (started_audio, is_offline)
        finally:
            if os.path.exists(part_path):
                try:
                    os.remove(part_path)
                except OSError:
                    pass

    def _speak_edge_tts(self, gen: int, text: str) -> bool:
        player = _find_mp3_player()
        if player is None:
            return False
        _, file_cmd, stdin_cmd = player
        voice = self._edge_voice_name()
        edge_rate = self._edge_rate_str()
        cache_path = self._cache_path_for(text, voice, edge_rate)

        # 1) Reproducción instantánea si ya existe en caché
        if os.path.isfile(cache_path) and os.path.getsize(cache_path) > 0:
            return self._play_cached_mp3(gen, file_cmd, cache_path)

        # 2) Hasta 2 intentos con edge-tts para garantizar la misma voz neuronal
        #    (el primer intento puede necesitar calibrar reloj DRM / reconectar WebSocket)
        for attempt in range(2):
            if self._is_cancelled(gen):
                return True
            if os.path.isfile(cache_path) and os.path.getsize(cache_path) > 0:
                return self._play_cached_mp3(gen, file_cmd, cache_path)
            ok, is_offline = self._speak_edge_tts_once(
                gen, text, voice, edge_rate, stdin_cmd, cache_path
            )
            if ok or self._is_cancelled(gen):
                return True
            if is_offline:
                return False
            if attempt == 0:
                time.sleep(0.25)
        return False

    def _speak_piper(self, gen: int, text: str) -> bool:
        piper_bin = shutil.which("piper")
        model_path = _find_piper_model()
        if not piper_bin or not model_path:
            return False
        tmp_wav = os.path.join(
            tempfile.gettempdir(), f"circe_piper_{threading.get_ident()}.wav"
        )
        try:
            res = subprocess.run(
                [piper_bin, "--model", model_path, "--output_file", tmp_wav],
                input=text.encode("utf-8"),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=15,
                check=False,
            )
            if res.returncode != 0 or not os.path.isfile(tmp_wav) or self._is_cancelled(gen):
                return False
            player_cmd: list[str] | None = None
            if shutil.which("paplay"):
                player_cmd = [shutil.which("paplay") or "paplay", tmp_wav]
            elif shutil.which("aplay"):
                player_cmd = [shutil.which("aplay") or "aplay", "-q", tmp_wav]
            elif shutil.which("ffplay"):
                player_cmd = [
                    shutil.which("ffplay") or "ffplay",
                    "-nodisp",
                    "-autoexit",
                    "-loglevel",
                    "quiet",
                    tmp_wav,
                ]
            if not player_cmd:
                return False
            proc = subprocess.Popen(
                player_cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            if not self._register_proc(gen, proc):
                return True
            self._last_backend = "piper"
            proc.wait()
            return True
        finally:
            if os.path.exists(tmp_wav):
                try:
                    os.remove(tmp_wav)
                except OSError:
                    pass

    def _speak_espeak(self, gen: int, text: str, backend: str) -> None:
        binary = shutil.which(backend) or "espeak-ng"
        cmd = [binary, "-v", self._espeak_voice_name(), "-s", str(self.rate), "-p", "54", text]
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        if not self._register_proc(gen, proc):
            return
        self._last_backend = backend
        proc.wait()

    def _speak_pyttsx3(self, text: str) -> None:
        import pyttsx3

        if self._engine is None:
            self._engine = pyttsx3.init()
            self._engine.setProperty("rate", self.rate)
            for v in self._engine.getProperty("voices") or []:
                vid = (getattr(v, "id", "") or "").lower()
                vname = (getattr(v, "name", "") or "").lower()
                if "es" in vid or "spanish" in vname or "espanol" in vname:
                    self._engine.setProperty("voice", v.id)
                    break
        self._last_backend = "pyttsx3"
        self._engine.say(text)
        self._engine.runAndWait()
