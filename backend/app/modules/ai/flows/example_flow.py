"""Example Flow Implementation

Demonstrates how to use BaseFlow with YAML configuration.
"""

import logging
from typing import Any, Dict

from .base_flow import BaseFlow

logger = logging.getLogger(__name__)


class ExampleFlow(BaseFlow):
    """Example flow demonstrating YAML configuration usage.

    This flow shows how to:
    - Load agents and tasks from YAML
    - Create a crew from configured agents/tasks
    - Use memory and knowledge features
    - Handle flow execution and state
    """

    def __init__(
        self,
        flow_id: str = "example_flow",
        enable_memory: bool = True,
        enable_knowledge: bool = True,
        **kwargs,
    ) -> None:
        """Initialize the ExampleFlow.

        Args:
            flow_id: Unique identifier for this flow instance.
            enable_memory: Whether to enable memory features.
            enable_knowledge: Whether to enable knowledge features.
            **kwargs: Additional arguments.
        """
        super().__init__(
            flow_id=flow_id,
            enable_memory=enable_memory,
            enable_knowledge=enable_knowledge,
            **kwargs,
        )

        logger.info("ExampleFlow initialized")

    def setup(self) -> None:
        """Set up the flow with agents and tasks from YAML config.

        This method demonstrates how to create specific agents and tasks
        for your flow using the factory methods.
        """
        logger.info(f"Setting up ExampleFlow: {self._flow_id}")

        # Load all agents from YAML config
        self.crew_factory.load_agents_from_config()

        # Load all tasks from YAML config
        self.crew_factory.load_tasks_from_config()

        # Create a crew with specific agents and tasks
        self._crew = self.create_crew(
            agents=["Researcher", "Writer"],
            tasks=["research_topic", "write_article"],
            memory=self._enable_memory,
            knowledge=self._enable_knowledge,
        )

        logger.info(f"ExampleFlow setup complete with crew: {self._crew}")
        self._is_setup = True

    def _execute_flow(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the example flow logic.

        Args:
            inputs: Input parameters for the flow.

        Returns:
            Dictionary of results.
        """
        results = {
            "flow_id": self._flow_id,
            "inputs": inputs,
            "message": "Example flow executed successfully",
            "agents_used": [],
            "tasks_executed": [],
        }

        # Get available agents
        agents = self.crew_factory.get_available_agents()
        results["agents_used"] = agents

        # Get available tasks
        tasks = self.crew_factory.get_available_tasks()
        results["tasks_executed"] = tasks

        # Add memory if enabled
        if self._enable_memory:
            self.add_memory("example_key", "example_value")
            results["memory_enabled"] = True

        # Add knowledge if enabled
        if self._enable_knowledge:
            from ..knowledge import KnowledgeService
            knowledge = KnowledgeService()
            knowledge.add_text("Example knowledge content")
            results["knowledge_enabled"] = True
            results["knowledge_sources"] = knowledge.list_sources_by_id()

        logger.info(f"ExampleFlow execution complete: {results}")
        return results

    def run_with_topic(self, topic: str) -> Dict[str, Any]:
        """Run the flow with a specific topic.

        Args:
            topic: Topic to research and write about.

        Returns:
            Flow execution results.
        """
        inputs = {"topic": topic}
        return self.run(inputs)


class ResearchAndWriteFlow(BaseFlow):
    """A specialized flow for research and content creation.

    This flow demonstrates a more specific use case:
    - Research a topic
    - Write an article based on research
    - Analyze the results
    """

    def __init__(
        self,
        flow_id: str = "research_write_flow",
        **kwargs,
    ) -> None:
        """Initialize the ResearchAndWriteFlow.

        Args:
            flow_id: Unique identifier for this flow instance.
            **kwargs: Additional arguments.
        """
        super().__init__(flow_id=flow_id, **kwargs)
        self._research_results = None

    def setup(self) -> None:
        """Set up the flow with agents and tasks."""
        logger.info(f"Setting up ResearchAndWriteFlow: {self._flow_id}")

        # Load agents
        self.crew_factory.load_agents_from_config()

        # Load tasks
        self.crew_factory.load_tasks_from_config()

        # Create crew with all agents for comprehensive workflow
        self._crew = self.create_crew(
            agents=["Researcher", "Writer", "Analyzer"],
            tasks=["research_topic", "write_article", "analyze_data"],
            memory=True,
            knowledge=False,
        )

        self._is_setup = True
        logger.info("ResearchAndWriteFlow setup complete")

    def _execute_flow(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the research and write workflow.

        Args:
            inputs: Input parameters including topic.

        Returns:
            Dictionary of results.
        """
        topic = inputs.get("topic", "No topic provided")

        results = {
            "flow_id": self._flow_id,
            "topic": topic,
            "status": "completed",
            "steps_completed": [],
            "output_files": [],
        }

        # Step 1: Research
        results["steps_completed"].append("research")

        # Step 2: Write article
        results["steps_completed"].append("write_article")

        # Step 3: Analyze
        results["steps_completed"].append("analyze_data")

        results["message"] = f"Completed research and write flow for topic: {topic}"

        logger.info(f"ResearchAndWriteFlow results: {results}")
        return results

    def run_research_only(self, topic: str) -> Dict[str, Any]:
        """Run only the research portion of the flow.

        Args:
            topic: Topic to research.

        Returns:
            Research results.
        """
        inputs = {"topic": topic, "mode": "research_only"}
        return self.run(inputs)
