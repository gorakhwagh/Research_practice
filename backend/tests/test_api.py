import unittest
from unittest.mock import AsyncMock, patch
from uuid import uuid4

from fastapi.testclient import TestClient

from ai_research.event_manager import event_manager
from ai_research.main import app


class ResearchApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_root_reports_backend_health(self) -> None:
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    def test_research_returns_report_and_completes_run(self) -> None:
        run_id = uuid4()
        with patch(
            "ai_research.main.execute_research",
            new=AsyncMock(return_value="Verified report"),
        ) as execute:
            response = self.client.post(
                "/api/research",
                json={"topic": "  AI research  ", "run_id": str(run_id)},
            )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {
            "run_id": str(run_id),
            "report": "Verified report",
        })
        execute.assert_awaited_once()
        self.assertEqual(
            event_manager._history[run_id][-1]["event"],
            "run_completed",
        )

    def test_blank_topic_is_rejected(self) -> None:
        response = self.client.post(
            "/api/research",
            json={"topic": "   ", "run_id": str(uuid4())},
        )

        self.assertEqual(response.status_code, 422)

    def test_failed_research_returns_error_and_publishes_failure(self) -> None:
        run_id = uuid4()
        with patch(
            "ai_research.main.execute_research",
            new=AsyncMock(side_effect=RuntimeError("provider unavailable")),
        ):
            response = self.client.post(
                "/api/research",
                json={"topic": "AI research", "run_id": str(run_id)},
            )

        self.assertEqual(response.status_code, 502)
        self.assertEqual(
            event_manager._history[run_id][-1]["event"],
            "run_failed",
        )


if __name__ == "__main__":
    unittest.main()
