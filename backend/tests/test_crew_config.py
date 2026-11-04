import os
import unittest
from unittest.mock import patch

from ai_research.crew import AiResearch


class CrewConfigurationTests(unittest.TestCase):
    def test_all_agents_use_the_configured_openrouter_model(self) -> None:
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-openrouter-key"}):
            crew = AiResearch(model="openrouter/openai/gpt-4o-mini").crew()

        self.assertEqual(len(crew.agents), 3)
        self.assertEqual(len(crew.tasks), 3)
        self.assertEqual(
            [agent.llm.provider for agent in crew.agents],
            ["openrouter", "openrouter", "openrouter"],
        )
        self.assertEqual(
            [agent.llm.model for agent in crew.agents],
            ["openai/gpt-4o-mini"] * 3,
        )


if __name__ == "__main__":
    unittest.main()
