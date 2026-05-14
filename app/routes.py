"""The 5 REST endpoints for /api/todos."""

from typing import Literal, Optional

from fastapi import APIRouter, HTTPException, Query, Request

from .crud import (
    create_todo,
    delete_todo,
    get_todo,
    list_todos,
    update_todo,
)
from .database import get_connection
from .models import TodoCreate, TodoResponse, TodoUpdate

router = APIRouter(prefix="/api/todos", tags=["todos"])

StatusFilter = Literal["pending", "done"]


def _conn(request: Request):
    return get_connection(request.app.state.db_path)


@router.get("", response_model=list[TodoResponse])
def list_endpoint(
    request: Request,
    status: Optional[StatusFilter] = Query(None),
):
    with _conn(request) as conn:
        return list_todos(conn, status)


@router.get("/{todo_id}", response_model=TodoResponse)
def get_endpoint(todo_id: int, request: Request):
    with _conn(request) as conn:
        todo = get_todo(conn, todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo


@router.post("", response_model=TodoResponse, status_code=201)
def create_endpoint(payload: TodoCreate, request: Request):
    with _conn(request) as conn:
        return create_todo(conn, payload.title, payload.description)


@router.patch("/{todo_id}", response_model=TodoResponse)
def update_endpoint(todo_id: int, payload: TodoUpdate, request: Request):
    fields = payload.model_dump(exclude_none=True)
    with _conn(request) as conn:
        if not get_todo(conn, todo_id):
            raise HTTPException(status_code=404, detail="Todo not found")
        return update_todo(conn, todo_id, fields)


@router.delete("/{todo_id}", status_code=204)
def delete_endpoint(todo_id: int, request: Request):
    with _conn(request) as conn:
        if not delete_todo(conn, todo_id):
            raise HTTPException(status_code=404, detail="Todo not found")
