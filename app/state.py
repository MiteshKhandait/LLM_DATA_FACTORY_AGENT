from typing import Any, Literal

from pydantic import BaseModel, Field

from app.models import Document


class ToolCallRecord(BaseModel):
    """
    Records one tool selected and executed by the agent.
    """

    tool_name: str
    arguments: dict[str, Any] = Field(default_factory=dict)
    iteration: int
    status: Literal["requested", "completed", "failed"] = "requested"


class ToolResultRecord(BaseModel):
    """
    Stores the result returned by a tool.
    """

    tool_name: str
    result: dict[str, Any]
    iteration: int


class AgentState(BaseModel):
    """
    Complete state of one agent execution.
    """

    user_request: str
    document: Document

    status: Literal[
        "pending",
        "running",
        "completed",
        "failed",
    ] = "pending"

    iteration: int = 0

    tool_calls: list[ToolCallRecord] = Field(
        default_factory=list
    )

    tool_results: list[ToolResultRecord] = Field(
        default_factory=list
    )

    final_response: str | None = None

    error: str | None = None