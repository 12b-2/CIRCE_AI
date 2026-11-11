from __future__ import annotations

import argparse
import asyncio

from circe_app.orchestrator import CIRCEOrchestrator


async def main() -> None:
    parser = argparse.ArgumentParser(description="CIRCE · Simulador de Ciberseguridad por Voz e IA")
    parser.add_argument(
        "--demo-text",
        type=str,
        default=None,
        help="Texto de prueba para simular la respuesta del estudiante",
    )
    parser.add_argument(
        "--mic",
        action="store_true",
        help="Usar micrófono para grabar audio",
    )
    parser.add_argument(
        "--level",
        type=str,
        default="level_1",
        help="ID del nivel a ejecutar (level_1 a level_5)",
    )
    parser.add_argument(
        "--gui",
        action="store_true",
        help="Iniciar la interfaz gráfica interactiva (5 niveles con voz y texto)",
    )
    args = parser.parse_args()

    if args.gui:
        from circe_app.ui.gui_app import main as gui_main

        gui_main()
        return

    orchestrator = CIRCEOrchestrator(level_id=args.level)
    orchestrator.speak_current_instructions(blocking=False)

    if args.mic:
        transcript = await orchestrator.capture_voice_turn()
    else:
        transcript = args.demo_text or "Reviso los registros de acceso y aíslo el sistema afectado."

    result = await orchestrator.process_student_turn(transcript)
    print("\n=== RESULTADO ===")
    print(result["narrator_response"])
    print(f"Puntaje: {result['score']} | XP: {result['xp']} | Siguiente nodo: {result['current_node']}")


if __name__ == "__main__":
    asyncio.run(main())
