from __future__ import annotations

from circe_app.config import ScenarioNode


SCENARIO_TREE = {
    "node_1": ScenarioNode(
        id="node_1",
        title="Detección del evento",
        prompt=(
            "Se detecta una posible exfiltración de datos. El sistema informa que "
            "alguien accedió a información sensible fuera de horario. ¿Qué haría usted primero?"
        ),
        correct_actions=[
            "aíslar el sistema afectado",
            "bloquear el acceso",
            "aislar el servidor",
            "desconectar el equipo comprometido",
        ],
        partial_actions=[
            "revisar logs",
            "notificar al equipo de seguridad",
            "hacer copia forensic",
        ],
        wrong_actions=[
            "restaurar el sistema sin investigar",
            "eliminar todo sin análisis",
            "compartir credenciales para probar",
            "ignorar la amenaza",
        ],
        consequences=[
            "El atacante puede seguir accediendo y extraer más información.",
            "La evidencia digital se puede perder.",
        ],
        next_node="node_2",
    ),
    "node_2": ScenarioNode(
        id="node_2",
        title="Análisis de alcance",
        prompt=(
            "La máquina comprometida ya fue aislada. Debe determinar qué datos fueron accedidos "
            "y quién tuvo permisos. ¿Cuál es su siguiente acción?"
        ),
        correct_actions=[
            "revisar los logs de acceso",
            "analizar permisos y conexiones",
            "identificar usuarios afectados",
            "comparar accesos sospechosos",
        ],
        partial_actions=[
            "revisar los archivos más importantes",
            "preguntar al responsable del área",
            "documentar la incidencia",
        ],
        wrong_actions=[
            "borrar los logs",
            "reiniciar todo sin evidencia",
            "revelar la brecha a todos los empleados",
        ],
        consequences=[
            "Se pierde trazabilidad del ataque y se complica la contención.",
            "Los usuarios afectados pueden seguir exponiendo datos.",
        ],
        next_node="node_3",
    ),
    "node_3": ScenarioNode(
        id="node_3",
        title="Comunicación y remediación",
        prompt=(
            "El alcance está delimitado. Debe decidir cómo coordinar la respuesta y la comunicación "
            "con la organización. ¿Qué haría?"
        ),
        correct_actions=[
            "notificar a la dirección y seguridad",
            "seguir el plan de respuesta a incidentes",
            "documentar medidas y comunicar a stakeholders",
            "activar el protocolo de filtrar y remediar",
        ],
        partial_actions=[
            "avisar a algunos departamentos",
            "pedir revisión legal",
            "iniciar una investigación preliminar",
        ],
        wrong_actions=[
            "publicar la información en un correo de grupo",
            "ocultar la incidencia para evitar alarma",
            "cancelar el proceso de respuesta",
        ],
        consequences=[
            "El daño reputacional y legal puede crecer si no se comunica apropiadamente.",
            "Se pierde oportunidad de control del impacto.",
        ],
        next_node=None,
    ),
}

START_NODE_ID = "node_1"
