from __future__ import annotations

import json
import time

from circe_app.auth.database import get_connection
from circe_app.session import SessionState


class ProgressStore:
    """Guarda y recupera el avance (score, XP, vidas, nodo activo) por usuario y nivel."""

    def save_progress(self, user_id: int, session: SessionState) -> None:
        record = session.to_record()
        connection = get_connection()
        try:
            connection.execute(
                """
                INSERT INTO progress (
                    user_id, level_id, active_node, scenario_completed, score, xp,
                    lives, max_lives, attempts, containment, data_safety, service_health,
                    node_results, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(user_id, level_id) DO UPDATE SET
                    active_node=excluded.active_node,
                    scenario_completed=excluded.scenario_completed,
                    score=excluded.score,
                    xp=excluded.xp,
                    lives=excluded.lives,
                    max_lives=excluded.max_lives,
                    attempts=excluded.attempts,
                    containment=excluded.containment,
                    data_safety=excluded.data_safety,
                    service_health=excluded.service_health,
                    node_results=excluded.node_results,
                    updated_at=excluded.updated_at
                """,
                (
                    user_id,
                    record["level_id"],
                    record["active_node"],
                    int(record["scenario_completed"]),
                    record["score"],
                    record["xp"],
                    record["lives"],
                    record["max_lives"],
                    record["attempts"],
                    record["containment"],
                    record["data_safety"],
                    record["service_health"],
                    json.dumps(record["node_results"]),
                    time.time(),
                ),
            )
            connection.commit()
        finally:
            connection.close()

    def load_progress(self, user_id: int, level_id: str) -> SessionState | None:
        connection = get_connection()
        try:
            row = connection.execute(
                "SELECT * FROM progress WHERE user_id = ? AND level_id = ?",
                (user_id, level_id),
            ).fetchone()
        finally:
            connection.close()

        if row is None:
            return None

        return SessionState.from_record(
            {
                "level_id": row["level_id"],
                "active_node": row["active_node"],
                "scenario_completed": bool(row["scenario_completed"]),
                "score": row["score"],
                "xp": row["xp"],
                "lives": row["lives"],
                "max_lives": row["max_lives"],
                "attempts": row["attempts"],
                "containment": row["containment"],
                "data_safety": row["data_safety"],
                "service_health": row["service_health"],
                "node_results": json.loads(row["node_results"]),
            }
        )

    def get_completed_levels(self, user_id: int) -> dict[str, float]:
        connection = get_connection()
        try:
            rows = connection.execute(
                "SELECT level_id, score FROM progress WHERE user_id = ? AND scenario_completed = 1",
                (user_id,),
            ).fetchall()
        finally:
            connection.close()
        return {row["level_id"]: row["score"] for row in rows}

    def get_all_progress(self, user_id: int) -> dict[str, dict]:
        """Devuelve el avance de TODOS los niveles (completados o en progreso) de un usuario."""
        connection = get_connection()
        try:
            rows = connection.execute(
                "SELECT level_id, active_node, scenario_completed, score, xp FROM progress WHERE user_id = ?",
                (user_id,),
            ).fetchall()
        finally:
            connection.close()
        return {
            row["level_id"]: {
                "active_node": row["active_node"],
                "scenario_completed": bool(row["scenario_completed"]),
                "score": row["score"],
                "xp": row["xp"],
            }
            for row in rows
        }
