from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class SessionState:
    active_node: str = "node_1"
    scenario_completed: bool = False
    score: float = 0.0
    attempts: int = 0
    transcript: list[dict[str, Any]] = field(default_factory=list)
    feedback: list[str] = field(default_factory=list)

    def add_turn(self, turn: dict[str, Any]) -> None:
        self.transcript.append(turn)

    def update_score(self, points: float) -> None:
        self.score = round(max(0.0, min(100.0, self.score + points * 100)), 2)

    def mark_complete(self) -> None:
        self.scenario_completed = True
