from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


@dataclass
class ScenarioNode:
    id: str
    title: str
    prompt: str
    correct_actions: list[str]
    partial_actions: list[str]
    wrong_actions: list[str]
    consequences: list[str]
    next_node: str | None = None


@dataclass
class CIRCEConfig:
    scenario_name: str = "Filtración de datos corporativos"
    max_decisions: int = 4
    llm_model: str = "llama3.1"
    stt_model: str = "tiny"
    audio_sample_rate: int = 16000
    voice_language: str = "es"
    tts_engine: Literal["pyttsx3", "piper"] = "pyttsx3"


DEFAULT_CONFIG = CIRCEConfig()
