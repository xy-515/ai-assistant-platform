#!/usr/bin/env python3
"""One-click startup: FastAPI backend + Vue frontend"""
import subprocess
import sys
import time
import webbrowser
from pathlib import Path

ROOT = Path(__file__).parent


def main():
    print("=" * 55)
    print("  AI Assistant Platform — Starting...")
    print("=" * 55)

    # 1. Start backend
    print("\n[1/2] Starting FastAPI backend (port 8000)...")
    backend = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "main:app", "--port", "8000"],
        cwd=str(ROOT / "backend"),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    time.sleep(1.5)

    # 2. Start frontend
    print("[2/2] Starting Vue frontend (port 5173)...")
    npm_cmd = "npm.cmd" if sys.platform == "win32" else "npm"
    frontend = subprocess.Popen(
        [npm_cmd, "run", "dev"],
        cwd=str(ROOT / "frontend"),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    time.sleep(2)

    print("\n" + "=" * 55)
    print("  Backend:  http://localhost:8000/docs")
    print("  Frontend: http://localhost:5173")
    print("=" * 55)
    print("\nPress Ctrl+C to stop all services...")

    webbrowser.open("http://localhost:5173")

    try:
        backend.wait()
        frontend.wait()
    except KeyboardInterrupt:
        print("\nStopping...")
        backend.terminate()
        frontend.terminate()
        print("All services stopped.")


if __name__ == "__main__":
    main()
