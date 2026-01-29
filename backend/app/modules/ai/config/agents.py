"""Agents Configuration Loader

Loads agent definitions from agents.yaml configuration file.
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


class AgentConfig:
    """Configuration for a single agent."""

    def __init__(self, config: Dict[str, Any]) -> None:
        self.name: str = config.get("name", "")
        self.role: str = config.get("role", "")
        self.goal: str = config.get("goal", "")
        self.backstory: str = config.get("backstory", "")
        self.llm_config: Dict[str, Any] = config.get("llm_config", {})
        self.tools: List[Dict[str, Any]] = config.get("tools", [])
        self.constraints: List[str] = config.get("constraints", [])

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return {
            "name": self.name,
            "role": self.role,
            "goal": self.goal,
            "backstory": self.backstory,
            "llm_config": self.llm_config,
            "tools": self.tools,
            "constraints": self.constraints,
        }


class AgentsConfig:
    """Manages agent configurations loaded from YAML."""

    def __init__(self, config_path: Optional[str] = None) -> None:
        """Initialize the agents configuration.

        Args:
            config_path: Path to the agents.yaml file. If not provided,
                        uses default location.
        """
        if config_path is None:
            config_path = os.environ.get(
                "AGENTS_CONFIG_PATH",
                str(Path(__file__).parent / "agents.yaml"),
            )
        self.config_path = Path(config_path)
        self._agents: Dict[str, AgentConfig] = {}
        self._load_config()

    def _load_config(self) -> None:
        """Load agents from the YAML configuration file."""
        if not self.config_path.exists():
            raise FileNotFoundError(f"Agents config not found: {self.config_path}")

        with open(self.config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)

        agents_data = config.get("agents", [])
        for agent_data in agents_data:
            agent = AgentConfig(agent_data)
            self._agents[agent.name] = agent

    def get_agent(self, name: str) -> Optional[AgentConfig]:
        """Get a specific agent by name.

        Args:
            name: The name of the agent to retrieve.

        Returns:
            AgentConfig if found, None otherwise.
        """
        return self._agents.get(name)

    def get_all_agents(self) -> Dict[str, AgentConfig]:
        """Get all loaded agents.

        Returns:
            Dictionary of agent names to AgentConfig objects.
        """
        return self._agents.copy()

    def get_agent_names(self) -> List[str]:
        """Get list of all agent names.

        Returns:
            List of agent names.
        """
        return list(self._agents.keys())


# Global instance for easy access
_agents_config: Optional[AgentsConfig] = None


def load_agents(config_path: Optional[str] = None) -> AgentsConfig:
    """Load agents configuration.

    Args:
        config_path: Optional path to agents.yaml file.

    Returns:
        AgentsConfig instance with loaded agents.
    """
    global _agents_config
    if _agents_config is None:
        _agents_config = AgentsConfig(config_path)
    return _agents_config


def get_agents_config() -> AgentsConfig:
    """Get the global agents configuration instance.

    Returns:
        The global AgentsConfig instance.
    """
    global _agents_config
    if _agents_config is None:
        _agents_config = AgentsConfig()
    return _agents_config
