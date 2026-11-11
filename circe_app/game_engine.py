from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from circe_app.knowledge.scenario import SCENARIO_TREE, START_NODE_ID


@dataclass
class DecisionOutcome:
    verdict: str
    score: float
    reason: str
    recommended_action: str
    next_node: str | None = None


class ScenarioEngine:
    def __init__(self) -> None:
        self.current_node_id = START_NODE_ID
        self.history: list[dict[str, Any]] = []

    def get_current_node(self):
        return SCENARIO_TREE[self.current_node_id]

    def advance(self, node_id: str | None) -> None:
        if node_id:
            self.current_node_id = node_id

    def record_result(self, result: dict[str, Any]) -> None:
        self.history.append(result)

    def summarize(self) -> dict[str, Any]:
        return {
            "current_node": self.current_node_id,
            "node_prompt": self.get_current_node().prompt,
            "history": self.history,
        }
