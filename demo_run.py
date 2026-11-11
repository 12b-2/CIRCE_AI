from __future__ import annotations

import asyncio

from circe_app.voice_pipeline import VoicePipeline


async def main() -> None:
    pipeline = VoicePipeline()
    result = await pipeline.process_voice_turn(
        user_text="Aíslo el servidor afectado y reviso los logs para confirmar el origen del acceso."
    )
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
