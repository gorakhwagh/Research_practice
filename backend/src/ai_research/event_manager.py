import asyncio
import json
import logging
from collections.abc import AsyncIterator
from datetime import datetime, timedelta, timezone
from uuid import UUID

from sse_starlette.sse import EventSourceResponse

logger = logging.getLogger(__name__)
_TERMINAL_EVENTS = {"run_completed", "run_failed"}
_HISTORY_TTL = timedelta(hours=1)


class EventManager:
    def __init__(self) -> None:
        self._queues: dict[UUID, set[asyncio.Queue[dict[str, str] | None]]] = {}
        self._history: dict[UUID, list[dict[str, str]]] = {}
        self._finished_at: dict[UUID, datetime] = {}
        self._lock = asyncio.Lock()

    async def publish(self, run_id: UUID, event: dict[str, str]) -> None:
        async with self._lock:
            self._prune_expired_runs()
            history = self._history.setdefault(run_id, [])
            history.append(event)
            for queue in self._queues.get(run_id, set()):
                queue.put_nowait(event)
            if event["event"] in _TERMINAL_EVENTS:
                self._finished_at[run_id] = datetime.now(timezone.utc)
                for queue in self._queues.get(run_id, set()):
                    queue.put_nowait(None)

    async def stream(self, run_id: UUID) -> AsyncIterator[dict[str, str]]:
        queue: asyncio.Queue[dict[str, str] | None] = asyncio.Queue()
        async with self._lock:
            self._prune_expired_runs()
            self._queues.setdefault(run_id, set()).add(queue)
            replay = list(self._history.get(run_id, []))
            finished = run_id in self._finished_at

        try:
            for event in replay:
                yield self._as_sse_message(event)
            if finished:
                return

            while True:
                event = await queue.get()
                if event is None:
                    return
                yield self._as_sse_message(event)
        finally:
            await self.disconnect(run_id, queue)

    async def disconnect(
        self,
        run_id: UUID,
        queue: asyncio.Queue[dict[str, str] | None],
    ) -> None:
        async with self._lock:
            clients = self._queues.get(run_id)
            if clients is not None:
                clients.discard(queue)
                if not clients:
                    self._queues.pop(run_id, None)

    @staticmethod
    def _as_sse_message(event: dict[str, str]) -> dict[str, str]:
        return {
            "event": event["event"],
            "data": json.dumps(event),
        }

    def _prune_expired_runs(self) -> None:
        cutoff = datetime.now(timezone.utc) - _HISTORY_TTL
        expired = [
            run_id
            for run_id, finished_at in self._finished_at.items()
            if finished_at < cutoff and run_id not in self._queues
        ]
        for run_id in expired:
            self._finished_at.pop(run_id, None)
            self._history.pop(run_id, None)
            logger.debug("Expired progress history for run %s", run_id)


event_manager = EventManager()


def event_stream_response(run_id: UUID) -> EventSourceResponse:
    return EventSourceResponse(
        event_manager.stream(run_id),
        ping=15,
        send_timeout=30,
    )
