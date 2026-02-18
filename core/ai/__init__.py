"""AI integration package for Xerppy ERP framework.

This package provides AI-powered capabilities using CrewAI v1.9+ for the ERP system,
including agent management, LLM factory, and database query tools.
"""

from core.ai.crew import XerppyCrew
from core.ai.crew_manager import CrewManager
from core.ai.database_query_tool import DatabaseQueryTool
from core.ai.llm_factory import LLMFactory

__all__ = ["XerppyCrew", "CrewManager", "DatabaseQueryTool", "LLMFactory"]
