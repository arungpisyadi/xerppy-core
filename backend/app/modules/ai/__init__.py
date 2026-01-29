"""AI Module Init

This module provides CrewAI integration with YAML-first approach and CrewAI Flows.
"""

from .factory import CrewFactory
from .flows.base_flow import BaseFlow
from .knowledge import KnowledgeService

__all__ = [
    "CrewFactory",
    "BaseFlow",
    "KnowledgeService",
]
