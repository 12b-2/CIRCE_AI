from __future__ import annotations

import re
import unicodedata

_PATTERNS = [
    r"ignor\w*\s+(\w+\s+){0,3}(instruccion\w*|reglas|indicacion\w*|prompt)",
    r"olvid\w*\s+(\w+\s+){0,3}(instruccion\w*|reglas)",
    r"(dame|damelo|asigna\w*|otorga\w*|pon\w*)\s+(\w+\s+){0,3}(puntos|puntaje|score|xp|vidas)",
    r"veredicto\s*(sea|es|:)?\s*(correct|partial|wrong|correcto)",
    r"(system|sistema)\s*prompt",
    r"(responde|devuelve|marca)\w*\s+(\w+\s+){0,3}(correct|correcta|100)",
    r"eres\s+ahora",
    r"a\s+partir\s+de\s+ahora",
]
_REGEX = [re.compile(p) for p in _PATTERNS]


def _norm(text: str) -> str:
    t = unicodedata.normalize("NFD", text.lower())
    return t.encode("ascii", "ignore").decode("ascii")


def strip_injection(text: str) -> tuple[str, bool]:
    """Quita las cláusulas dirigidas al evaluador. Devuelve (texto_limpio, hubo_intento)."""
    clauses = re.split(r"[.!?;\n,]+", text or "")
    kept, flagged = [], False
    for clause in clauses:
        if any(rx.search(_norm(clause)) for rx in _REGEX):
            flagged = True
        elif clause.strip():
            kept.append(clause.strip())
    return " ".join(kept), flagged