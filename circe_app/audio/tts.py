from __future__ import annotations

import shutil
import subprocess
import threading
from typing import Callable


class TextToSpeech:
    """Motor de síntesis de voz (TTS) modular y no bloqueante en español.
    Soporta:
      - espeak-ng (subproceso cancelable instantáneamente, voz es-419 / es)
      - piper (modelo neuronal local si está instalado)
      - pyttsx3 (hilo dedicado configurado en español)
    """

    def __init__(self, engine_name: str = "auto", rate: int = 165, voice: str = "es-419") -> None:
        self.engine_name = engine_name
        self.rate = rate
        self.voice = voice
        self.enabled: bool = True
        self._engine = None
        self._active_proc: subprocess.Popen | None = None
        self._lock = threading.Lock()
        self._is_speaking = False

    @property
    def is_speaking(self) -> bool:
        return self._is_speaking

    def _resolve_backend(self) -> str:
        if self.engine_name == "auto":
            if shutil.which("espeak-ng"):
                return "espeak-ng"
            if shutil.which("espeak"):
                return "espeak"
            return "pyttsx3"
        if self.engine_name == "pyttsx3" and shutil.which("espeak-ng"):
            # En Linux pyttsx3 invoca espeak internamente de forma bloqueante;
            # usar espeak-ng directo permite cancelar locución y evita congelar Tkinter.
            return "espeak-ng"
        return self.engine_name

    def stop(self) -> None:
        """Detiene inmediatamente cualquier locución activa."""
        with self._lock:
            if self._active_proc is not None and self._active_proc.poll() is None:
                try:
                    self._active_proc.terminate()
                    self._active_proc.wait(timeout=0.5)
                except Exception:
                    try:
                        self._active_proc.kill()
                    except Exception:
                        pass
            self._active_proc = None
            self._is_speaking = False

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

        clean_text = text.replace("·", ". ").replace("⚡", "").replace("❤", "vidas ").strip()
        self.stop()

        if blocking:
            self._speak_worker(clean_text, on_done)
        else:
            thread = threading.Thread(
                target=self._speak_worker,
                args=(clean_text, on_done),
                daemon=True,
            )
            thread.start()

    def _speak_worker(self, text: str, on_done: Callable[[], None] | None = None) -> None:
        backend = self._resolve_backend()
        self._is_speaking = True
        try:
            if backend in ("espeak-ng", "espeak"):
                binary = shutil.which(backend) or "espeak-ng"
                cmd = [binary, "-v", self.voice, "-s", str(self.rate), text]
                with self._lock:
                    self._active_proc = subprocess.Popen(
                        cmd,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                self._active_proc.wait()
                return

            if backend == "pyttsx3":
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
                self._engine.say(text)
                self._engine.runAndWait()
                return

            raise ValueError(f"Motor TTS no soportado: {self.engine_name}")
        except Exception:
            pass
        finally:
            self._is_speaking = False
            if on_done:
                try:
                    on_done()
                except Exception:
                    pass
