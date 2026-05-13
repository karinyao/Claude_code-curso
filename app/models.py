from typing import Literal, Optional
from pydantic import BaseModel, Field


# ── Response model (what the API returns) ──────────────────────────────────────

class TodoResponse(BaseModel):
    id: int
    title: str
    description: str
    status: Literal["pending", "done"]
    created_at: str
    updated_at: str


# ── Request models (validated input) ──────────────────────────────────────────

class TodoCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="Task title (required)")
    description: Optional[str] = Field(default="", max_length=1000, description="Task description (optional)")


class TodoUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    status: Optional[Literal["pending", "done"]] = None

    model_config = {"extra": "forbid"}  # Reject unknown fields
