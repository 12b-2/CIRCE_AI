from __future__ import annotations

from typing import Any

from circe_app.audio.stt import SpeechToText
from circe_app.audio.tts import TextToSpeech
from circe_app.evaluator import DecisionValidator
from circe_app.knowledge.scenario import SCENARIO_TREE


class VoicePipeline:
    def __init__(self) -> None:
        self.stt = SpeechToText(model="tiny")
        self.tts = TextToSpeech(engine_name="pyttsx3")
        self.validator = DecisionValidator()

    async def process_voice_turn(self, user_text: str | None = None, audio_path: str | None = None) -> dict[str, Any]:
        if user_text is None:
            if audio_path is None:
                raise ValueError("Debe proporcionar texto o archivo de audio.")
            user_text = await self.stt.transcribe(audio_path=audio_path)

        node = SCENARIO_TREE["node_1"]
        eval_result = self.validator.evaluate(
            user_text,
            node.prompt,
            node.correct_actions,
            node.partial_actions,
            node.wrong_actions,
        )

        narration = (
            f"Narrador: {node.prompt} "
            f"Tu decisión fue {eval_result['verdict']}. "
            f"{eval_result['reason']} "
            f"Recomendación: {eval_result['recommended_action']}"
        )

        try:
            self.tts.speak(narration)
        except Exception:
            pass

        return {
            "transcript": user_text,
            "evaluation": eval_result,
            "narration": narration,
        }
