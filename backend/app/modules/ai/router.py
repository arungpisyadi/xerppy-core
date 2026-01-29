"""AI Router

API endpoints for CrewAI Flows and related operations.
"""

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai", tags=["AI"])

# Flow instances registry (in production, use proper state management)
_flows: Dict[str, Any] = {}


# Request/Response Models
class FlowRunRequest(BaseModel):
    """Request model for running a flow."""

    flow_type: str = Field(default="example", description="Type of flow to run")
    inputs: Dict[str, Any] = Field(default_factory=dict, description="Input parameters")
    enable_memory: bool = Field(default=True, description="Enable memory features")
    enable_knowledge: bool = Field(default=False, description="Enable knowledge features")


class FlowResponse(BaseModel):
    """Response model for flow execution."""

    flow_id: str
    status: str
    inputs: Dict[str, Any]
    outputs: Dict[str, Any]
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error: Optional[str] = None


class FlowStatusResponse(BaseModel):
    """Response model for flow status."""

    flow_id: str
    flow_type: str
    status: str
    available_agents: List[str]
    available_tasks: List[str]
    state: Dict[str, Any]


class KnowledgeAddRequest(BaseModel):
    """Request model for adding knowledge."""

    content: str = Field(..., description="Content to add")
    source_type: str = Field(default="text", description="Type of source")
    metadata: Optional[Dict[str, Any]] = None


class KnowledgeQueryRequest(BaseModel):
    """Request model for querying knowledge."""

    query: str = Field(..., description="Query string")
    top_k: int = Field(default=5, description="Maximum results")


class KnowledgeResponse(BaseModel):
    """Response model for knowledge operations."""

    sources: List[Dict[str, Any]]
    query_results: List[str]


@router.post("/flows/run")
async def run_flow(request: FlowRunRequest) -> FlowResponse:
    """Run an AI flow.

    Args:
        request: Flow run request parameters.

    Returns:
        Flow execution results.
    """
    try:
        # Import flow classes
        from .flows.example_flow import ExampleFlow

        # Create flow instance
        flow = ExampleFlow(
            flow_id=f"flow_{request.flow_type}",
            enable_memory=request.enable_memory,
            enable_knowledge=request.enable_knowledge,
        )

        # Store flow instance
        _flows[flow._flow_id] = flow

        # Run the flow
        state = flow.run(request.inputs)

        return FlowResponse(
            flow_id=state.flow_id,
            status=state.status,
            inputs=state.inputs,
            outputs=state.outputs,
            started_at=state.started_at.isoformat() if state.started_at else None,
            completed_at=state.completed_at.isoformat() if state.completed_at else None,
            error=state.error,
        )

    except Exception as e:
        logger.error(f"Flow execution failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/flows/example")
async def run_example_flow(inputs: Dict[str, Any]) -> FlowResponse:
    """Run the example flow.

    Args:
        inputs: Input parameters for the flow.

    Returns:
        Flow execution results.
    """
    try:
        from .flows.example_flow import ExampleFlow

        flow = ExampleFlow()
        state = flow.run(inputs)

        return FlowResponse(
            flow_id=state.flow_id,
            status=state.status,
            inputs=state.inputs,
            outputs=state.outputs,
            started_at=state.started_at.isoformat() if state.started_at else None,
            completed_at=state.completed_at.isoformat() if state.completed_at else None,
            error=state.error,
        )

    except Exception as e:
        logger.error(f"Example flow execution failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/flows/status/{flow_id}")
async def get_flow_status(flow_id: str) -> FlowStatusResponse:
    """Get the status of a flow.

    Args:
        flow_id: ID of the flow to check.

    Returns:
        Current flow status.
    """
    flow = _flows.get(flow_id)
    if not flow:
        raise HTTPException(status_code=404, detail=f"Flow not found: {flow_id}")

    state = flow.get_state()

    # Get available agents and tasks
    agents = flow.crew_factory.get_available_agents() if flow.crew_factory else []
    tasks = flow.crew_factory.get_available_tasks() if flow.crew_factory else []

    return FlowStatusResponse(
        flow_id=flow_id,
        flow_type=state.name,
        status=state.status,
        available_agents=agents,
        available_tasks=tasks,
        state={
            "inputs": state.inputs,
            "outputs": state.outputs,
            "memory": state.memory,
            "error": state.error,
        },
    )


