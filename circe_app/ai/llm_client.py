from __future__ import annotations

import asyncio
import json
import os
from typing import Any

import requests


class LLMClient:
    """Cliente modular para evaluación semántica con LLM local (Ollama: llama3.1, qwen2.5, mistral)."""

    def __init__(self, base_url: str | None = None, model: str = "llama3.1", timeout: int = 18) -> None:
        self.base_url = (base_url or os.getenv("OLLAMA_URL", "http://localhost:11434")).rstrip("/")
        self.model = model or os.getenv("CIRCE_LLM_MODEL", "llama3.1")
        self.timeout = timeout

    def is_available(self) -> bool:
        """Verifica rápidamente si el servidor Ollama local responde."""
        try:
            resp = requests.get(f"{self.base_url}/api/tags", timeout=1.2)
            return resp.status_code == 200
        except Exception:
            return False

    def _post_generate(self, payload: dict[str, Any]) -> dict[str, Any]:
        response = requests.post(
            f"{self.base_url}/api/generate",
            json=payload,
            timeout=(1.5, self.timeout),
        )
        response.raise_for_status()
        return response.json()

    async def evaluate_action(
        self,
        user_text: str,
        node_prompt: str,
        correct_actions: list[str],
        partial_actions: list[str],
        wrong_actions: list[str],
    ) -> dict[str, Any]:
        payload = {
            "model": self.model,
            "stream": False,
            "format": "json",
            "options": {"temperature": 0.2},
            "prompt": (
                "Eres Circe, una instructora experta en ciberseguridad y respuesta a incidentes. "
                "Evalúa la decisión del estudiante (que pudo ser transcrita desde voz o escrita en texto) "
                "frente al nivel actual del incidente. Interpreta la intención técnica real en español. "
                "Devuelve EXCLUSIVAMENTE un objeto JSON con este esquema exacto: "
                "{\"verdict\": \"correct|partial|wrong\", \"score\": 0.0, \"reason\": \"Explicación clara en español\", "
                "\"recommended_action\": \"Consejo práctico en español\"}.\n\n"
                f"Contexto del Nivel: {node_prompt}\n"
                f"Acciones correctas esperadas: {correct_actions}\n"
                f"Acciones parcialmente correctas: {partial_actions}\n"
                f"Acciones incorrectas o peligrosas: {wrong_actions}\n"
                f"Respuesta del estudiante: {user_text}\n"
            ),
        }

        raw = await asyncio.to_thread(self._post_generate, payload)
        text = raw.get("response", "")

        if not text:
            raise RuntimeError("Respuesta vacía del servidor LLM.")

        try:
            parsed = json.loads(text)
            verdict = parsed.get("verdict", "partial")
            if verdict not in ("correct", "partial", "wrong"):
                verdict = "partial"
            score = float(parsed.get("score", 0.5))
            return {
                "verdict": verdict,
                "score": max(0.0, min(1.0, score)),
                "reason": str(parsed.get("reason", "")).strip() or "Evaluación completada.",
                "recommended_action": str(parsed.get("recommended_action", "")).strip(),
            }
        except (json.JSONDecodeError, ValueError, TypeError):
            return {
                "verdict": "partial",
                "score": 0.5,
                "reason": text[:300],
                "recommended_action": "Valide si la respuesta refleja contención, análisis forense y comunicación.",
            }
