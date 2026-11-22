from __future__ import annotations

from circe_app.hybrid import combine


def _local(verdict: str, score: float, **extra) -> dict:
    return {"verdict": verdict, "score": score, "reason": f"local {verdict}",
            "recommended_action": "accion local", **extra}


def _llm(verdict: str, score: float, **extra) -> dict:
    return {"verdict": verdict, "score": score, "reason": f"llm {verdict}",
            "recommended_action": "accion llm", **extra}


def test_mezcla_detectada_por_el_local_es_parcial_aunque_el_llm_diga_wrong() -> None:
    r = combine(_local("partial", 0.45, mixed=True), _llm("wrong", 0.0, dangerous_action=True))
    assert r["verdict"] == "partial"
    assert r["score"] >= 0.4
    assert r["reason"] == "local partial"          # el texto coincide con el veredicto final


def test_parcial_de_rubrica_sin_peligro_no_baja_a_wrong() -> None:
    local = _local("partial", 0.6, partial_hit=True, wrong_hit=False)
    r = combine(local, _llm("wrong", 0.0, dangerous_action=False, off_topic=False))
    assert r["verdict"] == "partial"


def test_si_el_llm_marca_peligro_se_respeta() -> None:
    local = _local("partial", 0.6, partial_hit=True, wrong_hit=False)
    r = combine(local, _llm("wrong", 0.0, dangerous_action=True))
    assert r["verdict"] == "wrong"


def test_fuera_de_tema_sigue_siendo_wrong() -> None:
    r = combine(_local("wrong", 0.1), _llm("wrong", 0.0, off_topic=True))
    assert r["verdict"] == "wrong"