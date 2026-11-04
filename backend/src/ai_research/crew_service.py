import asyncio
import logging
import os
import re
from contextvars import ContextVar
from pathlib import Path
from typing import Any
from uuid import UUID

from dotenv import load_dotenv

_BACKEND_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(_BACKEND_ROOT / ".env")

from crewai.events import crewai_event_bus
from crewai.events.base_event_listener import BaseEventListener
from crewai.events.types.task_events import TaskCompletedEvent, TaskStartedEvent

from ai_research.crew import AiResearch
from ai_research.event_manager import EventManager

logger = logging.getLogger(__name__)
_active_run: ContextVar[tuple[UUID, asyncio.AbstractEventLoop, EventManager] | None] = (
    ContextVar("active_research_run", default=None)
)
_AGENT_NAMES = {
    "Research Analyst": "Research Analyst",
    "Fact Checker": "Fact Checker",
    "Content Writer": "Content Writer",
}


class _CrewProgressListener(BaseEventListener):
    def setup_listeners(self, event_bus: Any) -> None:
        @event_bus.on(TaskStartedEvent)
        def on_task_started(_source: Any, event: TaskStartedEvent) -> None:
            self._publish_task_event(event, "agent_started", "working")

        @event_bus.on(TaskCompletedEvent)
        def on_task_completed(_source: Any, event: TaskCompletedEvent) -> None:
            self._publish_task_event(event, "agent_completed", "completed")

    @staticmethod
    def _publish_task_event(event: Any, event_name: str, status: str) -> None:
        active_run = _active_run.get()
        if active_run is None:
            return

        run_id, loop, manager = active_run
        agent_role = event.agent_role
        if not agent_role and event.task is not None:
            agent_role = getattr(getattr(event.task, "agent", None), "role", None)
        agent = _AGENT_NAMES.get(agent_role)
        if agent is None:
            logger.warning("Ignoring progress event for unrecognized agent role %r", agent_role)
            return

        event_data = {
            "event": event_name,
            "run_id": str(run_id),
            "agent": agent,
            "status": status,
        }
        future = asyncio.run_coroutine_threadsafe(
            manager.publish(run_id, event_data),
            loop,
        )
        future.result()


_progress_listener = _CrewProgressListener()


def _plain_text_report(report: str) -> str:
    report = re.sub(r"(?m)^\s{0,3}#{1,6}\s+", "", report)
    report = re.sub(
        r"\[([^\]]+)\]\((https?://[^)\s]+)\)",
        r"\1: \2",
        report,
    )
    report = re.sub(r"\*\*(.+?)\*\*", r"\1", report)
    report = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"\1", report)
    report = re.sub(r"`([^`\n]+)`", r"\1", report)
    report = re.sub(r"(?m)^\s*[-*]\s+", "- ", report)
    return report.strip()


def run_research(
    topic: str,
    run_id: UUID,
    manager: EventManager,
    loop: asyncio.AbstractEventLoop,
) -> str:
    if not os.getenv("OPENROUTER_API_KEY"):
        raise RuntimeError("OPENROUTER_API_KEY is not configured in backend/.env.")
    if not os.getenv("SERPER_API_KEY"):
        raise RuntimeError("SERPER_API_KEY is not configured in backend/.env.")

    model = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")
    token = _active_run.set((run_id, loop, manager))
    try:
        result = AiResearch(model=model).crew().kickoff(inputs={"topic": topic})
        if not result.tasks_output:
            raise RuntimeError("The research workflow returned no task output.")
        report = _plain_text_report(result.tasks_output[-1].raw)
        if not report:
            raise RuntimeError("The Content Writer returned an empty report.")
        if (
            "saved as" in report.casefold()
            and len(report.split()) < 50
        ):
            raise RuntimeError(
                "The Content Writer returned a file-save confirmation instead of the report."
            )
        return report
    finally:
        _active_run.reset(token)
