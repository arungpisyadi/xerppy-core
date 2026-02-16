"""AI integration package for Xerppy ERP framework.

This package provides AI-powered capabilities using CrewAI for the ERP system,
including agent management and database query tools.
"""

from core.ai.crew_manager import CrewManager
from core.ai.database_query_tool import DatabaseQueryTool

__all__ = ["CrewManager", "DatabaseQueryTool"]
