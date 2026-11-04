import asyncio
import os
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch
from uuid import uuid4

from ai_research.crew_service import run_research
from ai_research.event_manager import EventManager


class CrewServiceTests(unittest.TestCase):
    def run_with_output(self, raw: str) -> tuple[str | None, Mock]:
        crew = Mock()
        crew.kickoff.return_value = SimpleNamespace(
            tasks_output=[SimpleNamespace(raw=raw)]
        )
        crew_factory = Mock()
        crew_factory.return_value.crew.return_value = crew
        loop = asyncio.new_event_loop()
        try:
            with (
                patch.dict(
                    os.environ,
                    {
                        "OPENROUTER_API_KEY": "test-openrouter-key",
                        "SERPER_API_KEY": "test-serper-key",
                    },
                ),
                patch("ai_research.crew_service.AiResearch", crew_factory),
            ):
                report = run_research(
                    "AI forecasting",
                    uuid4(),
                    EventManager(),
                    loop,
                )
            return report, crew
        finally:
            loop.close()

    def test_returns_normalized_final_task_output(self) -> None:
        report, crew = self.run_with_output(
            "## 1. **Findings**\n"
            "AI improves forecasting. See [Source](https://example.com).\n"
            "- Better predictions"
        )

        self.assertEqual(
            report,
            "1. Findings\n"
            "AI improves forecasting. See Source: https://example.com.\n"
            "- Better predictions",
        )
        crew.kickoff.assert_called_once_with(inputs={"topic": "AI forecasting"})

    def test_rejects_file_save_confirmation_as_report(self) -> None:
        with self.assertRaisesRegex(RuntimeError, "file-save confirmation"):
            self.run_with_output(
                "The report has been successfully created and saved as report.txt."
            )


if __name__ == "__main__":
    unittest.main()
