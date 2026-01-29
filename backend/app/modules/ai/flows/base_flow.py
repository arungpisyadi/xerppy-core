"""BaseFlow Implementation

Base class for CrewAI Flows with YAML-first approach.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# Try to import CrewAI components, provide fallbacks if not available
try:
    from crew import Flow as CrewAIFlow
    from crew import FlowState

    CREWAI_AVAILABLE = True
except ImportError:
    CREWAI_AVAILABLE = False
    CrewAIFlow = None
    FlowState = None


class FlowStateModel(BaseModel):
    """Model representing the current state of a flow."""

    flow_id: str = Field(..., description="Unique identifier for the flow instance")
    name: str = Field(..., description="Name of the flow")
    status: str = Field(default="initialized", description="Current status of the flow")
    started_at: Optional[datetime] = Field(None, description="When the flow started")
    completed_at: Optional[datetime] = Field(None, description="When the flow completed")
    inputs: Dict[str, Any] = Field(default_factory=dict, description="Input parameters")
    outputs: Dict[str, Any] = Field(default_factory=dict, description="Output results")
    task_results: Dict[str, Any] = Field(default_factory=dict, description="Results from each task")
    memory: Dict[str, Any] = Field(default_factory=dict, description="Flow memory data")
    error: Optional[str] = Field(None, description="Error message if flow failed")


class BaseFlow:
    """Base class for CrewAI Flows with enhanced features.

    This class provides YAML-based agent and task configuration,
    state management, and factory-based agent/task creation.

    Note: If CrewAI is not installed, this class provides a stub implementation.
    Install crewai package to use full functionality.
    """

    def __init__(
        self,
        flow_id: Optional[str] = None,
        agents_config_path: Optional[str] = None,
        tasks_config_path: Optional[str] = None,
        enable_memory: bool = True,
        enable_knowledge: bool = True,
        **kwargs: Any,
    ) -> None:
        """Initialize the BaseFlow.

        Args:
            flow_id: Unique identifier for this flow instance.
            agents_config_path: Path to agents.yaml configuration.
            tasks_config_path: Path to tasks.yaml configuration.
            enable_memory: Whether to enable memory features.
            enable_knowledge: Whether to enable knowledge features.
            **kwargs: Additional arguments.
        """
        self._flow_id = flow_id or f"flow_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        self._enable_memory = enable_memory
        self._enable_knowledge = enable_knowledge
        self._is_setup = False

        # Import configurations here to avoid circular imports
        from ..config.agents import load_agents
        from ..config.tasks import load_tasks

        # Initialize configurations
        self.agents_config = load_agents(agents_config_path)
        self.tasks_config = load_tasks(tasks_config_path)

        # Initialize factory
        from ..factory import CrewFactory

        self.crew_factory = CrewFactory(
            agents_config=self.agents_config,
            tasks_config=self.tasks_config,
        )

        # Initialize state
        self.state = FlowStateModel(
            flow_id=self._flow_id,
            name=self.__class__.__name__,
            status="initialized",
        )

        logger.info(f"BaseFlow initialized: {self._flow_id}")

    def setup(self) -> None:
        """Set up the flow by initializing agents and tasks from YAML.

        Override this method in subclasses to define specific agents and tasks
        for your flow using the factory methods.
        """
        logger.info(f"Setting up flow: {self._flow_id}")
        self._is_setup = True
        # Subclasses should override this to create specific agents and tasks

    def run(self, inputs: Dict[str, Any]) -> FlowStateModel:
        """Execute the flow with the given inputs.

        Args:
            inputs: Dictionary of input parameters for the flow.

        Returns:
            FlowStateModel with the flow results.
        """
        logger.info(f"Running flow: {self._flow_id} with inputs: {inputs}")

        # Update state
        self.state.status = "running"
        self.state.started_at = datetime.utcnow()
        self.state.inputs = inputs

        try:
            # Call setup if not already done
            if not self._is_setup:
                self.setup()
                self._is_setup = True

            # Execute the flow logic
            result = self._execute_flow(inputs)

            # Update state with results
            self.state.status = "completed"
            self.state.completed_at = datetime.utcnow()
            self.state.outputs = result if isinstance(result, dict) else {"result": result}

            logger.info(f"Flow completed: {self._flow_id}")
            return self.state

        except Exception as e:
            logger.error(f"Flow failed: {self._flow_id} - {str(e)}")
            self.state.status = "failed"
            self.state.error = str(e)
            self.state.completed_at = datetime.utcnow()
            raise

    def _execute_flow(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the flow logic. Override in subclasses.

        Args:
            inputs: Input parameters for the flow.

        Returns:
            Dictionary of results.
        """
        return {"message": "Flow executed successfully", "inputs": inputs}

    def get_state(self) -> FlowStateModel:
        """Get the current state of the flow.

        Returns:
            FlowStateModel with current state information.
        """
        return self.state

    def get_agent(self, name: str) -> Optional[Any]:
        """Get a configured agent by name.

        Args:
            name: Name of the agent to retrieve.

        Returns:
            Agent instance if found, None otherwise.
        """
        if self.crew_factory:
            return self.crew_factory.get_agent(name)
        return None

    def get_task(self, name: str) -> Optional[Any]:
        """Get a configured task by name.

        Args:
            name: Name of the task to retrieve.

        Returns:
            Task instance if found, None otherwise.
        """
        if self.crew_factory:
            return self.crew_factory.get_task(name)
        return None

    def add_knowledge_source(self, source: Any) -> None:
        """Add a knowledge source to the flow.

        Args:
            source: Knowledge source instance.
        """
        if self._enable_knowledge:
            logger.info(f"Adding knowledge source: {type(source).__name__}")

    def add_memory(self, key: str, value: Any) -> None:
        """Add data to the flow memory.

        Args:
            key: Memory key.
            value: Value to store.
        """
        if self._enable_memory:
            self.state.memory[key] = value
            logger.info(f"Added memory: {key}")

    def get_memory(self, key: str) -> Any:
        """Get data from the flow memory.

        Args:
            key: Memory key.

        Returns:
            Stored value or None.
        """
        return self.state.memory.get(key)

    def create_crew(
        self,
        agents: List[str],
        tasks: List[str],
        memory: bool = True,
        knowledge: bool = False,
        **kwargs,
    ) -> Any:
        """Create a Crew from configured agents and tasks.

        Args:
            agents: List of agent names to include.
            tasks: List of task names to include.
            memory: Whether to enable memory for the crew.
            knowledge: Whether to enable knowledge for the crew.
            **kwargs: Additional arguments for crew creation.

        Returns:
            Crew instance.
        """
        if not self.crew_factory:
            raise ValueError("CrewFactory not initialized")

        return self.crew_factory.create_crew(
            agent_names=agents,
            task_names=tasks,
            memory=memory,
            knowledge=knowledge,
            **kwargs,
        )

    async def run_async(self, inputs: Dict[str, Any]) -> FlowStateModel:
        """Execute the flow asynchronously.

        Args:
            inputs: Dictionary of input parameters for the flow.

        Returns:
            FlowStateModel with the flow results.
        """
        logger.info(f"Running flow asynchronously: {self._flow_id}")

        import asyncio

        # Run in thread pool for compatibility
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, self.run, inputs)
        return result
