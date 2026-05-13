"""23 tests for the Todo REST API. Each test uses an isolated SQLite DB."""

import pytest
from fastapi.testclient import TestClient

from app.main import create_app


@pytest.fixture
def client(tmp_path):
    db_path = tmp_path / "test.db"
    app = create_app(db_path=str(db_path))
    with TestClient(app) as c:
        yield c


def _create(client, title="Tarea", description=None):
    payload = {"title": title}
    if description is not None:
        payload["description"] = description
    r = client.post("/api/todos", json=payload)
    assert r.status_code == 201
    return r.json()


# ── GET /api/todos ────────────────────────────────────────────────────────────

def test_list_empty(client):
    r = client.get("/api/todos")
    assert r.status_code == 200
    assert r.json() == []


def test_list_with_items(client):
    _create(client, "A")
    _create(client, "B")
    r = client.get("/api/todos")
    assert r.status_code == 200
    assert len(r.json()) == 2


def test_list_filter_pending(client):
    t1 = _create(client, "A")
    t2 = _create(client, "B")
    client.patch(f"/api/todos/{t2['id']}", json={"status": "done"})
    r = client.get("/api/todos?status=pending")
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 1
    assert data[0]["id"] == t1["id"]


def test_list_filter_done(client):
    _create(client, "A")
    t2 = _create(client, "B")
    client.patch(f"/api/todos/{t2['id']}", json={"status": "done"})
    r = client.get("/api/todos?status=done")
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 1
    assert data[0]["status"] == "done"


def test_list_filter_invalid(client):
    r = client.get("/api/todos?status=foobar")
    assert r.status_code == 422


# ── GET /api/todos/{id} ───────────────────────────────────────────────────────

def test_get_existing(client):
    created = _create(client, "Mi tarea")
    r = client.get(f"/api/todos/{created['id']}")
    assert r.status_code == 200
    assert r.json()["title"] == "Mi tarea"


def test_get_not_found(client):
    r = client.get("/api/todos/9999")
    assert r.status_code == 404


def test_get_response_fields(client):
    created = _create(client, "Test", "desc")
    r = client.get(f"/api/todos/{created['id']}")
    body = r.json()
    assert set(body.keys()) >= {"id", "title", "description", "status", "created_at"}
    assert body["status"] == "pending"
    assert body["description"] == "desc"


# ── POST /api/todos ───────────────────────────────────────────────────────────

def test_create_complete(client):
    r = client.post("/api/todos", json={"title": "T", "description": "D"})
    assert r.status_code == 201
    body = r.json()
    assert body["title"] == "T"
    assert body["description"] == "D"
    assert body["status"] == "pending"


def test_create_only_title(client):
    r = client.post("/api/todos", json={"title": "Solo título"})
    assert r.status_code == 201
    body = r.json()
    assert body["title"] == "Solo título"
    assert body["description"] is None


def test_create_no_title(client):
    r = client.post("/api/todos", json={"description": "sin título"})
    assert r.status_code == 422


def test_create_empty_title(client):
    r = client.post("/api/todos", json={"title": ""})
    assert r.status_code == 422


def test_create_title_too_long(client):
    r = client.post("/api/todos", json={"title": "x" * 500})
    assert r.status_code == 422


# ── PATCH /api/todos/{id} ─────────────────────────────────────────────────────

def test_patch_title(client):
    t = _create(client, "Original")
    r = client.patch(f"/api/todos/{t['id']}", json={"title": "Nuevo"})
    assert r.status_code == 200
    assert r.json()["title"] == "Nuevo"


def test_patch_status(client):
    t = _create(client, "Tarea")
    r = client.patch(f"/api/todos/{t['id']}", json={"status": "done"})
    assert r.status_code == 200
    assert r.json()["status"] == "done"


def test_patch_multiple_fields(client):
    t = _create(client, "A")
    r = client.patch(
        f"/api/todos/{t['id']}",
        json={"title": "B", "description": "C", "status": "done"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["title"] == "B"
    assert body["description"] == "C"
    assert body["status"] == "done"


def test_patch_not_found(client):
    r = client.patch("/api/todos/9999", json={"title": "X"})
    assert r.status_code == 404


def test_patch_invalid_status(client):
    t = _create(client, "A")
    r = client.patch(f"/api/todos/{t['id']}", json={"status": "in_progress"})
    assert r.status_code == 422


def test_patch_unknown_field(client):
    t = _create(client, "A")
    r = client.patch(f"/api/todos/{t['id']}", json={"foo": "bar"})
    assert r.status_code == 422


# ── DELETE /api/todos/{id} ────────────────────────────────────────────────────

def test_delete_success(client):
    t = _create(client, "Borrar")
    r = client.delete(f"/api/todos/{t['id']}")
    assert r.status_code == 204


def test_delete_verify_removed(client):
    t = _create(client, "Borrar")
    client.delete(f"/api/todos/{t['id']}")
    r = client.get(f"/api/todos/{t['id']}")
    assert r.status_code == 404


def test_delete_not_found(client):
    r = client.delete("/api/todos/9999")
    assert r.status_code == 404


def test_delete_count_decreases(client):
    _create(client, "A")
    t = _create(client, "B")
    _create(client, "C")
    assert len(client.get("/api/todos").json()) == 3
    client.delete(f"/api/todos/{t['id']}")
    assert len(client.get("/api/todos").json()) == 2
