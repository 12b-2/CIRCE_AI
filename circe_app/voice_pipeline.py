from __future__ import annotations

from typing import Any

from circe_app.orchestrator import CIRCEOrchestrator


class VoicePipeline:
    """Pipeline unificado de voz + evaluación + respuesta para CIRCE."""

    def __init__(self, level_id: str = "level_1") -> None:
        self.orchestrator = CIRCEOrchestrator(level_id=level_id)
        self.stt = self.orchestrator.stt
        self.tts = self.orchestrator.tts
        self.validator = self.orchestrator.validator

    async def process_voice_turn(
        self,
        user_text: str | None = None,
        audio_path: str | None = None,
    ) -> dict[str, Any]:
        if user_text is None:
            if audio_path is None:
                raise ValueError("Debe proporcionar texto o archivo de audio.")
            user_text = await self.stt.transcribe(audio_path=audio_path)

        result = await self.orchestrator.process_student_turn(
            student_text=user_text,
            auto_advance=True,
            speak_response=True,
            input_mode="voice" if audio_path else "text",
        )
        return {
            "transcript": user_text,
            "evaluation": result["evaluation"],
            "narration": result["narrator_response"],
            "spoken_feedback": result["spoken_feedback"],
            "current_node": result["current_node"],
            "score": result["score"],
        }
