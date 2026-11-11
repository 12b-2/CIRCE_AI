from __future__ import annotations

import asyncio

from circe_app.orchestrator import CIRCEOrchestrator


class LocalConsoleUI:
    def __init__(self, level_id: str = "level_1") -> None:
        self.orchestrator = CIRCEOrchestrator(level_id=level_id)

    async def run_scenario(self) -> dict:
        scenario = self.orchestrator.engine.level_scenario
        print("\n=== CIRCE · Entrenamiento Interactivo por Voz y Texto ===")
        print(f"Escenario: {scenario.title}")
        print("Objetivo: responder a los 5 niveles de decisión (escribe '/voz' para grabar con micrófono).")

        while True:
            active = self.orchestrator.get_active_node()
            print(f"\n--- {active.title} ---")
            print(active.prompt)
            self.orchestrator.speak_current_instructions(blocking=False)

            choice = input("Tu decisión (texto o '/voz') > ").strip()
            if choice.lower() in ("/voz", "voz", "/mic"):
                print("Grabando voz desde el micrófono (6 segundos)...")
                choice = await self.orchestrator.capture_voice_turn(duration_seconds=6)
                print(f"Transcripción STT: {choice}")
                input_mode = "voice"
            else:
                input_mode = "text"

            result = await self.orchestrator.process_student_turn(
                choice,
                auto_advance=True,
                speak_response=True,
                input_mode=input_mode,
            )
            print("\n--- Evaluación del Modelo ---")
            print(result["narrator_response"])
            print(f"Puntaje acumulado: {result['score']} / 100 | XP: {result['xp']} | Vidas: {result['lives']}")

            if result["scenario_completed"]:
                print("\n¡Nivel completado! Se han finalizado las 5 decisiones del escenario.")
                return result


async def main() -> None:
    ui = LocalConsoleUI()
    await ui.run_scenario()


if __name__ == "__main__":
    asyncio.run(main())
