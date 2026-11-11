from __future__ import annotations

import argparse
import asyncio

from circe_app.orchestrator import CIRCEOrchestrator


async def main() -> None:
    parser = argparse.ArgumentParser(description="CIRCE MVP")
    parser.add_argument("--demo-text", type=str, default=None, help="Texto de prueba para simular la respuesta del estudiante")
    parser.add_argument("--mic", action="store_true", help="Usar micrófono para grabar audio")
    args = parser.parse_args()

    orchestrator = CIRCEOrchestrator()

    if args.mic:
        transcript = await orchestrator.capture_voice_turn()
    else:
        transcript = args.demo_text or "Reviso los registros de acceso y aíslo el sistema afectado."

    result = await orchestrator.process_student_turn(transcript)
    print("\n=== RESULTADO ===")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
