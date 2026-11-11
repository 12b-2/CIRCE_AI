from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class SecurityRule:
    id: str
    title: str
    description: str
    priority: str = "high"
    tags: list[str] = field(default_factory=list)


SECURITY_RULES = [
    SecurityRule(
        id="IR-01",
        title="Contención inmediata",
        description="Si existe evidencia de acceso no autorizado, se debe aislar la máquina o servicio afectado antes de continuar con actividad de remediación.",
        priority="critical",
        tags=["containment", "access", "isolation", "incident"],
    ),
    SecurityRule(
        id="IR-02",
        title="Preservación de evidencia",
        description="Los registros, logs y artefactos deben preservarse para análisis forense y trazabilidad del incidente.",
        priority="high",
        tags=["evidence", "logs", "forensics"],
    ),
    SecurityRule(
        id="IR-03",
        title="Evaluación de alcance",
        description="Se debe identificar qué sistemas, usuarios, permisos y datos fueron afectados para determinar el impacto real.",
        priority="high",
        tags=["scope", "impact", "permissions", "analysis"],
    ),
    SecurityRule(
        id="IR-04",
        title="Comunicación consistente",
        description="Las decisiones y la comunicación a dirección, seguridad y áreas impactadas deben ser coordinadas y documentadas.",
        priority="medium",
        tags=["communication", "stakeholders", "response"],
    ),
]

CRITICAL_CONSEQUENCES = {
    "exfiltration": "La filtración de datos puede continuar, ampliando el daño y exigiendo un mayor esfuerzo de remediación.",
    "evidence_loss": "La pérdida de evidencia dificulta la investigación y reduce la capacidad de atribución.",
    "miscommunication": "La falta de coordinación puede generar decisiones contradictorias y un impacto reputacional significativo.",
}
