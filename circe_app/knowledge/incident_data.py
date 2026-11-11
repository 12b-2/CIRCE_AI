from __future__ import annotations

INCIDENT_CONTEXT = {
    "company": "NexaCorp",
    "system": "servidor de archivos compartidos",
    "impact": "acceso no autorizado a información empresarial sensible",
    "affected_assets": ["servidor interno", "equipo de administración", "sistema de backup"],
    "root_cause": "credenciales comprometidas y posible movimiento lateral",
    "timeline": [
        "08:42 - se detecta acceso no autorizado fuera de horario",
        "08:45 - se activa la alerta de seguridad",
        "08:50 - se aisla la máquina afectada",
    ],
}
