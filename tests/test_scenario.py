from __future__ import annotations

import pytest

from circe_app.evaluator import DecisionValidator
from circe_app.knowledge.scenario import LEVELS_CATALOG, validate_catalog


def _evaluar(level_id: str, node_id: str, texto: str) -> dict:
    n = LEVELS_CATALOG[level_id].nodes[node_id]
    return DecisionValidator().evaluate(
        texto, n.prompt, n.correct_actions, n.partial_actions, n.wrong_actions,
        n.keywords_correct, n.keywords_partial, n.keywords_wrong,
    )


def test_catalogo_valido() -> None:
    assert validate_catalog() == []


@pytest.mark.parametrize("keyword,texto", [
    ("red", "cambio las credenciales"),        # antes coincidía por subcadena
    ("api", "lo reviso rápido"),
    ("cert", "quiero certificar el equipo"),
])
def test_keyword_no_coincide_por_subcadena(keyword: str, texto: str) -> None:
    tokens = DecisionValidator._normalize(texto).split()
    assert not DecisionValidator._keyword_hit(keyword, tokens)


@pytest.mark.parametrize("level_id,node_id,texto", [
    ("level_1", "node_1", "Aíslo el servidor de la red sin apagarlo ni formatearlo para conservar la memoria"),
    ("level_2", "node_4", "No pago el rescate, activo el plan de continuidad y aviso a las autoridades y a legal"),
    ("level_2", "node_4", "No voy a pagar el rescate y aviso a las autoridades"),
])
def test_negaciones_de_acciones_peligrosas_no_penalizan(level_id: str, node_id: str, texto: str) -> None:
    assert _evaluar(level_id, node_id, texto)["verdict"] == "correct"


@pytest.mark.parametrize("level_id,node_id,texto", [
    ("level_1", "node_1", "Aíslo el servidor de la red y después lo formateo"),
    ("level_3", "node_1", "Bloqueo la sesión y luego elimino la cuenta del director con todos sus correos"),
    ("level_5", "node_2", "Hago la imagen forense con hashes y luego formateo la laptop para reutilizarla"),
])
def test_mezcla_correcta_y_peligrosa_es_parcial(level_id: str, node_id: str, texto: str) -> None:
    assert _evaluar(level_id, node_id, texto)["verdict"] == "partial"


def test_fuera_de_tema_es_incorrecto() -> None:
    assert _evaluar("level_4", "node_3", "Me gusta la pizza con piña")["verdict"] == "wrong"