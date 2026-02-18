"""CrewAI Manager for Xerppy ERP framework.

This module provides the CrewManager class for initializing and managing
CrewAI agents within the ERP system using YAML configuration files.

Configuration Files:
    - agents.yaml: Define agent configurations (role, goal, backstory, tools)
    - tasks.yaml: Define task configurations (description, expected_output, agent)
    - crews.yaml: Define crew compositions (agents, tasks, process settings)

Example:
    >>> manager = CrewManager()
    >>> crew = await manager.load_crew_async("erp_assistant")
    >>> result = await crew.kickoff_async()
"""

# pyright: reportCallIssue=false, reportArgumentType=false

from __future__ import annotations

import asyncio
import logging
import os
from pathlib import Path
from typing import Any

import yaml
from crewai import Agent, Crew, Task

logger = logging.getLogger(__name__)

# Default config directory
DEFAULT_CONFIG_DIR = Path(__file__).parent / "config"

# Tool mapping - maps YAML tool names to actual tool instances
TOOL_MAPPING: dict[str, Any] = {}


def _init_tool_mapping() -> None:
    """Initialize the tool mapping with available tools."""
    global TOOL_MAPPING
    if not TOOL_MAPPING:
        try:
            from core.ai.database_query_tool import DatabaseQueryTool

            TOOL_MAPPING["DatabaseQueryTool"] = DatabaseQueryTool()
            logger.info("Tool mapping initialized with DatabaseQueryTool")
        except Exception as e:
            logger.warning(f"Failed to initialize tools: {e}")


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

    def __init__(
        self,
        config_dir: Path | str | None = None,
    ) -> None:
        """Initialize the CrewManager with API key from configuration.

        Args:
            config_dir: Optional custom path to the config directory containing
                       agents.yaml, tasks.yaml, and crews.yaml files.
                       Defaults to core/ai/config/.

        The API key is loaded from Flask config (CREWAI_API_KEY) with
        environment variable (CREWAI_API_KEY) as fallback.
        """
        # Initialize tool mapping
        _init_tool_mapping()

        self.config_dir = Path(config_dir) if config_dir else DEFAULT_CONFIG_DIR
        self._agents_config: dict[str, Any] = {}
        self._tasks_config: dict[str, Any] = {}
        self._crews_config: dict[str, Any] = {}
        self.api_key: str | None = self._load_api_key()
        self._crew: Crew | None = None

        # Load YAML configurations
        self._load_yaml_configs()

        if self.api_key:
            logger.info("CrewManager initialized with API key")
        else:
            logger.warning(
                "CrewManager initialized without API key. "
                "Set CREWAI_API_KEY in config or environment."
            )

    def _load_yaml_configs(self) -> None:
        """Load all YAML configuration files from the config directory."""
        # Load agents.yaml
        agents_file = self.config_dir / "agents.yaml"
        if agents_file.exists():
            with open(agents_file) as f:
                self._agents_config = yaml.safe_load(f) or {}
            logger.info(f"Loaded {len(self._agents_config)} agent configurations")
        else:
            logger.warning(f"agents.yaml not found in {self.config_dir}")

        # Load tasks.yaml
        tasks_file = self.config_dir / "tasks.yaml"
        if tasks_file.exists():
            with open(tasks_file) as f:
                self._tasks_config = yaml.safe_load(f) or {}
            logger.info(f"Loaded {len(self._tasks_config)} task configurations")
        else:
            logger.warning(f"tasks.yaml not found in {self.config_dir}")

        # Load crews.yaml
        crews_file = self.config_dir / "crews.yaml"
        if crews_file.exists():
            with open(crews_file) as f:
                self._crews_config = yaml.safe_load(f) or {}
            logger.info(f"Loaded {len(self._crews_config)} crew configurations")
        else:
            logger.warning(f"crews.yaml not found in {self.config_dir}")

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

    async def run_crew(
        self,
        tasks: list[Task],
        agents: list[Agent],
        verbose: bool = True,
    ) -> Any:
        """Create and run a crew with the specified tasks and agents asynchronously.

        Args:
            tasks: List of tasks to execute.
            agents: List of agents to use.
            verbose: Whether to enable verbose output.

        Returns:
            The CrewOutput containing the results of the crew execution.

        Example:
            >>> manager = CrewManager()
            >>> result = await manager.run_crew(
            ...     tasks=[task1, task2],
            ...     agents=[agent1, agent2]
            ... )
        """
        logger.info(f"Running crew with {len(tasks)} tasks and {len(agents)} agents")

        crew = Crew(
            agents=agents,  # type: ignore[arg-type]
            tasks=tasks,
            verbose=verbose,
        )

        self._crew = crew

        # Use async kickoff for non-blocking execution
        result = await asyncio.to_thread(crew.kickoff)

        logger.info("Crew execution completed")
        return result

    async def run_crew_async(
        self,
        tasks: list[Task],
        agents: list[Agent],
        verbose: bool = True,
    ) -> Any:
        """Create and run a crew with the specified tasks and agents asynchronously.

        This is an alias for run_crew() that uses async execution.

        Args:
            tasks: List of tasks to execute.
            agents: List of agents to use.
            verbose: Whether to enable verbose output.

        Returns:
            The CrewOutput containing the results of the crew execution.

        Example:
            >>> manager = CrewManager()
            >>> result = await manager.run_crew_async(
            ...     tasks=[task1, task2],
            ...     agents=[agent1, agent2]
            ... )
        """
        return await self.run_crew(tasks, agents, verbose)

    def get_erp_assistant(self) -> Crew:
        """Get a pre-configured ERP assistant crew with DatabaseQueryTool.

        This creates a ready-to-use crew with a database query tool
        that can answer questions about ERP data.

        Returns:
            A pre-configured Crew instance for ERP assistance.

        Example:
            >>> manager = CrewManager()
            >>> crew = manager.get_erp_assistant()
            >>> result = await crew.kickoff_async()
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

    async def get_erp_assistant_async(self) -> Crew:
        """Get a pre-configured ERP assistant crew asynchronously.

        This creates a ready-to-use crew with a database query tool
        that can answer questions about ERP data.

        Returns:
            A pre-configured Crew instance for ERP assistance.

        Example:
            >>> manager = CrewManager()
            >>> crew = await manager.get_erp_assistant_async()
            >>> result = await asyncio.to_thread(crew.kickoff)
        """
        # Run the synchronous creation in a thread pool to avoid blocking
        return await asyncio.to_thread(self.get_erp_assistant)

    # ==========================================================================
    # YAML Configuration Methods
    # ==========================================================================

    def get_available_agents(self) -> list[str]:
        """Get list of available agent names from YAML configuration.

        Returns:
            List of agent configuration keys from agents.yaml.
        """
        return list(self._agents_config.keys())

    def get_available_tasks(self) -> list[str]:
        """Get list of available task names from YAML configuration.

        Returns:
            List of task configuration keys from tasks.yaml.
        """
        return list(self._tasks_config.keys())

    def get_available_crews(self) -> list[str]:
        """Get list of available crew names from YAML configuration.

        Returns:
            List of crew configuration keys from crews.yaml.
        """
        return list(self._crews_config.keys())

    def load_agent_from_yaml(self, agent_name: str) -> Agent:
        """Load and create an agent from YAML configuration.

        Args:
            agent_name: The key name of the agent in agents.yaml.

        Returns:
            A configured CrewAI Agent instance.

        Raises:
            ValueError: If agent_name is not found in agents.yaml.
        """
        if agent_name not in self._agents_config:
            available = ", ".join(self.get_available_agents())
            raise ValueError(
                f"Agent '{agent_name}' not found in configuration. "
                f"Available agents: {available}"
            )

        config = self._agents_config[agent_name]

        # Get tools from config
        tools = []
        tool_names = config.get("tools", [])
        for tool_name in tool_names:
            if tool_name in TOOL_MAPPING:
                tools.append(TOOL_MAPPING[tool_name])
            else:
                logger.warning(f"Tool '{tool_name}' not found in tool mapping")

        agent = Agent(
            role=config.get("role", ""),
            goal=config.get("goal", ""),
            backstory=config.get("backstory", ""),
            tools=tools,
            verbose=config.get("verbose", True),
            allow_delegation=config.get("allow_delegation", False),
        )

        logger.info(f"Loaded agent '{agent_name}' from YAML configuration")
        return agent

    def load_task_from_yaml(self, task_name: str, agent: Agent) -> Task:
        """Load and create a task from YAML configuration.

        Args:
            task_name: The key name of the task in tasks.yaml.
            agent: The agent to assign this task to.

        Returns:
            A configured CrewAI Task instance.

        Raises:
            ValueError: If task_name is not found in tasks.yaml.
        """
        if task_name not in self._tasks_config:
            available = ", ".join(self.get_available_tasks())
            raise ValueError(
                f"Task '{task_name}' not found in configuration. "
                f"Available tasks: {available}"
            )

        config = self._tasks_config[task_name]

        task = Task(
            description=config.get("description", ""),
            agent=agent,
            expected_output=config.get("expected_output", ""),
        )

        logger.info(f"Loaded task '{task_name}' from YAML configuration")
        return task

    def load_crew(self, crew_name: str) -> Crew:
        """Load and create a complete crew from YAML configuration.

        Args:
            crew_name: The key name of the crew in crews.yaml.

        Returns:
            A configured CrewAI Crew instance ready to execute.

        Raises:
            ValueError: If crew_name is not found in crews.yaml or referenced
                       agents/tasks are missing.
        """
        if crew_name not in self._crews_config:
            available = ", ".join(self.get_available_crews())
            raise ValueError(
                f"Crew '{crew_name}' not found in configuration. "
                f"Available crews: {available}"
            )

        config = self._crews_config[crew_name]

        # Load all agents
        agent_names = config.get("agents", [])
        agents = []
        for agent_name in agent_names:
            agent = self.load_agent_from_yaml(agent_name)
            agents.append(agent)

        # Load all tasks (in order)
        task_names = config.get("tasks", [])
        tasks = []
        for task_name in task_names:
            # Find the agent for this task from task config
            task_config = self._tasks_config.get(task_name, {})
            assigned_agent_name = task_config.get("agent")

            # Find the matching agent
            task_agent = None
            if assigned_agent_name:
                # Try to find agent by name in the loaded agents
                for i, agent in enumerate(agents):
                    if agent_names[i] == assigned_agent_name:
                        task_agent = agent
                        break

            if not task_agent and agents:
                task_agent = agents[0]  # Default to first agent

            if task_agent:
                task = self.load_task_from_yaml(task_name, task_agent)
                tasks.append(task)

        # Get process type
        process = config.get("process", "sequential")

        # Create crew
        crew = Crew(
            agents=agents,  # type: ignore[arg-type]
            tasks=tasks,
            verbose=config.get("verbose", True),
            process=process,
        )

        logger.info(f"Loaded crew '{crew_name}' from YAML configuration")
        self._crew = crew
        return crew

    async def load_crew_async(self, crew_name: str) -> Crew:
        """Load and create a complete crew from YAML configuration asynchronously.

        Args:
            crew_name: The key name of the crew in crews.yaml.

        Returns:
            A configured CrewAI Crew instance ready to execute.

        Raises:
            ValueError: If crew_name is not found in crews.yaml or referenced
                       agents/tasks are missing.

        Example:
            >>> manager = CrewManager()
            >>> crew = await manager.load_crew_async("erp_assistant")
            >>> result = await asyncio.to_thread(crew.kickoff)
        """
        # Run the synchronous load in a thread pool to avoid blocking
        return await asyncio.to_thread(self.load_crew, crew_name)

    async def run_crew_from_yaml(self, crew_name: str) -> Any:
        """Load and execute a crew from YAML configuration asynchronously.

        Args:
            crew_name: The key name of the crew in crews.yaml.

        Returns:
            The CrewOutput containing the results of the crew execution.

        Example:
            >>> manager = CrewManager()
            >>> result = await manager.run_crew_from_yaml("erp_assistant")
        """
        crew = self.load_crew(crew_name)
        # Use asyncio.to_thread for non-blocking execution
        result = await asyncio.to_thread(crew.kickoff)
        logger.info(f"Crew '{crew_name}' execution completed")
        return result

    # ==========================================================================
    # Backward Compatibility Methods (Sync)
    # ==========================================================================

    def run_crew_sync(
        self,
        tasks: list[Task],
        agents: list[Agent],
        verbose: bool = True,
    ) -> Any:
        """Synchronous wrapper for run_crew (for backward compatibility).

        Args:
            tasks: List of tasks to execute.
            agents: List of agents to use.
            verbose: Whether to enable verbose output.

        Returns:
            The CrewOutput containing the results of the crew execution.
        """
        return asyncio.run(self.run_crew(tasks, agents, verbose))

    def run_crew_from_yaml_sync(self, crew_name: str) -> Any:
        """Synchronous wrapper for run_crew_from_yaml (for backward compatibility).

        Args:
            crew_name: The key name of the crew in crews.yaml.

        Returns:
            The CrewOutput containing the results of the crew execution.
        """
        return asyncio.run(self.run_crew_from_yaml(crew_name))
