from __future__ import annotations

from typing import Any

from circe_app.ai.llm_client import LLMClient
from circe_app.audio.stt import SpeechToText
from circe_app.audio.tts import TextToSpeech
from circe_app.config import CIRCEConfig, DEFAULT_CONFIG, ScenarioNode
from circe_app.evaluator import DecisionValidator
from circe_app.game_engine import ScenarioEngine
from circe_app.session import SessionState


class CIRCEOrchestrator:
    """Orquestador central de CIRCE.
    Coordina los 5 niveles del escenario, la captura de voz (STT), la síntesis de voz (TTS),
    el modelo de lenguaje local (Ollama LLM) y el validador semántico de respaldo.
    """

    def __init__(self, config: CIRCEConfig | None = None, level_id: str | None = None) -> None:
        self.config = config or DEFAULT_CONFIG
        selected_level = level_id or self.config.default_level_id
        self.engine = ScenarioEngine(level_id=selected_level)
        self.stt = SpeechToText(
            model=self.config.stt_model,
            sample_rate=self.config.audio_sample_rate,
            language=self.config.voice_language,
        )
        self.tts = TextToSpeech(
            engine_name=self.config.tts_engine,
            rate=self.config.tts_rate,
        )
        self.llm = LLMClient(
            base_url=self.config.llm_base_url,
            model=self.config.llm_model,
            timeout=self.config.llm_timeout_seconds,
        )
        self.validator = DecisionValidator()
        self.current_node = self.engine.current_node_id
        self.history: list[dict[str, Any]] = []
        self.session = SessionState(
            level_id=selected_level,
            active_node=self.current_node,
        )

    def select_level(self, level_id: str) -> None:
        """Cambia o reinicia a uno de los 5 niveles disponibles."""
        self.tts.stop()
        scenario = self.engine.select_level(level_id)
        self.current_node = scenario.start_node_id
        self.history = []
        self.session = SessionState(
            level_id=scenario.id,
            active_node=self.current_node,
        )

    def get_active_node(self) -> ScenarioNode:
        return self.engine.level_scenario.nodes[self.current_node]

    def get_ordered_nodes(self) -> list[ScenarioNode]:
        return self.engine.get_ordered_nodes()

    def speak_current_instructions(self, blocking: bool = False) -> None:
        """Narra por voz las instrucciones del nivel/nodo activo."""
        node = self.get_active_node()
        text = f"{node.title}. {node.prompt}"
        try:
            self.tts.speak(text, blocking=blocking)
        except Exception:
            pass

    def speak_text(self, text: str, blocking: bool = False) -> None:
        """Narra cualquier texto en voz alta de forma segura."""
        try:
            self.tts.speak(text, blocking=blocking)
        except Exception:
            pass

    async def capture_voice_turn(self, duration_seconds: int = 6) -> str:
        self.tts.stop()
        transcript = await self.stt.capture_microphone(duration_seconds=duration_seconds)
        self.history.append({"type": "user_voice", "content": transcript, "node": self.current_node})
        self.session.add_turn({"type": "user_voice", "content": transcript, "node": self.current_node})
        return transcript

    async def evaluate_node_decision(self, node: ScenarioNode, student_text: str) -> dict[str, Any]:
        """Evalúa la respuesta usando el LLM local (si está activo) o el Evaluador Semántico Local."""
        if self.llm.is_available():
            try:
                evaluation = await self.llm.evaluate_action(
                    user_text=student_text,
                    node_prompt=node.prompt,
                    correct_actions=node.correct_actions,
                    partial_actions=node.partial_actions,
                    wrong_actions=node.wrong_actions,
                )
                evaluation["engine_used"] = f"LLM ({self.llm.model})"
                return evaluation
            except Exception:
                pass

        evaluation = self.validator.evaluate(
            user_text=student_text,
            node_prompt=node.prompt,
            correct_actions=node.correct_actions,
            partial_actions=node.partial_actions,
            wrong_actions=node.wrong_actions,
            keywords_correct=node.keywords_correct,
            keywords_partial=node.keywords_partial,
            keywords_wrong=node.keywords_wrong,
        )
        evaluation["engine_used"] = "Evaluador Semántico Local"
        return evaluation

    def advance_to_next_node(self) -> bool:
        """Avanza al siguiente nodo de los 5 niveles. Devuelve True si avanzó o False si completó el escenario."""
        node = self.get_active_node()
        next_node = node.next_node
        if next_node and next_node in self.engine.level_scenario.nodes:
            self.current_node = next_node
            self.engine.advance(next_node)
            self.session.active_node = next_node
            return True
        self.session.mark_complete()
        return False

    async def process_student_turn(
        self,
        student_text: str,
        auto_advance: bool = True,
        speak_response: bool = True,
        input_mode: str = "text",
    ) -> dict[str, Any]:
        node = self.get_active_node()
        evaluated_node_id = node.id
        evaluation = await self.evaluate_node_decision(node, student_text)

        verdict = evaluation.get("verdict", "partial")
        verdict_es = {
            "correct": "correcta",
            "partial": "parcialmente correcta",
            "wrong": "incorrecta",
        }.get(verdict, "parcialmente correcta")

        total_nodes = len(self.engine.level_scenario.nodes)
        self.session.attempts += 1
        xp_gained = self.session.update_score(
            float(evaluation.get("score", 0.0)),
            verdict=verdict,
            total_nodes=total_nodes,
        )
        evaluation["xp_gained"] = xp_gained

        record = {
            "type": "evaluation",
            "node": evaluated_node_id,
            "level_number": node.level_number,
            "node_title": node.title,
            "student_text": student_text,
            "input_mode": input_mode,
            "content": evaluation,
        }
        self.history.append(record)
        self.session.add_turn(record)
        self.session.node_results[evaluated_node_id] = record
        self.engine.record_result(record)

        spoken_feedback = (
            f"Tu decisión en el {node.title} fue {verdict_es}. "
            f"{evaluation.get('reason', '')} "
            f"{evaluation.get('recommended_action', '')}"
        )
        response_text = (
            f"Narrador ({node.title}): {node.prompt}\n\n"
            f"Tu respuesta fue evaluada como: {verdict_es} (+{xp_gained} XP).\n"
            f"{evaluation.get('reason', '')}\n"
            f"Acción recomendada: {evaluation.get('recommended_action', '')}"
        )

        if speak_response and self.config.auto_speak_feedback:
            self.speak_text(spoken_feedback, blocking=False)

        if auto_advance:
            self.advance_to_next_node()

        return {
            "evaluated_node": evaluated_node_id,
            "current_node": self.current_node,
            "node_prompt": self.get_active_node().prompt,
            "evaluation": evaluation,
            "history": self.history,
            "narrator_response": response_text,
            "spoken_feedback": spoken_feedback,
            "score": self.session.score,
            "xp": self.session.xp,
            "lives": self.session.lives,
            "scenario_completed": self.session.scenario_completed,
        }
