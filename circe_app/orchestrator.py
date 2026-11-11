from __future__ import annotations

from typing import Any

from circe_app.ai.llm_client import LLMClient
from circe_app.audio.stt import SpeechToText
from circe_app.audio.tts import TextToSpeech
from circe_app.evaluator import DecisionValidator
from circe_app.knowledge.scenario import SCENARIO_TREE, START_NODE_ID
from circe_app.session import SessionState


class CIRCEOrchestrator:
    def __init__(self) -> None:
        self.stt = SpeechToText(model="tiny")
        self.tts = TextToSpeech(engine_name="pyttsx3")
        self.llm = LLMClient(model="llama3.1")
        self.validator = DecisionValidator()
        self.current_node = START_NODE_ID
        self.history: list[dict[str, Any]] = []
        self.session = SessionState(active_node=START_NODE_ID)

    async def capture_voice_turn(self) -> str:
        transcript = await self.stt.capture_microphone()
        self.history.append({"type": "user_voice", "content": transcript})
        self.session.add_turn({"type": "user_voice", "content": transcript})
        return transcript

    async def process_student_turn(self, student_text: str) -> dict[str, Any]:
        node = SCENARIO_TREE[self.current_node]
        evaluation = None

        try:
            evaluation = await self.llm.evaluate_action(
                user_text=student_text,
                node_prompt=node.prompt,
                correct_actions=node.correct_actions,
                partial_actions=node.partial_actions,
                wrong_actions=node.wrong_actions,
            )
        except Exception:
            evaluation = self.validator.evaluate(
                student_text,
                node.prompt,
                node.correct_actions,
                node.partial_actions,
                node.wrong_actions,
            )

        self.history.append({"type": "evaluation", "content": evaluation, "node": self.current_node})
        self.session.add_turn({"type": "evaluation", "content": evaluation, "node": self.current_node})
        self.session.attempts += 1
        self.session.update_score(float(evaluation.get("score", 0.0)))

        response_text = (
            f"Narrador: {node.prompt}\n\n"
            f"Tu respuesta fue evaluada como: {evaluation.get('verdict', 'partial')}. "
            f"{evaluation.get('reason', '')} "
            f"Acción recomendada: {evaluation.get('recommended_action', '')}"
        )

        try:
            self.tts.speak(response_text)
        except Exception:
            pass

        next_node = node.next_node
        if next_node:
            self.current_node = next_node
            self.session.active_node = next_node
        else:
            self.session.mark_complete()

        return {
            "current_node": self.current_node,
            "node_prompt": node.prompt,
            "evaluation": evaluation,
            "history": self.history,
            "narrator_response": response_text,
            "score": self.session.score,
            "scenario_completed": self.session.scenario_completed,
        }
