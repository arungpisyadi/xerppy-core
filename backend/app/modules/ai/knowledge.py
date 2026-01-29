"""KnowledgeService Implementation

Service for managing CrewAI Knowledge sources.
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Type, TypeVar

logger = logging.getLogger(__name__)

# Try to import CrewAI Knowledge components
try:
    from crew import KnowledgeSource, DocumentKnowledgeSource, TextKnowledgeSource

    CREWAI_KNOWLEDGE_AVAILABLE = True
except ImportError:
    CREWAI_KNOWLEDGE_AVAILABLE = False
    KnowledgeSource = None
    DocumentKnowledgeSource = None
    TextKnowledgeSource = None


T = TypeVar("T", bound="KnowledgeSource")


@dataclass
class KnowledgeSourceConfig:
    """Configuration for a knowledge source."""

    source_id: str
    source_type: str
    name: str
    description: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


class BaseKnowledgeSource(ABC):
    """Abstract base class for knowledge sources."""

    @abstractmethod
    def add_content(self, content: str, **kwargs) -> None:
        """Add content to the knowledge source."""
        pass

    @abstractmethod
    def query(self, query: str, **kwargs) -> List[str]:
        """Query the knowledge source."""
        pass

    @abstractmethod
    def get_sources(self) -> List[str]:
        """Get list of source references."""
        pass


class InMemoryKnowledgeSource(BaseKnowledgeSource):
    """Simple in-memory knowledge source for development.

    This is a fallback implementation when CrewAI Knowledge is not available.
    """

    def __init__(self, name: str = "InMemory") -> None:
        """Initialize the in-memory knowledge source.

        Args:
            name: Name of the knowledge source.
        """
        self.name = name
        self._documents: Dict[str, Dict[str, Any]] = {}
        logger.info(f"InMemoryKnowledgeSource initialized: {name}")

    def add_content(
        self,
        content: str,
        source_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> str:
        """Add content to the knowledge source.

        Args:
            content: Text content to add.
            source_id: Optional source identifier.
            metadata: Optional metadata.

        Returns:
            Source ID of the added content.
        """
        source_id = source_id or f"doc_{len(self._documents) + 1}"
        self._documents[source_id] = {
            "content": content,
            "metadata": metadata or {},
            "added_at": datetime.utcnow().isoformat(),
        }
        logger.info(f"Added content: {source_id}")
        return source_id

    def query(self, query: str, top_k: int = 5, **kwargs) -> List[str]:
        """Query the knowledge source using simple text matching.

        Args:
            query: Search query.
            top_k: Maximum number of results.

        Returns:
            List of matching content snippets.
        """
        query_lower = query.lower()
        results = []

        for doc_id, doc_data in self._documents.items():
            content = doc_data["content"].lower()
            if query_lower in content:
                results.append(doc_data["content"][:500])  # Return first 500 chars

        return results[:top_k]

    def get_sources(self) -> List[str]:
        """Get list of source IDs.

        Returns:
            List of source IDs.
        """
        return list(self._documents.keys())

    def get_document(self, source_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific document by source ID.

        Args:
            source_id: Source identifier.

        Returns:
            Document data or None.
        """
        return self._documents.get(source_id)

    def list_all(self) -> Dict[str, Dict[str, Any]]:
        """List all documents.

        Returns:
            Dictionary of source IDs to document data.
        """
        return self._documents.copy()


