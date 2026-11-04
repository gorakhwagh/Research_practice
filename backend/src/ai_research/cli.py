import asyncio
import sys
from uuid import uuid4

from ai_research.event_manager import EventManager
from ai_research.services import execute_research


async def run(topic: str) -> str:
    return await execute_research(topic, uuid4(), EventManager())


def main() -> None:
    topic = " ".join(sys.argv[1:]).strip()
    if not topic:
        raise SystemExit('Usage: python -m ai_research.cli "Research topic"')
    print(asyncio.run(run(topic)))


if __name__ == "__main__":
    main()
