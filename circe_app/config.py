from __future__ import annotations

import os
from dataclasses import dataclass, field
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
    level_number: int = 1
    hint: str = "Piensa primero en contener la amenaza, preservar la evidencia forense y comunicar formalmente."
    keywords_correct: list[str] = field(default_factory=list)
    keywords_partial: list[str] = field(default_factory=list)
    keywords_wrong: list[str] = field(default_factory=list)


@dataclass
class LevelScenario:
    id: str
    level_number: int
    title: str
    subtitle: str
    icon: str
    difficulty: str
    description: str
    start_node_id: str
    nodes: dict[str, ScenarioNode]


@dataclass
class CIRCEConfig:
    scenario_name: str = "Filtración de datos corporativos"
    default_level_id: str = "level_1"
    max_decisions: int = 5
    llm_base_url: str = field(default_factory=lambda: os.getenv("OLLAMA_URL", "http://localhost:11434"))
    llm_model: str = field(default_factory=lambda: os.getenv("CIRCE_LLM_MODEL", "llama3.1"))
    llm_timeout_seconds: int = 15
    stt_model: str = field(default_factory=lambda: os.getenv("CIRCE_STT_MODEL", "tiny"))
    stt_device: str = field(default_factory=lambda: os.getenv("CIRCE_STT_DEVICE", "cpu"))
    stt_compute_type: str = "int8"
    audio_sample_rate: int = 16000
    max_record_seconds: int = 15
    voice_language: str = "es"
    tts_engine: Literal["auto", "espeak-ng", "pyttsx3", "piper"] = "auto"
    tts_rate: int = 165
    auto_speak_instructions: bool = True
    auto_speak_feedback: bool = True


DEFAULT_CONFIG = CIRCEConfig()
