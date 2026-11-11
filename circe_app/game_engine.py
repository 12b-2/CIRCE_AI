from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from circe_app.config import LevelScenario, ScenarioNode
from circe_app.knowledge.scenario import (
    START_NODE_ID,
    get_level_scenario,
    list_levels,
)


@dataclass
class DecisionOutcome:
    verdict: str
    score: float
    reason: str
    recommended_action: str
    xp_gained: int = 0
    next_node: str | None = None


class ScenarioEngine:
    """Motor de escenarios y niveles de CIRCE.
    Soporta múltiples niveles de campaña (level_1 a level_5) y múltiples nodos de decisión por nivel.
    """

    def __init__(self, level_id: str = "level_1") -> None:
        self.level_scenario: LevelScenario = get_level_scenario(level_id)
        self.current_node_id: str = self.level_scenario.start_node_id or START_NODE_ID
        self.history: list[dict[str, Any]] = []

    def select_level(self, level_id: str) -> LevelScenario:
        self.level_scenario = get_level_scenario(level_id)
        self.current_node_id = self.level_scenario.start_node_id
        self.history = []
        return self.level_scenario

    def get_all_levels(self) -> list[LevelScenario]:
        return list_levels()

    def get_current_node(self) -> ScenarioNode:
        return self.level_scenario.nodes[self.current_node_id]

    def get_ordered_nodes(self) -> list[ScenarioNode]:
        return sorted(self.level_scenario.nodes.values(), key=lambda n: n.level_number)

    def advance(self, node_id: str | None) -> bool:
        if node_id and node_id in self.level_scenario.nodes:
            self.current_node_id = node_id
            return True
        return False

    def record_result(self, result: dict[str, Any]) -> None:
        self.history.append(result)

    def summarize(self) -> dict[str, Any]:
        node = self.get_current_node()
        return {
            "level_id": self.level_scenario.id,
            "level_title": self.level_scenario.title,
            "current_node": self.current_node_id,
            "node_prompt": node.prompt,
            "history": self.history,
        }
