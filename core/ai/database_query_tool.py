"""Database Query Tool for CrewAI agents.

This module provides a safe, read-only database query tool that allows
AI agents to query ERP data while maintaining security and audit trails.
"""

from __future__ import annotations

import logging
import re
from typing import Any

from crewai.tools import BaseTool
from pydantic import Field

logger = logging.getLogger(__name__)

# SQL keywords that are not allowed (write operations)
FORBIDDEN_KEYWORDS: frozenset[str] = frozenset(
    {
        "INSERT",
        "UPDATE",
        "DELETE",
        "DROP",
        "CREATE",
        "ALTER",
        "TRUNCATE",
        "GRANT",
        "REVOKE",
        "EXEC",
        "EXECUTE",
        "CALL",
    }
)


class DatabaseQueryTool(BaseTool):
    """A custom CrewAI tool for safely querying the ERP database.

    This tool allows AI agents to execute read-only SQL SELECT queries
    against the ERP database while providing audit logging and error handling.

    Attributes:
        name: Tool name identifier.
        description: Human-readable description of the tool's purpose.

    Example:
        >>> tool = DatabaseQueryTool()
        >>> result = tool._run("SELECT * FROM users WHERE active = true")
    """

    name: str = Field(default="database_query_tool", description="The tool name")
    description: str = Field(
        default=(
            "A tool that can query the ERP database to read data. "
            "Use this when you need to fetch information from the database."
        ),
        description="Tool description for the AI agent",
    )

    def __init__(self, **kwargs: Any) -> None:
        """Initialize the DatabaseQueryTool.

        Args:
            **kwargs: Additional keyword arguments passed to BaseTool.
        """
        super().__init__(**kwargs)
        logger.info("DatabaseQueryTool initialized")

    def _validate_query(self, query: str) -> str:
        """Validate that the query is a safe SELECT statement.

        Args:
            query: The SQL query to validate.

        Returns:
            The validated query string.

        Raises:
            ValueError: If the query is not a SELECT or contains forbidden keywords.
        """
        # Strip whitespace and convert to uppercase for validation
        cleaned_query = query.strip().upper()

        # Check if query starts with SELECT
        if not cleaned_query.startswith("SELECT"):
            raise ValueError(
                "Only SELECT queries are allowed. "
                f"Received query starting with: {cleaned_query[:20]}..."
            )

        # Check for forbidden keywords
        # Use word boundary matching to avoid false positives
        for keyword in FORBIDDEN_KEYWORDS:
            # Match keyword as a whole word (with word boundaries)
            pattern = r"\b" + keyword + r"\b"
            if re.search(pattern, cleaned_query):
                raise ValueError(
                    f"Forbidden keyword '{keyword}' detected in query. "
                    "Only SELECT queries are allowed for safety."
                )

        return query

    def _run(self, query: str) -> str:
        """Execute a read-only SQL SELECT query against the ERP database.

        This method validates the query, executes it safely, and returns
        the results in a formatted string.

        Args:
            query: The SQL SELECT query to execute.

        Returns:
            A string containing the query results or an error message.

        Raises:
            ValueError: If the query is not a valid SELECT statement.
        """
        try:
            # Validate the query first
            validated_query = self._validate_query(query)

            # Log the query for audit purposes
            logger.info(f"Executing database query: {validated_query[:200]}...")

            # Import here to avoid circular imports
            from sqlalchemy import text

            from core.extensions import db

            # Get the database session
            session = db.session

            # Execute the query using SQLAlchemy
            result = session.execute(text(validated_query))

            # Fetch all rows
            rows = result.fetchall()

            # Format the results
            if not rows:
                return "No results found for the given query."

            # Get column names from result keys
            columns = result.keys()

            # Format as a readable string
            output_lines: list[str] = []

            # Header
            output_lines.append("Query Results:")
            output_lines.append("-" * 50)

            # Column headers
            output_lines.append(" | ".join(str(col) for col in columns))
            output_lines.append("-" * 50)

            # Data rows
            for row in rows:
                output_lines.append(" | ".join(str(value) for value in row))

            output_lines.append("-" * 50)
            output_lines.append(f"Total rows: {len(rows)}")

            return "\n".join(output_lines)

        except ValueError as e:
            # Re-raise ValueError for validation errors
            logger.warning(f"Query validation failed: {e}")
            raise

        except Exception as e:
            # Handle other database errors gracefully
            error_message = f"Database query failed: {str(e)}"
            logger.error(error_message)
            return f"Error executing query: {str(e)}"
