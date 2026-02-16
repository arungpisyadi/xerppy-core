"""CrewAI Manager for Xerppy ERP framework.

This module provides the CrewManager class for initializing and managing
CrewAI agents within the ERP system.
"""

from __future__ import annotations

import logging
import os
from collections.abc import Sequence
from typing import Any

from crewai import Agent, Crew, Task

logger = logging.getLogger(__name__)


class CrewManager:
    """Manager for CrewAI agents and crews in the Xerppy ERP system.

    This class provides methods to create, configure, and run CrewAI agents
    and crews for AI-powered ERP operations.

    Attributes:
        api_key: The CrewAI API key for authentication.

    Example:
        >>> manager = CrewManager()
        >>> agent = manager.create_agent(
        ...     role="Data Analyst",
        ...     goal="Analyze ERP data and provide insights",
        ...     backstory="You are an expert data analyst..."
        ... )
    """

    def __init__(self) -> None:
        """Initialize the CrewManager with API key from configuration.

        The API key is loaded from Flask config (CREWAI_API_KEY) with
        environment variable (CREWAI_API_KEY) as fallback.
        """
        self.api_key: str | None = self._load_api_key()
        self._crew: Crew | None = None

        if self.api_key:
            logger.info("CrewManager initialized with API key")
        else:
            logger.warning(
                "CrewManager initialized without API key. "
                "Set CREWAI_API_KEY in config or environment."
            )

    def _load_api_key(self) -> str | None:
        """Load the CrewAI API key from Flask config or environment variable.

        Returns:
            The API key if found, None otherwise.
        """
        # Try to get from Flask config first
        try:
            from flask import current_app

            api_key = current_app.config.get("CREWAI_API_KEY")
            if api_key:
                return api_key
        except Exception:
            # Flask app might not be available
            pass

        # Fallback to environment variable
        return os.environ.get("CREWAI_API_KEY")

    def create_agent(
        self,
        role: str,
        goal: str,
        backstory: str,
        tools: list[Any] | None = None,
    ) -> Agent:
        """Create a CrewAI agent with the specified configuration.

        Args:
            role: The role/title of the agent.
            goal: The goal the agent should achieve.
            backstory: The backstory/context for the agent.
            tools: Optional list of tools the agent can use.

        Returns:
            A configured CrewAI Agent instance.

        Example:
            >>> manager = CrewManager()
            >>> agent = manager.create_agent(
            ...     role="Data Analyst",
            ...     goal="Analyze sales data",
            ...     backstory="Expert in ERP data analysis",
            ...     tools=[DatabaseQueryTool()]
            ... )
        """
        logger.info(f"Creating agent with role: {role}")

        agent = Agent(
            role=role,
            goal=goal,
            backstory=backstory,
            tools=tools or [],
            verbose=True,
            allow_delegation=False,
        )

        return agent

    def create_task(
        self,
        description: str,
        agent: Agent,
        expected_output: str | None = None,
    ) -> Task:
        """Create a CrewAI task with the specified configuration.

        Args:
            description: Detailed description of the task.
            agent: The agent assigned to this task.
            expected_output: Optional description of expected output format.

        Returns:
            A configured CrewAI Task instance.

        Example:
            >>> manager = CrewManager()
            >>> task = manager.create_task(
            ...     description="Analyze Q1 sales data",
            ...     agent=data_analyst_agent,
            ...     expected_output="Summary report with charts"
            ... )
        """
        logger.info(f"Creating task: {description[:50]}...")

        task = Task(
            description=description,
            agent=agent,
            expected_output=expected_output or "",
        )

        return task

    def run_crew(
        self,
        tasks: list[Task],
        agents: Sequence[Agent],
        verbose: bool = True,
    ) -> Any:
        """Create and run a crew with the specified tasks and agents.

        Args:
            tasks: List of tasks to execute.
            agents: List of agents to use.
            verbose: Whether to enable verbose output.

        Returns:
            The CrewOutput containing the results of the crew execution.

        Example:
            >>> manager = CrewManager()
            >>> result = manager.run_crew(
            ...     tasks=[task1, task2],
            ...     agents=[agent1, agent2]
            ... )
        """
        logger.info(f"Running crew with {len(tasks)} tasks and {len(agents)} agents")

        crew = Crew(
            agents=agents,
            tasks=tasks,
            verbose=verbose,
        )

        self._crew = crew

        result = crew.kickoff()

        logger.info("Crew execution completed")
        return result

    def get_erp_assistant(self) -> Crew:
        """Get a pre-configured ERP assistant crew with DatabaseQueryTool.

        This creates a ready-to-use crew with a database query tool
        that can answer questions about ERP data.

        Returns:
            A pre-configured Crew instance for ERP assistance.

        Example:
            >>> manager = CrewManager()
            >>> crew = manager.get_erp_assistant()
            >>> result = crew.kickoff()
        """
        logger.info("Creating ERP Assistant crew")

        # Import the database query tool
        from core.ai.database_query_tool import DatabaseQueryTool

        # Create the database query tool
        db_tool = DatabaseQueryTool()

        # Create the ERP assistant agent
        erp_assistant = self.create_agent(
            role="ERP Data Analyst",
            goal=(
                "Analyze and provide insights from ERP database data. "
                "Help users understand their business data and generate reports."
            ),
            backstory=(
                "You are an expert ERP system analyst with deep knowledge of "
                "business data structures. You can query databases and provide "
                "clear, actionable insights from the data."
            ),
            tools=[db_tool],
        )

        # Create a default task for the assistant
        task = self.create_task(
            description=(
                "Answer user questions about ERP data by querying the database "
                "and presenting the results in a clear format."
            ),
            agent=erp_assistant,
            expected_output=(
                "Clear, formatted responses with data from the ERP system"
            ),
        )

        # Create and return the crew
        crew = Crew(
            agents=[erp_assistant],
            tasks=[task],
            verbose=True,
        )

        return crew
