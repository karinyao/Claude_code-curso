"""
Todo Dashboard — Streamlit frontend for the Todo REST API.
Runs alongside the FastAPI backend (default: http://localhost:8000).
"""

import requests
import streamlit as st

# ── Config ─────────────────────────────────────────────────────────────────────

API_BASE = "http://localhost:8000/api/todos"

st.set_page_config(
    page_title="Todo Dashboard",
    page_icon="✅",
    layout="wide",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────

st.markdown("""
<style>
    /* General */
    .block-container { padding-top: 2rem; max-width: 900px; }

    /* Summary cards */
    .summary-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1rem 1.5rem;
        text-align: center;
    }
    .summary-card .number {
        font-size: 2.2rem;
        font-weight: 700;
        line-height: 1;
    }
    .summary-card .label {
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #64748b;
        margin-top: 4px;
    }
    .num-total   { color: #1e40af; }
    .num-pending { color: #b45309; }
    .num-done    { color: #15803d; }

    /* Task rows */
    .task-row {
        border-radius: 10px;
        padding: 0.75rem 1rem;
        margin-bottom: 0.5rem;
        border-left: 4px solid transparent;
    }
    .task-pending {
        background: #fffbeb;
        border-left-color: #f59e0b;
    }
    .task-done {
        background: #f0fdf4;
        border-left-color: #22c55e;
        opacity: 0.75;
    }
    .task-title-pending { font-weight: 600; color: #1e293b; }
    .task-title-done    { font-weight: 600; color: #6b7280; text-decoration: line-through; }
    .task-meta          { font-size: 0.78rem; color: #94a3b8; margin-top: 2px; }
    .badge-pending {
        display: inline-block;
        background: #fef3c7; color: #92400e;
        border-radius: 9999px; padding: 1px 8px;
        font-size: 0.72rem; font-weight: 600;
    }
    .badge-done {
        display: inline-block;
        background: #dcfce7; color: #166534;
        border-radius: 9999px; padding: 1px 8px;
        font-size: 0.72rem; font-weight: 600;
    }
    /* Sidebar form */
    section[data-testid="stSidebar"] { background: #f1f5f9; }
</style>
""", unsafe_allow_html=True)


# ── API helpers ────────────────────────────────────────────────────────────────

def api_get_all(status_filter: str = "all") -> list[dict]:
    params = {} if status_filter == "all" else {"status": status_filter}
    try:
        r = requests.get(API_BASE, params=params, timeout=5)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        st.error("⚠️ No se puede conectar a la API. ¿Está corriendo en http://localhost:8000?")
        return []
    except Exception as e:
        st.error(f"Error al cargar tareas: {e}")
        return []


def api_create(title: str, description: str) -> bool:
    try:
        r = requests.post(API_BASE, json={"title": title, "description": description}, timeout=5)
        return r.status_code == 201
    except Exception as e:
        st.error(f"Error al crear tarea: {e}")
        return False


def api_complete(todo_id: int) -> bool:
    try:
        r = requests.patch(f"{API_BASE}/{todo_id}", json={"status": "done"}, timeout=5)
        return r.status_code == 200
    except Exception as e:
        st.error(f"Error al completar tarea: {e}")
        return False


def api_delete(todo_id: int) -> bool:
    try:
        r = requests.delete(f"{API_BASE}/{todo_id}", timeout=5)
        return r.status_code == 204
    except Exception as e:
        st.error(f"Error al eliminar tarea: {e}")
        return False


# ── Sidebar — New task form ────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## ➕ Nueva tarea")
    with st.form("create_form", clear_on_submit=True):
        new_title = st.text_input("Título *", placeholder="ej. Revisar el pipeline")
        new_desc  = st.text_area("Descripción", placeholder="Detalles opcionales…", height=100)
        submitted = st.form_submit_button("Crear tarea", use_container_width=True, type="primary")

    if submitted:
        if not new_title.strip():
            st.warning("El título es obligatorio.")
        else:
            if api_create(new_title.strip(), new_desc.strip()):
                st.success("✅ Tarea creada.")
                st.rerun()

    st.divider()
    st.markdown("#### 🔍 Filtrar")
    status_filter = st.radio(
        "Estado",
        options=["all", "pending", "done"],
        format_func=lambda x: {"all": "Todas", "pending": "⏳ Pendientes", "done": "✅ Completadas"}[x],
        label_visibility="collapsed",
    )

    st.divider()
    if st.button("🔄 Actualizar", use_container_width=True):
        st.rerun()


# ── Main area ──────────────────────────────────────────────────────────────────

st.markdown("# ✅ Todo Dashboard")
st.caption("Panel de control — conectado a la API REST local")

todos = api_get_all(status_filter)

# Summary cards
total   = len(api_get_all("all"))   # always counts all
pending = len([t for t in api_get_all("all") if t["status"] == "pending"])
done    = total - pending

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(f"""
    <div class="summary-card">
        <div class="number num-total">{total}</div>
        <div class="label">Total</div>
    </div>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""
    <div class="summary-card">
        <div class="number num-pending">{pending}</div>
        <div class="label">Pendientes</div>
    </div>""", unsafe_allow_html=True)
with c3:
    st.markdown(f"""
    <div class="summary-card">
        <div class="number num-done">{done}</div>
        <div class="label">Completadas</div>
    </div>""", unsafe_allow_html=True)

st.markdown("---")

# Task list
if not todos:
    label = {
        "all":     "No hay tareas todavía. Crea una desde el panel izquierdo.",
        "pending": "No hay tareas pendientes. 🎉",
        "done":    "No hay tareas completadas aún.",
    }[status_filter]
    st.info(label)
else:
    filter_label = {"all": "Todas las tareas", "pending": "⏳ Pendientes", "done": "✅ Completadas"}
    st.markdown(f"### {filter_label[status_filter]} ({len(todos)})")

    for todo in todos:
        is_done   = todo["status"] == "done"
        row_class = "task-done" if is_done else "task-pending"
        title_class = "task-title-done" if is_done else "task-title-pending"
        badge = '<span class="badge-done">done</span>' if is_done else '<span class="badge-pending">pending</span>'
        desc_html = f'<div class="task-meta">{todo["description"]}</div>' if todo.get("description") else ""

        col_text, col_actions = st.columns([6, 1])

        with col_text:
            st.markdown(f"""
            <div class="task-row {row_class}">
                <div class="{title_class}">#{todo['id']} &nbsp; {todo['title']} &nbsp; {badge}</div>
                {desc_html}
                <div class="task-meta">Creada: {todo['created_at'][:16].replace('T', ' ')}</div>
            </div>
            """, unsafe_allow_html=True)

        with col_actions:
            st.write("")  # vertical spacing
            if not is_done:
                if st.button("✔", key=f"done_{todo['id']}", help="Marcar como completada"):
                    if api_complete(todo["id"]):
                        st.rerun()
            if st.button("🗑", key=f"del_{todo['id']}", help="Eliminar tarea"):
                if api_delete(todo["id"]):
                    st.rerun()
