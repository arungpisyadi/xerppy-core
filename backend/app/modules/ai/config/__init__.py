"""AI Config Init

Configuration module for AI agents and tasks.
"""

from .agents import load_agents
from .tasks import load_tasks

__all__ = [
    "load_agents",
    "load_tasks",
]
