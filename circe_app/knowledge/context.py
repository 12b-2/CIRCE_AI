from __future__ import annotations

from typing import Any

from circe_app.config import LevelScenario, ScenarioNode
from circe_app.knowledge.rules import SECURITY_RULES

# Reglas IR relevantes por tipo de decisión. Ajusta a tu criterio.
NODE_RULE_IDS: dict[int, list[str]] = {
    1: ["IR-01"],
    2: ["IR-02", "IR-03"],
    3: ["IR-01", "IR-03"],
    4: ["IR-04"],
    5: ["IR-02", "IR-04"],
}

# Contexto breve por nivel (el de level_1 viene de incident_data.py)
LEVEL_CONTEXT: dict[str, str] = {
    "level_1": "Empresa NexaCorp. Servidor de archivos compartidos con acceso no autorizado fuera de horario; causa probable: credenciales comprometidas y movimiento lateral.",
    "level_2": "Ransomware cifrando carpetas compartidas SMB en estaciones de finanzas; riesgo sobre copias sombra y servidor de backups.",
    "level_3": "Fraude BEC: cuenta del Director Financiero comprometida desde una IP anómala, con órdenes de pago urgentes.",
    "level_4": "Llave de acceso cloud expuesta en un repositorio; el atacante crea instancias y lee buckets de almacenamiento.",
    "level_5": "Amenaza interna: ingeniero con privilegios elevados copia propiedad intelectual a un servicio externo.",
}


def build_node_context(
    level: LevelScenario,
    node: ScenarioNode,
    session: Any,
    history: list[dict[str, Any]],
    max_previous: int = 2,
) -> str:
    rules = [r for r in SECURITY_RULES if r.id in NODE_RULE_IDS.get(node.level_number, [])]
    rules_txt = "\n".join(f"- {r.id} {r.title}: {r.description}" for r in rules) or "- (sin reglas específicas)"

    previous = [h for h in history if h.get("type") == "evaluation"][-max_previous:]
    prev_txt = "\n".join(
        f"- {h['node_title']}: {h['content'].get('verdict')}" for h in previous
    ) or "- (primera decisión)"

    return (
        f"ESCENARIO: {level.title}\n"
        f"SITUACIÓN: {LEVEL_CONTEXT.get(level.id, level.description)}\n"
        f"ETAPA ACTUAL: {node.title}\n"
        f"PLANTEAMIENTO: {node.prompt}\n"
        f"REGLAS DE RESPUESTA A INCIDENTES APLICABLES:\n{rules_txt}\n"
        f"CONSECUENCIA SI SE DECIDE MAL: {' '.join(node.consequences)}\n"
        f"DECISIONES PREVIAS DEL ESTUDIANTE:\n{prev_txt}\n"
        f"ESTADO: vidas={session.lives}, contención={session.containment}%, "
        f"seguridad de datos={session.data_safety}%"
    )