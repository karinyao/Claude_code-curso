from typing import Literal, Optional
from fastapi import APIRouter, HTTPException, Query, Request
from .models import TodoCreate, TodoResponse, TodoUpdate
from . import crud

router = APIRouter(prefix="/api/todos", tags=["todos"])


def _db(request: Request):
    """Helper: pull the db_path from the app's state."""
    return request.app.state.db_path


@router.get("", response_model=list[TodoResponse])
def list_todos(
    request: Request,
    status: Optional[Literal["pending", "done"]] = Query(
        default=None,
        description="Filter by status: 'pending' or 'done'",
    ),
):
    return crud.get_all_todos(status=status, db_path=_db(request))


@router.get("/{todo_id}", response_model=TodoResponse)
def get_todo(todo_id: int, request: Request):
    todo = crud.get_todo_by_id(todo_id, db_path=_db(request))
    if not todo:
        raise HTTPException(status_code=404, detail=f"Task {todo_id} not found")
    return todo


@router.post("", response_model=TodoResponse, status_code=201)
def create_todo(payload: TodoCreate, request: Request):
    return crud.create_todo(
        title=payload.title,
        description=payload.description or "",
        db_path=_db(request),
    )


@router.patch("/{todo_id}", response_model=TodoResponse)
def update_todo(todo_id: int, payload: TodoUpdate, request: Request):
    db = _db(request)
    if not crud.get_todo_by_id(todo_id, db_path=db):
        raise HTTPException(status_code=404, detail=f"Task {todo_id} not found")
    fields = payload.model_dump(exclude_none=True)
    return crud.update_todo(todo_id, fields, db_path=db)


@router.delete("/{todo_id}", status_code=204)
def delete_todo(todo_id: int, request: Request):
    if not crud.delete_todo(todo_id, db_path=_db(request)):
        raise HTTPException(status_code=404, detail=f"Task {todo_id} not found")
