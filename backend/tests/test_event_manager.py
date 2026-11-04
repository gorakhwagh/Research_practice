import asyncio
import unittest
from uuid import uuid4

from ai_research.event_manager import EventManager


class EventManagerTests(unittest.TestCase):
    def test_stream_receives_live_events_and_closes_on_terminal_event(self) -> None:
        async def exercise() -> None:
            manager = EventManager()
            run_id = uuid4()
            stream = manager.stream(run_id)
            pending_event = asyncio.create_task(anext(stream))
            await asyncio.sleep(0)

            await manager.publish(
                run_id,
                {"event": "agent_started", "agent": "Research Analyst"},
            )
            message = await asyncio.wait_for(pending_event, timeout=1)
            self.assertEqual(message["event"], "agent_started")
            self.assertIn("Research Analyst", message["data"])

            await manager.publish(
                run_id,
                {"event": "run_completed", "run_id": str(run_id)},
            )
            terminal_event = await asyncio.wait_for(anext(stream), timeout=1)
            self.assertEqual(terminal_event["event"], "run_completed")
            with self.assertRaises(StopAsyncIteration):
                await asyncio.wait_for(anext(stream), timeout=1)

        asyncio.run(exercise())

    def test_finished_run_replays_events_to_late_subscriber(self) -> None:
        async def exercise() -> None:
            manager = EventManager()
            run_id = uuid4()
            await manager.publish(
                run_id,
                {"event": "agent_completed", "agent": "Fact Checker"},
            )
            await manager.publish(
                run_id,
                {"event": "run_completed", "run_id": str(run_id)},
            )

            events = [event async for event in manager.stream(run_id)]
            self.assertEqual(
                [event["event"] for event in events],
                ["agent_completed", "run_completed"],
            )

        asyncio.run(exercise())


if __name__ == "__main__":
    unittest.main()
