"""CrewFactory Implementation

Factory class for creating CrewAI agents and tasks from YAML configuration.
"""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Try to import CrewAI components
try:
    from crew import Agent, Task, Crew
    from crew import LLM

    CREWAI_AVAILABLE = True
except ImportError:
    CREWAI_AVAILABLE = False
    Agent = None
    Task = None
    Crew = None
    LLM = None


class CrewFactory:
    """Factory for creating CrewAI agents and tasks from YAML config.

    This factory loads agent and task configurations from YAML files
    and provides methods to dynamically create CrewAI objects.
    """

    def __init__(
        self,
        agents_config: Optional[Any] = None,
        tasks_config: Optional[Any] = None,
        default_llm_config: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize the CrewFactory.

        Args:
            agents_config: AgentsConfig instance with agent definitions.
            tasks_config: TasksConfig instance with task definitions.
            default_llm_config: Default LLM configuration to use.
        """
        self.agents_config = agents_config
        self.tasks_config = tasks_config
        self.default_llm_config = default_llm_config or {
            "model": "gpt-4",
            "temperature": 0.7,
        }

        # Cache for created agents and tasks
        self._agents: Dict[str, Any] = {}
        self._tasks: Dict[str, Any] = {}

        logger.info("CrewFactory initialized")

    def load_agents_from_config(self) -> Dict[str, Any]:
        """Load all agents from configuration.

        Returns:
            Dictionary of agent names to Agent instances.
        """
        if not CREWAI_AVAILABLE or not self.agents_config:
            logger.warning("CrewAI not available or no agents config")
            return {}

        agents = {}
        for agent_config in self.agents_config.get_all_agents().values():
            agent = self.create_agent(agent_config)
            if agent:
                agents[agent_config.name] = agent

        logger.info(f"Loaded {len(agents)} agents from config")
        return agents

    def load_tasks_from_config(self) -> Dict[str, Any]:
        """Load all tasks from configuration.

        Returns:
            Dictionary of task names to Task instances.
        """
        if not CREWAI_AVAILABLE or not self.tasks_config:
            logger.warning("CrewAI not available or no tasks config")
            return {}

        tasks = {}
        for task_config in self.tasks_config.get_all_tasks().values():
            task = self.create_task(task_config)
            if task:
                tasks[task_config.name] = task

        logger.info(f"Loaded {len(tasks)} tasks from config")
        return tasks

    def create_agent(self, agent_config: Any) -> Optional[Any]:
        """Create a CrewAI Agent from configuration.

        Args:
            agent_config: AgentConfig instance with agent definition.

        Returns:
            Agent instance or None if CrewAI not available.
        """
        if not CREWAI_AVAILABLE or not Agent:
            logger.warning("Cannot create agent: CrewAI not available")
            return None

        # Get LLM configuration
        llm_config = agent_config.llm_config or self.default_llm_config

        # Create LLM instance
        llm = LLM(
            model=llm_config.get("model", "gpt-4"),
            temperature=llm_config.get("temperature", 0.7),
            max_tokens=llm_config.get("max_tokens", 4000),
        )

        # Create agent
        agent = Agent(
            role=agent_config.role,
            goal=agent_config.goal,
            backstory=agent_config.backstory,
            llm=llm,
            verbose=True,
            allow_delegation=False,
        )

        # Cache the agent
        self._agents[agent_config.name] = agent

        logger.debug(f"Created agent: {agent_config.name}")
        return agent

    def create_task(self, task_config: Any, context: Optional[List[Any]] = None) -> Optional[Any]:
        """Create a CrewAI Task from configuration.

        Args:
            task_config: TaskConfig instance with task definition.
            context: Optional list of context tasks.

        Returns:
            Task instance or None if CrewAI not available.
        """
        if not CREWAI_AVAILABLE or not Task:
            logger.warning("Cannot create task: CrewAI not available")
            return None

        # Get the agent for this task
        agent = None
        if self.agents_config:
            agent_config = self.agents_config.get_agent(task_config.agent)
            if agent_config:
                agent = self._agents.get(agent_config.name)
                if not agent:
                    agent = self.create_agent(agent_config)

        # Create task
        task = Task(
            description=task_config.description,
            expected_output=task_config.expected_output,
            agent=agent,
            async_execution=task_config.async_execution,
            context=context,
        )

        # Cache the task
        self._tasks[task_config.name] = task

        logger.debug(f"Created task: {task_config.name}")
        return task

    def get_agent(self, name: str) -> Optional[Any]:
        """Get a created agent by name.

        Args:
            name: Name of the agent.

        Returns:
            Agent instance if found, None otherwise.
        """
        return self._agents.get(name)

    def get_task(self, name: str) -> Optional[Any]:
        """Get a created task by name.

        Args:
            name: Name of the task.

        Returns:
            Task instance if found, None otherwise.
        """
        return self._tasks.get(name)

    def create_crew(
        self,
        agent_names: List[str],
        task_names: List[str],
        memory: bool = True,
        knowledge: bool = False,
        **kwargs,
    ) -> Any:
        """Create a Crew from agents and tasks.

        Args:
            agent_names: List of agent names to include.
            task_names: List of task names to include.
            memory: Whether to enable memory for the crew.
            knowledge: Whether to enable knowledge for the crew.
            **kwargs: Additional arguments for Crew.

        Returns:
            Crew instance.
        """
        if not CREWAI_AVAILABLE or not Crew:
            logger.warning("Cannot create crew: CrewAI not available")
            return None

        # Get agents
        agents = []
        for name in agent_names:
            agent = self._agents.get(name)
            if agent:
                agents.append(agent)

        # Get tasks
        tasks = []
        for name in task_names:
            task = self._tasks.get(name)
            if task:
                tasks.append(task)

        # Create crew
        crew = Crew(
            agents=agents,
            tasks=tasks,
            memory=memory,
            knowledge=knowledge,
            verbose=True,
            **kwargs,
        )

        logger.info(f"Created crew with {len(agents)} agents and {len(tasks)} tasks")
        return crew

    def create_flow_crew(
        self,
        agent_names: List[str],
        task_names: List[str],
        flow_name: str = "Default Flow",
    ) -> Any:
        """Create a crew optimized for flow execution.

        Args:
            agent_names: List of agent names to include.
            task_names: List of task names to include.
            flow_name: Name of the flow.

        Returns:
            Crew instance configured for flows.
        """
        return self.create_crew(
            agent_names=agent_names,
            task_names=task_names,
            memory=True,
            knowledge=False,
            flow_name=flow_name,
        )

    def get_available_agents(self) -> List[str]:
        """Get list of available agent names.

        Returns:
            List of agent names.
        """
        return list(self._agents.keys())

    def get_available_tasks(self) -> List[str]:
        """Get list of available task names.

        Returns:
            List of task names.
        """
        return list(self._tasks.keys())

    def reload_config(self) -> None:
        """Reload configuration from YAML files."""
        self._agents = self.load_agents_from_config()
        self._tasks = self.load_tasks_from_config()
        logger.info("Configuration reloaded")


def create_factory(
    agents_config_path: Optional[str] = None,
    tasks_config_path: Optional[str] = None,
    default_llm_config: Optional[Dict[str, Any]] = None,
) -> CrewFactory:
    """Create a CrewFactory instance with configurations.

    Args:
        agents_config_path: Path to agents.yaml file.
        tasks_config_path: Path to tasks.yaml file.
        default_llm_config: Default LLM configuration.

    Returns:
        CrewFactory instance.
    """
    from ..config.agents import load_agents
    from ..config.tasks import load_tasks

    agents_config = load_agents(agents_config_path)
    tasks_config = load_tasks(tasks_config_path)

    return CrewFactory(
        agents_config=agents_config,
        tasks_config=tasks_config,
        default_llm_config=default_llm_config,
    )
