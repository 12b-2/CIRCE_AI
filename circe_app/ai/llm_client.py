from __future__ import annotations

import json
import os
from typing import Any

import requests


class LLMClient:
    def __init__(self, base_url: str | None = None, model: str = "llama3.1") -> None:
        self.base_url = base_url or os.getenv("OLLAMA_URL", "http://localhost:11434")
        self.model = model

    async def evaluate_action(self, user_text: str, node_prompt: str, correct_actions: list[str], partial_actions: list[str], wrong_actions: list[str]) -> dict[str, Any]:
        payload = {
            "model": self.model,
            "stream": False,
            "format": "json",
            "options": {"temperature": 0.2},
            "prompt": (
                "Eres un experto en ciberseguridad y evaluación de decisiones en entrenamiento de incidentes. "
                "Evalúa si la acción del estudiante es correcta, parcialmente correcta o incorrecta respecto a un escenario. "
                "No dependas de palabras clave rígidas ni de un patrón textual. Debes interpretar la intención del usuario. "
                "Devuelve JSON con este formato exacto: "
                "{\"verdict\": \"correct|partial|wrong\", \"score\": 0.0, \"reason\": \"...\", \"recommended_action\": \"...\"}.\n\n"
                f"Escenario: {node_prompt}\n"
                f"Acciones correctas: {correct_actions}\n"
                f"Acciones parcialmente correctas: {partial_actions}\n"
                f"Acciones incorrectas: {wrong_actions}\n"
                f"Respuesta del estudiante: {user_text}\n"
            ),
        }

        response = requests.post(f"{self.base_url}/api/generate", json=payload, timeout=90)
        response.raise_for_status()
        raw = response.json()
        text = raw.get("response", "")

        if not text:
            return {
                "verdict": "wrong",
                "score": 0.0,
                "reason": "No se obtuvo respuesta del modelo.",
                "recommended_action": "Reintente la acción y describa la intención con más detalle.",
            }

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {
                "verdict": "partial",
                "score": 0.5,
                "reason": text[:300],
                "recommended_action": "Valide si la respuesta refleja una acción de contención, análisis o comunicación apropiada.",
            }
