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

# Palabras que niegan lo que viene después ("sin apagarlo", "no formateo").
NEGATIONS = {"no", "nunca", "jamas", "sin", "ni", "evito", "evitar", "evitamos", "evita", "evitando"}
NEGATION_LOOKBACK = 3   # cuántas palabras hacia atrás se revisan
KEYWORD_GAP = 2         # palabras que pueden separar las partes de una palabra clave de varias palabras


class DecisionValidator:
    """Validador semántico y léxico local de decisiones para CIRCE.
    Actúa como motor híbrido y respaldo determinista cuando el LLM local no está activo.

    Convención de palabras clave (keywords_correct / keywords_partial / keywords_wrong):
      "aislar"       palabra completa; también acepta conjugaciones (aislo, aislando) y plurales.
      "format*"      cualquier palabra que EMPIECE con "format" (formatear, formateo, formateándolo).
      "post mortem"  varias palabras: deben aparecer en ese orden, con como máximo 2 palabras en medio.
    Las apariciones negadas ("sin apagarlo", "no formateo") no cuentan como coincidencia.
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

    # ------------------------------------------------------------------ palabras clave
    @classmethod
    def _parse_keyword(cls, kw: str) -> list[str]:
        parts: list[str] = []
        for raw in (kw or "").split():
            norm = cls._normalize(raw)
            if norm:
                parts.append(norm + "*" if raw.endswith("*") else norm)
        return parts

    @classmethod
    def _part_matches(cls, token: str, part: str) -> bool:
        if part.endswith("*"):
            return token.startswith(part[:-1])
        if token == part or token in (part + "s", part + "es"):
            return True
        return cls._stem_token(token) == cls._stem_token(part)

    @classmethod
    def _keyword_hit(cls, kw: str, tokens: list[str], skip_negated: bool = False) -> bool:
        parts = cls._parse_keyword(kw)
        if not parts:
            return False
        check_negation = skip_negated and parts[0] not in NEGATIONS
        for i, tok in enumerate(tokens):
            if not cls._part_matches(tok, parts[0]):
                continue
            if check_negation and any(t in NEGATIONS for t in tokens[max(0, i - NEGATION_LOOKBACK):i]):
                continue
            pos, ok = i, True
            for part in parts[1:]:
                nxt = next(
                    (k for k in range(pos + 1, min(pos + 1 + KEYWORD_GAP + 1, len(tokens)))
                     if cls._part_matches(tokens[k], part)),
                    None,
                )
                if nxt is None:
                    ok = False
                    break
                pos = nxt
            if ok:
                return True
        return False

    @classmethod
    def _hits(cls, keywords: list[str] | None, tokens: list[str], skip_negated: bool = False) -> list[str]:
        return [kw for kw in (keywords or []) if cls._keyword_hit(kw, tokens, skip_negated)]

    # ------------------------------------------------------------------ evaluación
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
        tokens = text.split()
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
        # Las apariciones negadas ("sin verificar la integridad") no cuentan ni a favor ni en contra.
        kw_correct_hits = self._hits(keywords_correct, tokens, skip_negated=True)
        kw_partial_hits = self._hits(keywords_partial, tokens)
        kw_wrong_hits = self._hits(keywords_wrong, tokens, skip_negated=True)

        best_correct = max(correct_scores, default=0.0)
        best_partial = max(partial_scores, default=0.0)
        best_wrong = max(wrong_scores, default=0.0)

        # 3. ¿Habla de otra cosa? (varias palabras y ninguna comparte raíz con el vocabulario del nodo)
        domain_vocab = " ".join([
            node_prompt, *correct_actions, *partial_actions, *wrong_actions,
            *(keywords_correct or []), *(keywords_partial or []), *(keywords_wrong or []),
        ])
        off_topic = len(tokens) >= 4 and not (user_stems & self._extract_stems(domain_vocab))

        recommended_default = (
            f"La acción prioritaria recomendada es: {correct_actions[0]}."
            if correct_actions
            else "Priorice la contención, preservación forense y comunicación formal."
        )

        strong_wrong = best_wrong >= 0.65 and best_wrong > best_correct
        danger = bool(kw_wrong_hits) or strong_wrong
        clearly_correct = best_correct >= 0.6 or len(kw_correct_hits) >= 2
        looks_correct = (
            best_correct >= 0.45
            or len(kw_correct_hits) >= 2
            or (len(kw_correct_hits) == 1 and best_correct >= 0.3)
        )

        mixed = False

        # Regla de decisión
        if strong_wrong or (danger and not clearly_correct):
            verdict = "wrong"
            score = 0.15
            reason = (
                "La decisión propuesta incluye acciones riesgosas o contraproducentes que pueden "
                "destruir evidencia forense o agravar el impacto del incidente."
            )
            recommended = recommended_default
        elif looks_correct and danger:
            mixed = True
            verdict = "partial"
            score = 0.45
            reason = (
                "Tu respuesta incluye una acción correcta, pero también otra riesgosa que puede "
                "destruir evidencia o agravar el incidente."
            )
            recommended = "Conserva solo la medida correcta y descarta la acción riesgosa."
        elif looks_correct:
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
        elif off_topic:
            verdict = "wrong"
            score = 0.10
            reason = "Tu respuesta no está relacionada con el incidente ni describe una acción técnica."
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
            "partial_match": best_partial,
            "wrong_hit": danger,
            # Coincidió con una acción o palabra parcial de la rúbrica y no hay nada peligroso
            "partial_hit": (best_partial >= 0.45 or bool(kw_partial_hits)) and not danger,
            # Acción correcta + acción peligrosa en la misma respuesta
            "mixed": mixed,
            "detected_concepts": [k.replace("*", "") for k in kw_correct_hits],
        }