import os

from crewai import Agent, Crew, LLM, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import FileReadTool, FileWriterTool, ScrapeWebsiteTool, SerperDevTool


@CrewBase
class AiResearch:
    """Research, verify, and write a plain-text research report."""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    def __init__(self, model: str | None = None) -> None:
        configured_model = model or os.getenv(
            "OPENROUTER_MODEL",
            "openai/gpt-4o-mini",
        )
        self.model = configured_model.removeprefix("openrouter/")

    def _llm(self) -> LLM:
        return LLM(model=self.model, provider="openrouter")

    @agent
    def research_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config["research_analyst"],
            llm=self._llm(),
            tools=[
                SerperDevTool(),
                ScrapeWebsiteTool(),
                FileReadTool(),
                FileWriterTool(),
            ],
            allow_delegation=False,
            verbose=False,
        )

    @agent
    def fact_checker(self) -> Agent:
        return Agent(
            config=self.agents_config["fact_checker"],
            llm=self._llm(),
            tools=[SerperDevTool(), ScrapeWebsiteTool()],
            allow_delegation=False,
            verbose=False,
        )

    @agent
    def content_writer(self) -> Agent:
        return Agent(
            config=self.agents_config["content_writer"],
            llm=self._llm(),
            tools=[FileWriterTool()],
            allow_delegation=False,
            verbose=False,
        )

    @task
    def research_task(self) -> Task:
        return Task(config=self.tasks_config["research_task"])

    @task
    def fact_check_task(self) -> Task:
        return Task(config=self.tasks_config["fact_check_task"])

    @task
    def writing_task(self) -> Task:
        return Task(config=self.tasks_config["writing_task"])

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=False,
        )
