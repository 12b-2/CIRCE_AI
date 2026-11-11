from __future__ import annotations

import asyncio

from circe_app.knowledge.scenario import SCENARIO_TREE
from circe_app.orchestrator import CIRCEOrchestrator


class LocalConsoleUI:
    def __init__(self) -> None:
        self.orchestrator = CIRCEOrchestrator()

    async def run_scenario(self) -> dict:
        print("\n=== CIRCE MVP ===")
        print("Escenario: Filtración de datos corporativos")
        print("Objetivo: responder correctamente a 3 nodos de decisión sobre un incidente de seguridad.")

        while True:
            active = SCENARIO_TREE[self.orchestrator.current_node]
            print(f"\n--- Nodo actual: {active.title} ---")
            print(active.prompt)

            choice = input("Tu decisión > ")
            result = await self.orchestrator.process_student_turn(choice)
            print("\n--- Resultado ---")
            print(result["narrator_response"])
            print(f"Puntaje acumulado: {result['score']} / 100")

            if result["scenario_completed"]:
                print("\nEscenario completado. Se ha finalizado la simulación.")
                return result


async def main() -> None:
    ui = LocalConsoleUI()
    await ui.run_scenario()


if __name__ == "__main__":
    asyncio.run(main())
