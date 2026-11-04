import asyncio
from uuid import UUID

from ai_research.crew_service import run_research
from ai_research.event_manager import EventManager


async def execute_research(
    topic: str,
    run_id: UUID,
    manager: EventManager,
) -> str:
    loop = asyncio.get_running_loop()
    return await asyncio.to_thread(run_research, topic, run_id, manager, loop)
