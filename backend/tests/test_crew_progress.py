import asyncio
import unittest
from types import SimpleNamespace
from uuid import uuid4

from ai_research.crew_service import _CrewProgressListener, _active_run
from ai_research.event_manager import EventManager


class CrewProgressTests(unittest.TestCase):
    def test_task_statuses_are_published_from_worker_thread(self) -> None:
        async def exercise() -> None:
            manager = EventManager()
            run_id = uuid4()
            loop = asyncio.get_running_loop()
            token = _active_run.set((run_id, loop, manager))
            stream = manager.stream(run_id)
            waiting_event = asyncio.create_task(anext(stream))
            await asyncio.sleep(0)

            try:
                await asyncio.to_thread(
                    _CrewProgressListener._publish_task_event,
                    SimpleNamespace(agent_role="Research Analyst"),
                    "agent_started",
                    "working",
                )
                started = await asyncio.wait_for(waiting_event, timeout=1)
                self.assertEqual(started["event"], "agent_started")
                self.assertIn("Research Analyst", started["data"])
                self.assertIn("working", started["data"])

                await asyncio.to_thread(
                    _CrewProgressListener._publish_task_event,
                    SimpleNamespace(agent_role="Research Analyst"),
                    "agent_completed",
                    "completed",
                )
                completed = await asyncio.wait_for(anext(stream), timeout=1)
                self.assertEqual(completed["event"], "agent_completed")
                self.assertIn("completed", completed["data"])

                await asyncio.to_thread(
                    _CrewProgressListener._publish_task_event,
                    SimpleNamespace(
                        agent_role=None,
                        task=SimpleNamespace(
                            agent=SimpleNamespace(role="Fact Checker")
                        ),
                    ),
                    "agent_started",
                    "working",
                )
                fact_checker = await asyncio.wait_for(anext(stream), timeout=1)
                self.assertIn("Fact Checker", fact_checker["data"])
            finally:
                await stream.aclose()
                _active_run.reset(token)

        asyncio.run(exercise())


if __name__ == "__main__":
    unittest.main()
