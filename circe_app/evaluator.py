from __future__ import annotations

import re
import unicodedata
from typing import Any


class DecisionValidator:
    """Validador local de decisiones para CIRCE. Sirve como fallback real cuando el LLM no está disponible."""

    @staticmethod
    def _normalize(value: str) -> str:
        normalized = unicodedata.normalize("NFD", value.lower())
        normalized = normalized.encode("ascii", "ignore").decode("ascii")
        return re.sub(r"[^a-z0-9\s]", " ", normalized)

    def evaluate(self, user_text: str, node_prompt: str, correct_actions: list[str], partial_actions: list[str], wrong_actions: list[str]) -> dict[str, Any]:
        text = self._normalize(user_text or "")

        correct_hits = [term for term in correct_actions if self._normalize(term) in text]
        partial_hits = [term for term in partial_actions if self._normalize(term) in text]
        wrong_hits = [term for term in wrong_actions if self._normalize(term) in text]

        if wrong_hits:
            verdict = "wrong"
            score = 0.15
            reason = "La respuesta incluye acciones peligrosas o no apropiadas para la contención del incidente."
            recommended = "Priorice la contención, la preservación de evidencia y la evaluación del alcance antes de actuar."
        elif correct_hits:
            verdict = "correct"
            score = 0.95
            reason = "La respuesta refleja una acción adecuada para la respuesta a incidentes y la intención del caso."
            recommended = "Mantenga el enfoque en contención, análisis de alcance y comunicación formal."
        elif partial_hits:
            verdict = "partial"
            score = 0.6
            reason = "La respuesta tiene una intención útil, pero aún no completa la respuesta correcta para este escenario."
            recommended = "Ajuste su respuesta para incluir contención del sistema, revisión del alcance y coordinación con seguridad."
        else:
            verdict = "partial"
            score = 0.45
            reason = "La respuesta no expresa de forma clara una acción correcta o incompleta para este escenario."
            recommended = "Describa la acción concreta que tomaría para aislar, analizar y comunicar el incidente."

        return {
            "verdict": verdict,
            "score": score,
            "reason": reason,
            "recommended_action": recommended,
        }
