import unittest

from ai_research.crew_service import _plain_text_report


class PlainTextReportTests(unittest.TestCase):
    def test_removes_markdown_while_preserving_headings_bullets_and_sources(self) -> None:
        report = (
            "## 1. **Forecasting**\n"
            "AI improves forecasts. See [Open Climate Fix](https://example.com).\n"
            "* Better local predictions\n"
            "`source data`"
        )

        self.assertEqual(
            _plain_text_report(report),
            "1. Forecasting\n"
            "AI improves forecasts. See Open Climate Fix: https://example.com.\n"
            "- Better local predictions\n"
            "source data",
        )


if __name__ == "__main__":
    unittest.main()
