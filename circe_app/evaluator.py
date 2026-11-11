from __future__ import annotations

import re
import unicodedata
from typing import Any


STOPWORDS_ES = {
    "el", "la", "los", "las", "un", "una", "unos", "unas", "de", "del", "al",
    "a", "en", "con", "por", "para", "sin", "sobre", "y", "o", "u", "que",
    "se", "su", "sus", "mi", "mis", "tu", "tus", "es", "son", "fue", "mas",
    "pero", "como", "este", "esta", "estos", "estas", "ese", "esa", "todo",
    "toda", "todos", "todas", "yo", "primero", "luego", "despues", "hacer",
    "haria", "voy", "vamos",
}


class DecisionValidator:
    """Validador semántico y léxico local de decisiones para CIRCE.
    Actúa como motor híbrido y respaldo determinista cuando el LLM local no está activo.
    """

    @staticmethod
    def _normalize(value: str) -> str:
        normalized = unicodedata.normalize("NFD", (value or "").lower())
        normalized = normalized.encode("ascii", "ignore").decode("ascii")
        normalized = re.sub(r"[^a-z0-9\s]", " ", normalized)
        return re.sub(r"\s+", " ", normalized).strip()

    @classmethod
    def _stem_token(cls, token: str) -> str:
        # Reducción morfológica ligera en español para emparejar conjugaciones (ej. aíslo/aislar/aislando -> aisl)
        if len(token) <= 4:
            return token
        for suffix in (
            "amiento", "imiento", "aciones", "iciones", "ando", "iendo",
            "aron", "ieron", "aria", "aran", "eran", "iran", "adas", "idos",
            "ada", "ido", "ar", "er", "ir", "es", "os", "as", "an", "en", "o",
        ):
            if token.endswith(suffix) and len(token) - len(suffix) >= 4:
                return token[: -len(suffix)]
        return token

    @classmethod
    def _extract_stems(cls, text: str) -> set[str]:
        norm = cls._normalize(text)
        tokens = [t for t in norm.split() if t not in STOPWORDS_ES and len(t) > 2]
        return {cls._stem_token(t) for t in tokens} | set(tokens)

    @classmethod
    def _phrase_match_score(cls, user_norm: str, user_stems: set[str], phrase: str) -> float:
        phrase_norm = cls._normalize(phrase)
        if not phrase_norm:
            return 0.0
        if phrase_norm in user_norm:
            return 1.0
        phrase_stems = cls._extract_stems(phrase_norm)
        if not phrase_stems:
            return 0.0
        overlap = len(phrase_stems & user_stems)
        return overlap / len(phrase_stems)

    def evaluate(
        self,
        user_text: str,
        node_prompt: str,
        correct_actions: list[str],
        partial_actions: list[str],
        wrong_actions: list[str],
        keywords_correct: list[str] | None = None,
        keywords_partial: list[str] | None = None,
        keywords_wrong: list[str] | None = None,
    ) -> dict[str, Any]:
        text = self._normalize(user_text or "")
        user_stems = self._extract_stems(text)

        if not text or len(text) < 3:
            return {
                "verdict": "wrong",
                "score": 0.0,
                "reason": "No se detectó una instrucción o decisión clara.",
                "recommended_action": (
                    f"Indica una acción concreta como: {correct_actions[0] if correct_actions else 'aislar y analizar el incidente'}."
                ),
            }

        # 1. Coincidencias exactas o por solapamiento de raíces con las listas de acciones
        correct_scores = [self._phrase_match_score(text, user_stems, a) for a in correct_actions]
        partial_scores = [self._phrase_match_score(text, user_stems, a) for a in partial_actions]
        wrong_scores = [self._phrase_match_score(text, user_stems, a) for a in wrong_actions]

        # 2. Coincidencias con palabras clave específicas del nodo
        kw_correct_hits = [
            kw for kw in (keywords_correct or [])
            if self._normalize(kw) in text or (self._extract_stems(kw) and self._extract_stems(kw).issubset(user_stems))
        ]
        kw_partial_hits = [
            kw for kw in (keywords_partial or [])
            if self._normalize(kw) in text or (self._extract_stems(kw) and self._extract_stems(kw).issubset(user_stems))
        ]
        kw_wrong_hits = [
            kw for kw in (keywords_wrong or [])
            if self._normalize(kw) in text
        ]

        best_correct = max(correct_scores, default=0.0)
        best_partial = max(partial_scores, default=0.0)
        best_wrong = max(wrong_scores, default=0.0)

        recommended_default = (
            f"La acción prioritaria recomendada es: {correct_actions[0]}."
            if correct_actions
            else "Priorice la contención, preservación forense y comunicación formal."
        )

        # Regla de decisión
        if (best_wrong >= 0.65 or kw_wrong_hits) and best_correct < 0.6 and len(kw_correct_hits) == 0:
            verdict = "wrong"
            score = 0.15
            reason = (
                "La decisión propuesta incluye acciones riesgosas o contraproducentes que pueden "
                "destruir evidencia forense o agravar el impacto del incidente."
            )
            recommended = recommended_default
        elif best_correct >= 0.45 or len(kw_correct_hits) >= 2 or (len(kw_correct_hits) == 1 and best_correct >= 0.3):
            verdict = "correct"
            score = 0.95 if (best_correct >= 0.7 or len(kw_correct_hits) >= 2) else 0.85
            reason = (
                "¡Excelente decisión! Tu acción aborda directamente la prioridad crítica de este nivel "
                "siguiendo las buenas prácticas de respuesta a incidentes."
            )
            recommended = "Continúa aplicando contención oportuna, trazabilidad forense y coordinación."
        elif len(kw_correct_hits) == 1 or best_partial >= 0.45 or len(kw_partial_hits) >= 1:
            verdict = "partial"
            score = 0.60
            reason = (
                "Tu respuesta va bien encaminada y aporta valor, pero falta ejecutar o detallar "
                "la medida principal de este nivel para controlar completamente el riesgo."
            )
            recommended = recommended_default
        else:
            verdict = "partial"
            score = 0.45
            reason = (
                "Tu respuesta es general y no especifica con suficiente precisión la acción técnica "
                "clave para resolver esta etapa del incidente."
            )
            recommended = recommended_default

        return {
            "verdict": verdict,
            "score": score,
            "reason": reason,
            "recommended_action": recommended,
        }
