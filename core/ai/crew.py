"""Xerppy AI Core Crew Implementation.

This module implements the Xerppy AI Core using CrewAI v1.9+ Flows architecture
with the @CrewBase decorator pattern.
"""

# mypy: ignore-errors
# pyright: reportCallIssue=false, reportArgumentType=false

from __future__ import annotations

from typing import Any

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

from core.ai.llm_factory import LLMFactory


@CrewBase
class XerppyCrew:
    """Xerppy AI Core Crew implementation using CrewAI v1.9+ Flows architecture."""

    agents_config: dict[str, Any] = {}
    tasks_config: dict[str, Any] = {}

    @agent
    def strategist(self) -> Agent:
        """Create the AI Strategy Architect agent with dynamic LLM injection."""
        conf: dict[str, Any] = self.agents_config["strategist"]
        llm = LLMFactory.create_llm(
            conf["llm_config"]["provider"],
            conf["llm_config"]["model"]
        )
        return Agent(config=conf, llm=llm)

    @agent
    def writer(self) -> Agent:
        """Create the Content Strategist & Writer agent with dynamic LLM injection."""
        conf: dict[str, Any] = self.agents_config["writer"]
        llm = LLMFactory.create_llm(
            conf["llm_config"]["provider"],
            conf["llm_config"]["model"]
        )
        return Agent(config=conf, llm=llm)

    @agent
    def privacy_officer(self) -> Agent:
        """Create the AI Privacy & Compliance Officer agent with dynamic LLM injection."""
        conf: dict[str, Any] = self.agents_config["privacy_officer"]
        llm = LLMFactory.create_llm(
            conf["llm_config"]["provider"],
            conf["llm_config"]["model"]
        )
        return Agent(config=conf, llm=llm)

    @task
    def strategic_analysis_task(self) -> Task:
        """Create the strategic analysis task."""
        config: dict[str, Any] = self.tasks_config["strategic_analysis_task"]
        return Task(description=config.get("description", ""), expected_output=config.get("expected_output", ""))

    @task
    def content_creation_task(self) -> Task:
        """Create the content creation task."""
        config: dict[str, Any] = self.tasks_config["content_creation_task"]
        return Task(description=config.get("description", ""), expected_output=config.get("expected_output", ""))

    @task
    def privacy_assessment_task(self) -> Task:
        """Create the privacy assessment task."""
        config: dict[str, Any] = self.tasks_config["privacy_assessment_task"]
        return Task(description=config.get("description", ""), expected_output=config.get("expected_output", ""))

    @crew
    def crew(self) -> Crew:
        """Create the Xerppy AI Core Crew."""
        return Crew(
            agents=[
                self.strategist(),
                self.writer(),
                self.privacy_officer()
            ],
            tasks=[
                self.strategic_analysis_task(),
                self.content_creation_task(),
                self.privacy_assessment_task()
            ],
            process=Process.sequential,
            verbose=True
        )
