from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class SessionState:
    level_id: str = "level_1"
    active_node: str = "node_1"
    scenario_completed: bool = False
    score: float = 0.0
    xp: int = 0
    lives: int = 3
    max_lives: int = 3
    attempts: int = 0
    containment: int = 35
    data_safety: int = 50
    service_health: int = 60
    start_timestamp: float = field(default_factory=time.time)
    transcript: list[dict[str, Any]] = field(default_factory=list)
    feedback: list[str] = field(default_factory=list)
    node_results: dict[str, dict[str, Any]] = field(default_factory=dict)

    def add_turn(self, turn: dict[str, Any]) -> None:
        self.transcript.append(turn)

    def update_score(self, points: float, verdict: str = "partial", total_nodes: int = 5) -> int:
        # Escalado para 5 niveles de decisión (máximo 100 puntos)
        increment = (points * (100.0 / max(1, total_nodes)))
        self.score = round(max(0.0, min(100.0, self.score + increment)), 1)

        if verdict == "correct":
            xp_gained = 20
            self.containment = min(100, self.containment + 15)
            self.data_safety = min(100, self.data_safety + 12)
            self.service_health = min(100, self.service_health + 10)
        elif verdict == "partial":
            xp_gained = 10
            self.containment = min(100, self.containment + 6)
            self.data_safety = min(100, self.data_safety + 4)
            self.service_health = max(10, self.service_health - 2)
        else:
            xp_gained = 0
            self.lives = max(0, self.lives - 1)
            self.containment = max(5, self.containment - 12)
            self.data_safety = max(5, self.data_safety - 15)
            self.service_health = max(5, self.service_health - 12)

        self.xp += xp_gained
        return xp_gained

    def mark_complete(self) -> None:
        self.scenario_completed = True

    def elapsed_formatted(self) -> str:
        elapsed = max(0, int(time.time() - self.start_timestamp))
        minutes, seconds = divmod(elapsed, 60)
        return f"{minutes:02d}:{seconds:02d}"
