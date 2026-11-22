from __future__ import annotations

from typing import Any

CORRECT_NEXT_STEP = "Continúa con contención oportuna, trazabilidad forense y coordinación."


def _first_sentence(text: str) -> str:
    text = (text or "").strip()
    for i, ch in enumerate(text):
        if ch in ".!?":
            return text[: i + 1]
    return text


def combine(
    local: dict[str, Any],
    llm: dict[str, Any] | None,
    focus: str = "",
    avoided: str = "",
) -> dict[str, Any]:
    if llm is None:
        return local

    lv, mv = local["verdict"], llm["verdict"]
    dangerous = llm.get("dangerous_action", False)
    off_topic = llm.get("off_topic", False)
    score = round(0.4 * local["score"] + 0.6 * llm["score"], 2)
    partial_hit = local.get("partial_hit", local.get("partial_match", 0.0) >= 0.45)

    if {lv, mv} == {"correct", "wrong"}:
        verdict, score = "partial", min(score, 0.55)
    elif lv == "wrong" and mv == "correct":
        verdict, score = "partial", min(score, 0.6)
    elif local.get("mixed") and not off_topic and mv in ("partial", "wrong"):
        # El local detectó una acción correcta y otra peligrosa en la misma respuesta: parcial por definición.
        verdict, score = "partial", max(score, 0.4)
    elif lv == "correct" and mv == "partial" and not dangerous:
        # El LLM exige más de lo que pide la rúbrica y no vio nada peligroso.
        verdict, score = "correct", max(score, local["score"])
    elif (
        lv == "partial" and mv == "wrong"
        and not dangerous and not off_topic
        and partial_hit
        and not local.get("wrong_hit", False)
    ):
        # Acción parcial de la rúbrica sin nada peligroso: nunca debe costar una vida.
        verdict, score = "partial", max(score, 0.5)
    else:
        verdict = "correct" if score >= 0.8 else "partial" if score >= 0.4 else "wrong"
        if lv == "wrong" and verdict == "correct":
            verdict = "partial"

    # El score debe ser coherente con el veredicto final
    lo, hi = {"correct": (0.8, 1.0), "partial": (0.4, 0.7), "wrong": (0.0, 0.3)}[verdict]
    score = round(max(lo, min(hi, score)), 2)

    # Texto coherente con el veredicto final
    if verdict == "correct":
        if mv == "correct" and llm.get("reason"):
            reason = _first_sentence(llm["reason"])
        elif focus:
            reason = f"Muy bien: resolviste la prioridad de esta etapa, {focus}."
        else:
            reason = "Muy bien: resolviste la prioridad de esta etapa."
        recommended = (
            f"Con esto evitas esta consecuencia: {avoided[0].lower() + avoided[1:]}" if avoided else CORRECT_NEXT_STEP
        )
    else:
        src = llm if verdict == mv else (local if verdict == lv else llm)
        reason = src["reason"] or local["reason"]
        recommended = src["recommended_action"] or local["recommended_action"]

    return {
        "verdict": verdict,
        "score": score,
        "reason": reason,
        "recommended_action": recommended,
        "detected_concepts": llm.get("detected_concepts", []),
        "missing_concepts": llm.get("missing_concepts", []),
        "dangerous_action": dangerous,
        "off_topic": off_topic,
        "confidence": "alta" if lv == mv else "baja",
    }