class KnowledgeService:
    """Service for managing CrewAI Knowledge sources.

    This service provides a unified interface for managing knowledge sources
    with support for multiple backends (in-memory, vector stores, etc.).
    """

    def __init__(
        self,
        default_source: Optional[BaseKnowledgeSource] = None,
        vector_store_type: str = "in_memory",
    ) -> None:
        """Initialize the KnowledgeService.

        Args:
            default_source: Default knowledge source to use.
            vector_store_type: Type of vector store to use.
        """
        self._sources: Dict[str, BaseKnowledgeSource] = {}
        self._default_source = default_source or InMemoryKnowledgeSource("default")
        self._vector_store_type = vector_store_type

        # Register default source
        self.add_source(self._default_source, is_default=True)

        logger.info(f"KnowledgeService initialized with {vector_store_type} store")

    def add_source(
        self,
        source: BaseKnowledgeSource,
        source_id: Optional[str] = None,
        is_default: bool = False,
    ) -> str:
        """Add a knowledge source.

        Args:
            source: Knowledge source instance.
            source_id: Optional source identifier.
            is_default: Whether to set as default source.

        Returns:
            Source ID.
        """
        source_id = source_id or f"source_{len(self._sources) + 1}"
        self._sources[source_id] = source

        if is_default:
            self._default_source = source

        logger.info(f"Added knowledge source: {source_id}")
        return source_id

    def get_source(self, source_id: str) -> Optional[BaseKnowledgeSource]:
        """Get a knowledge source by ID.

        Args:
            source_id: Source identifier.

        Returns:
            Knowledge source or None.
        """
        return self._sources.get(source_id)

    def get_default_source(self) -> BaseKnowledgeSource:
        """Get the default knowledge source.

        Returns:
            Default knowledge source.
        """
        return self._default_source

    def add_document(
        self,
        content: str,
        source_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> str:
        """Add a document to the default knowledge source.

        Args:
            content: Document content.
            source_id: Optional source identifier.
            metadata: Optional metadata.

        Returns:
            Source ID.
        """
        return self._default_source.add_content(
            content=content,
            source_id=source_id,
            metadata=metadata,
            **kwargs,
        )

    def add_url(self, url: str, **kwargs) -> str:
        """Add content from a URL.

        Args:
            url: URL to fetch content from.

        Returns:
            Source ID.
        """
        try:
            import httpx

            with httpx.Client() as client:
                response = client.get(url, timeout=30.0)
                response.raise_for_status()
                content = response.text

            source_id = self._default_source.add_content(
                content=content[:10000],  # Limit content size
                metadata={"url": url, "type": "url"},
            )
            logger.info(f"Added URL content: {url}")
            return source_id

        except Exception as e:
            logger.error(f"Failed to add URL: {url} - {str(e)}")
            raise

    def add_text(self, text: str, source_id: Optional[str] = None, **kwargs) -> str:
        """Add text content.

        Args:
            text: Text content.
            source_id: Optional source identifier.

        Returns:
            Source ID.
        """
        return self._default_source.add_content(
            content=text,
            source_id=source_id,
            metadata={"type": "text"},
            **kwargs,
        )

    def query(self, query: str, source_id: Optional[str] = None, top_k: int = 5, **kwargs) -> List[str]:
        """Query knowledge sources.

        Args:
            query: Search query.
            source_id: Optional specific source to query.
            top_k: Maximum number of results.

        Returns:
            List of matching content snippets.
        """
        if source_id:
            source = self.get_source(source_id)
            if source:
                return source.query(query, top_k=top_k, **kwargs)
            return []

        # Query all sources
        results = []
        for source in self._sources.values():
            source_results = source.query(query, top_k=top_k, **kwargs)
            results.extend(source_results)

        return results[:top_k]

    def list_sources(self) -> List[Dict[str, Any]]:
        """List all knowledge sources.

        Returns:
            List of source information dictionaries.
        """
        source_list = []
        for source_id, source in self._sources.items():
            source_info = {
                "source_id": source_id,
                "name": getattr(source, "name", "Unknown"),
                "type": type(source).__name__,
                "document_count": len(source.get_sources()) if hasattr(source, "get_sources") else 0,
            }
            source_list.append(source_info)

        return source_list

    def list_sources_by_id(self) -> List[str]:
        """Get list of source IDs.

        Returns:
            List of source IDs.
        """
        return list(self._sources.keys())

    def remove_source(self, source_id: str) -> bool:
        """Remove a knowledge source.

        Args:
            source_id: Source identifier.

        Returns:
            True if removed, False otherwise.
        """
        if source_id in self._sources:
            del self._sources[source_id]
            logger.info(f"Removed knowledge source: {source_id}")
            return True
        return False

    def clear(self) -> None:
        """Clear all knowledge sources except default."""
        self._sources = {}
        self._sources["default"] = self._default_source
        logger.info("Cleared all non-default knowledge sources")

    def get_stats(self) -> Dict[str, Any]:
        """Get knowledge service statistics.

        Returns:
            Dictionary of statistics.
        """
        total_documents = 0
        for source in self._sources.values():
            if hasattr(source, "get_sources"):
                total_documents += len(source.get_sources())

        return {
            "source_count": len(self._sources),
            "total_documents": total_documents,
            "vector_store_type": self._vector_store_type,
        }


def create_knowledge_service(vector_store_type: str = "in_memory") -> KnowledgeService:
    """Create a KnowledgeService instance.

    Args:
        vector_store_type: Type of vector store to use.

    Returns:
        KnowledgeService instance.
    """
    return KnowledgeService(vector_store_type=vector_store_type)
