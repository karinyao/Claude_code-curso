#!/usr/bin/env python3
"""
start.py — Arranca la API (puerto 8000) y el dashboard Streamlit (puerto 8501)
en paralelo desde un solo comando.

Uso:
    python start.py

Detener: Ctrl+C (mata ambos procesos).
"""

import subprocess
import sys
import time
import signal
import os


def main():
    print("🚀 Arrancando Todo App...\n")

    # ── 1. Levantar la API en segundo plano ─────────────────────────────────────
    api_proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    print(f"✅ API arrancando  →  http://localhost:8000  (PID {api_proc.pid})")
    print(f"   Docs disponibles en  →  http://localhost:8000/docs\n")

    # Espera breve para que la API inicialice la DB antes de que Streamlit haga peticiones
    time.sleep(2)

    # ── 2. Levantar Streamlit en primer plano ───────────────────────────────────
    streamlit_proc = subprocess.Popen(
        [
            sys.executable, "-m", "streamlit", "run", "dashboard.py",
            "--server.port", "8501",
            "--server.headless", "true",
            "--browser.gatherUsageStats", "false",
        ],
    )
    print(f"✅ Dashboard arrancando  →  http://localhost:8501  (PID {streamlit_proc.pid})")
    print("\n   Presiona Ctrl+C para detener ambos procesos.\n")

    # ── Gestión de señales — Ctrl+C mata ambos ──────────────────────────────────
    def shutdown(sig, frame):
        print("\n\n🛑 Deteniendo servicios...")
        streamlit_proc.terminate()
        api_proc.terminate()
        streamlit_proc.wait()
        api_proc.wait()
        print("   Todo detenido. ¡Hasta pronto!")
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    # ── Monitoreo — si la API muere, avisamos ───────────────────────────────────
    while True:
        if api_proc.poll() is not None:
            print("⚠️  La API se detuvo inesperadamente.")
            streamlit_proc.terminate()
            break
        if streamlit_proc.poll() is not None:
            print("⚠️  Streamlit se detuvo inesperadamente.")
            api_proc.terminate()
            break
        time.sleep(1)


if __name__ == "__main__":
    main()
