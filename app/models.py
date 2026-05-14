"""Pydantic models for request validation and response serialization."""

from typing import Literal, Optional

from pydantic import BaseModel, Field

TodoStatus = Literal["pending", "done"]


class TodoCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)


class TodoUpdate(BaseModel):
    model_config = {"extra": "forbid"}

    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    status: Optional[TodoStatus] = None


class TodoResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    status: TodoStatus
    created_at: str