@router.get("/flows/list")
async def list_flows() -> Dict[str, List[str]]:
    """List all running flows.

    Returns:
        List of flow IDs.
    """
    return {"flows": list(_flows.keys())}


@router.delete("/flows/{flow_id}")
async def delete_flow(flow_id: str) -> Dict[str, str]:
    """Delete a flow instance.

    Args:
        flow_id: ID of the flow to delete.

    Returns:
        Confirmation message.
    """
    if flow_id in _flows:
        del _flows[flow_id]
        return {"message": f"Flow deleted: {flow_id}"}
    raise HTTPException(status_code=404, detail=f"Flow not found: {flow_id}")


@router.get("/knowledge/sources")
async def list_knowledge_sources() -> Dict[str, Any]:
    """List all knowledge sources.

    Returns:
        List of knowledge sources with stats.
    """
    try:
        from .knowledge import KnowledgeService

        knowledge = KnowledgeService()
        stats = knowledge.get_stats()
        sources = knowledge.list_sources()

        return {
            "stats": stats,
            "sources": sources,
        }

    except Exception as e:
        logger.error(f"Failed to list knowledge sources: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/knowledge/add")
async def add_knowledge(request: KnowledgeAddRequest) -> Dict[str, Any]:
    """Add content to the knowledge base.

    Args:
        request: Knowledge to add.

    Returns:
        Source ID of added content.
    """
    try:
        from .knowledge import KnowledgeService

        knowledge = KnowledgeService()

        if request.source_type == "text":
            source_id = knowledge.add_text(request.content)
        else:
            source_id = knowledge.add_document(
                content=request.content,
                metadata=request.metadata,
            )

        return {
            "source_id": source_id,
            "message": "Content added successfully",
        }

    except Exception as e:
        logger.error(f"Failed to add knowledge: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/knowledge/query")
async def query_knowledge(request: KnowledgeQueryRequest) -> KnowledgeResponse:
    """Query the knowledge base.

    Args:
        request: Query parameters.

    Returns:
        Query results.
    """
    try:
        from .knowledge import KnowledgeService

        knowledge = KnowledgeService()
        results = knowledge.query(request.query, top_k=request.top_k)
        sources = knowledge.list_sources()

        return KnowledgeResponse(
            sources=sources,
            query_results=results,
        )

    except Exception as e:
        logger.error(f"Knowledge query failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/config/agents")
async def list_agents() -> Dict[str, List[str]]:
    """List available agents from configuration.

    Returns:
        List of agent names.
    """
    try:
        from .config.agents import get_agents_config

        config = get_agents_config()
        agents = config.get_agent_names()

        return {
            "agents": agents,
            "count": len(agents),
        }

    except Exception as e:
        logger.error(f"Failed to list agents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/config/tasks")
async def list_tasks() -> Dict[str, Any]:
    """List available tasks from configuration.

    Returns:
        List of task names and details.
    """
    try:
        from .config.tasks import get_tasks_config

        config = get_tasks_config()
        tasks = config.get_task_names()

        # Get task details
        task_details = []
        for name in tasks:
            task = config.get_task(name)
            if task:
                task_details.append({
                    "name": task.name,
                    "agent": task.agent,
                    "async_execution": task.async_execution,
                })

        return {
            "tasks": tasks,
            "task_details": task_details,
            "count": len(tasks),
        }

    except Exception as e:
        logger.error(f"Failed to list tasks: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def ai_health_check() -> Dict[str, str]:
    """Health check for AI module.

    Returns:
        Health status.
    """
    return {
        "status": "healthy",
        "module": "ai",
        "flows_registered": len(_flows),
    }
