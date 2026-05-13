"""
Automated tests for the Todo API.
Each test gets a fresh SQLite file via the `client` fixture — fully isolated.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import create_app
from app.database import init_db


# ── Fixtures ───────────────────────────────────────────────────────────────────

@pytest.fixture
def client(tmp_path):
    """TestClient backed by a fresh per-test SQLite database."""
    db_file = tmp_path / "test_todos.db"
    init_db(db_file)
    app = create_app(db_path=db_file)
    with TestClient(app) as c:
        yield c


# ── Helper ─────────────────────────────────────────────────────────────────────

def create_task(client, title="Buy groceries", description="Milk and eggs"):
    return client.post("/api/todos", json={"title": title, "description": description})


# ── GET /api/todos ─────────────────────────────────────────────────────────────

class TestListTodos:
    def test_empty_list(self, client):
        res = client.get("/api/todos")
        assert res.status_code == 200
        assert res.json() == []

    def test_returns_created_tasks(self, client):
        create_task(client, "Task A")
        create_task(client, "Task B")
        res = client.get("/api/todos")
        assert res.status_code == 200
        assert len(res.json()) == 2

    def test_filter_by_pending(self, client):
        r1 = create_task(client, "Pending task")
        r2 = create_task(client, "Done task")
        client.patch(f"/api/todos/{r2.json()['id']}", json={"status": "done"})

        res = client.get("/api/todos?status=pending")
        assert res.status_code == 200
        data = res.json()
        assert len(data) == 1
        assert data[0]["status"] == "pending"

    def test_filter_by_done(self, client):
        r1 = create_task(client, "Task 1")
        client.patch(f"/api/todos/{r1.json()['id']}", json={"status": "done"})
        create_task(client, "Task 2")

        res = client.get("/api/todos?status=done")
        assert res.status_code == 200
        data = res.json()
        assert len(data) == 1
        assert data[0]["status"] == "done"

    def test_invalid_status_filter(self, client):
        res = client.get("/api/todos?status=invalid")
        assert res.status_code == 422


# ── GET /api/todos/{id} ────────────────────────────────────────────────────────

class TestGetTodo:
    def test_get_existing_task(self, client):
        created = create_task(client, "My task", "My desc").json()
        res = client.get(f"/api/todos/{created['id']}")
        assert res.status_code == 200
        assert res.json()["title"] == "My task"
        assert res.json()["description"] == "My desc"

    def test_get_nonexistent_task_returns_404(self, client):
        res = client.get("/api/todos/9999")
        assert res.status_code == 404
        assert "9999" in res.json()["detail"]

    def test_response_has_required_fields(self, client):
        created = create_task(client).json()
        res = client.get(f"/api/todos/{created['id']}")
        data = res.json()
        for field in ("id", "title", "description", "status", "created_at", "updated_at"):
            assert field in data, f"Missing field: {field}"


# ── POST /api/todos ────────────────────────────────────────────────────────────

class TestCreateTodo:
    def test_create_with_title_and_description(self, client):
        res = client.post("/api/todos", json={"title": "Buy milk", "description": "Whole milk"})
        assert res.status_code == 201
        data = res.json()
        assert data["title"] == "Buy milk"
        assert data["description"] == "Whole milk"
        assert data["status"] == "pending"
        assert data["id"] is not None

    def test_create_with_title_only(self, client):
        res = client.post("/api/todos", json={"title": "Minimal task"})
        assert res.status_code == 201
        assert res.json()["description"] == ""

    def test_create_without_title_returns_422(self, client):
        res = client.post("/api/todos", json={"description": "No title here"})
        assert res.status_code == 422

    def test_create_with_empty_title_returns_422(self, client):
        res = client.post("/api/todos", json={"title": ""})
        assert res.status_code == 422

    def test_create_with_title_too_long_returns_422(self, client):
        res = client.post("/api/todos", json={"title": "x" * 256})
        assert res.status_code == 422


# ── PATCH /api/todos/{id} ──────────────────────────────────────────────────────

class TestUpdateTodo:
    def test_update_title(self, client):
        created = create_task(client, "Old title").json()
        res = client.patch(f"/api/todos/{created['id']}", json={"title": "New title"})
        assert res.status_code == 200
        assert res.json()["title"] == "New title"

    def test_update_status_to_done(self, client):
        created = create_task(client).json()
        res = client.patch(f"/api/todos/{created['id']}", json={"status": "done"})
        assert res.status_code == 200
        assert res.json()["status"] == "done"

    def test_update_multiple_fields(self, client):
        created = create_task(client, "Old", "Old desc").json()
        res = client.patch(
            f"/api/todos/{created['id']}",
            json={"title": "New", "description": "New desc", "status": "done"},
        )
        assert res.status_code == 200
        data = res.json()
        assert data["title"] == "New"
        assert data["description"] == "New desc"
        assert data["status"] == "done"

    def test_update_nonexistent_returns_404(self, client):
        res = client.patch("/api/todos/9999", json={"title": "Ghost"})
        assert res.status_code == 404

    def test_update_with_invalid_status_returns_422(self, client):
        created = create_task(client).json()
        res = client.patch(f"/api/todos/{created['id']}", json={"status": "in-progress"})
        assert res.status_code == 422

    def test_update_with_unknown_field_returns_422(self, client):
        created = create_task(client).json()
        res = client.patch(f"/api/todos/{created['id']}", json={"priority": "high"})
        assert res.status_code == 422


# ── DELETE /api/todos/{id} ─────────────────────────────────────────────────────

class TestDeleteTodo:
    def test_delete_existing_task(self, client):
        created = create_task(client).json()
        res = client.delete(f"/api/todos/{created['id']}")
        assert res.status_code == 204

    def test_deleted_task_is_gone(self, client):
        created = create_task(client).json()
        client.delete(f"/api/todos/{created['id']}")
        res = client.get(f"/api/todos/{created['id']}")
        assert res.status_code == 404

    def test_delete_nonexistent_returns_404(self, client):
        res = client.delete("/api/todos/9999")
        assert res.status_code == 404

    def test_delete_reduces_list_count(self, client):
        r1 = create_task(client, "Task 1").json()
        create_task(client, "Task 2")
        client.delete(f"/api/todos/{r1['id']}")
        res = client.get("/api/todos")
        assert len(res.json()) == 1
