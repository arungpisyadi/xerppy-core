"""Tasks Configuration Loader

Loads task definitions from tasks.yaml configuration file.
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


class TaskConfig:
    """Configuration for a single task."""

    def __init__(self, config: Dict[str, Any]) -> None:
        self.name: str = config.get("name", "")
        self.description: str = config.get("description", "")
        self.expected_output: str = config.get("expected_output", "")
        self.agent: str = config.get("agent", "")
        self.context: Dict[str, Any] = config.get("context", {})
        self.async_execution: bool = config.get("async_execution", False)
        self.output_file: Optional[str] = config.get("output_file")
        self.constraints: List[str] = config.get("constraints", [])
        self.dependencies: List[str] = config.get("dependencies", [])

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "expected_output": self.expected_output,
            "agent": self.agent,
            "context": self.context,
            "async_execution": self.async_execution,
            "output_file": self.output_file,
            "constraints": self.constraints,
            "dependencies": self.dependencies,
        }


class TasksConfig:
    """Manages task configurations loaded from YAML."""

    def __init__(self, config_path: Optional[str] = None) -> None:
        """Initialize the tasks configuration.

        Args:
            config_path: Path to the tasks.yaml file. If not provided,
                        uses default location.
        """
        if config_path is None:
            config_path = os.environ.get(
                "TASKS_CONFIG_PATH",
                str(Path(__file__).parent / "tasks.yaml"),
            )
        self.config_path = Path(config_path)
        self._tasks: Dict[str, TaskConfig] = {}
        self._load_config()

    def _load_config(self) -> None:
        """Load tasks from the YAML configuration file."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Tasks config not found: {self.config_path}")

        with open(self.config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)

        tasks_data = config.get("tasks", [])
        for task_data in tasks_data:
            task = TaskConfig(task_data)
            self._tasks[task.name] = task

    def get_task(self, name: str) -> Optional[TaskConfig]:
        """Get a specific task by name.

        Args:
            name: The name of the task to retrieve.

        Returns:
            TaskConfig if found, None otherwise.
        """
        return self._tasks.get(name)

    def get_all_tasks(self) -> Dict[str, TaskConfig]:
        """Get all loaded tasks.

        Returns:
            Dictionary of task names to TaskConfig objects.
        """
        return self._tasks.copy()

    def get_task_names(self) -> List[str]:
        """Get list of all task names.

        Returns:
            List of task names.
        """
        return list(self._tasks.keys())

    def get_tasks_for_agent(self, agent_name: str) -> List[TaskConfig]:
        """Get all tasks assigned to a specific agent.

        Args:
            agent_name: The name of the agent.

        Returns:
            List of TaskConfig objects assigned to the agent.
        """
        return [
            task for task in self._tasks.values() if task.agent == agent_name
        ]


# Global instance for easy access
_tasks_config: Optional[TasksConfig] = None


def load_tasks(config_path: Optional[str] = None) -> TasksConfig:
    """Load tasks configuration.

    Args:
        config_path: Optional path to tasks.yaml file.

    Returns:
        TasksConfig instance with loaded tasks.
    """
    global _tasks_config
    if _tasks_config is None:
        _tasks_config = TasksConfig(config_path)
    return _tasks_config


def get_tasks_config() -> TasksConfig:
    """Get the global tasks configuration instance.

    Returns:
        The global TasksConfig instance.
    """
    global _tasks_config
    if _tasks_config is None:
        _tasks_config = TasksConfig()
    return _tasks_config
