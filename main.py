#!/usr/bin/env python3
"""Drishti RAG Assistant — Full-Stack Runner

Orchestrates:
1. Ollama model service (qwen3.5:4b)
2. FastAPI backend (http://localhost:8000)
3. Vite kiosk UI (http://localhost:5173)

Handles graceful shutdown of all services on Ctrl+C (SIGINT) or SIGTERM.
"""

import os
import signal
import subprocess
import sys
import threading
import time
import urllib.request
import urllib.error
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
UI_DIR = ROOT_DIR / "ui"
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
MODEL_NAME = "qwen3.5:4b"
BACKEND_PORT = int(os.environ.get("PORT", 8000))
FRONTEND_PORT = int(os.environ.get("FRONTEND_PORT", 5173))

# ANSI Color codes for clean tagged logs
CYAN = "\033[36m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
MAGENTA = "\033[35m"
RED = "\033[31m"
BOLD = "\033[1m"
RESET = "\033[0m"

processes = []
shutting_down = False


def log(prefix: str, color: str, message: str):
    print(f"{color}{BOLD}[{prefix}]{RESET} {message}", flush=True)


def check_url(url: str, timeout: float = 2.0) -> bool:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            return resp.status in (200, 404)
    except (urllib.error.URLError, ConnectionRefusedError, TimeoutError, OSError):
        return False


def stream_output(pipe, prefix: str, color: str):
    """Read lines from subprocess stdout/stderr and print with tagged prefix."""
    try:
        for line in iter(pipe.readline, ""):
            if not line:
                break
            text = line.rstrip()
            if text:
                print(f"{color}[{prefix}]{RESET} {text}", flush=True)
    except (ValueError, OSError):
        pass
    finally:
        try:
            pipe.close()
        except Exception:
            pass


def ensure_ollama() -> subprocess.Popen | None:
    """Ensure Ollama is running and model qwen3.5:4b is available."""
    log("Ollama", CYAN, "Checking Ollama status...")
    ollama_proc = None

    if not check_url(f"{OLLAMA_HOST}/api/tags", timeout=1.5):
        log("Ollama", YELLOW, f"Ollama not detected at {OLLAMA_HOST}. Starting 'ollama serve'...")
        try:
            ollama_proc = subprocess.Popen(
                ["ollama", "serve"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )
            processes.append(ollama_proc)
            threading.Thread(
                target=stream_output,
                args=(ollama_proc.stdout, "Ollama", CYAN),
                daemon=True,
            ).start()
        except FileNotFoundError:
            log("Ollama", RED, "Error: 'ollama' binary not found in PATH. Please install Ollama.")
            sys.exit(1)

        # Wait for Ollama to become ready
        start_time = time.time()
        while time.time() - start_time < 15:
            if check_url(f"{OLLAMA_HOST}/api/tags", timeout=1.0):
                break
            time.sleep(0.5)
        else:
            log("Ollama", RED, "Timed out waiting for Ollama to start.")
            sys.exit(1)

    log("Ollama", GREEN, f"Ollama service is reachable at {OLLAMA_HOST}.")

    # Check if the model is downloaded
    try:
        req = urllib.request.Request(f"{OLLAMA_HOST}/api/tags")
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            data = resp.read().decode("utf-8")
            if MODEL_NAME in data:
                log("Ollama", GREEN, f"Model '{MODEL_NAME}' is ready.")
            else:
                log("Ollama", YELLOW, f"Model '{MODEL_NAME}' not found locally. Pulling model...")
                pull_code = subprocess.call(["ollama", "pull", MODEL_NAME])
                if pull_code == 0:
                    log("Ollama", GREEN, f"Model '{MODEL_NAME}' pulled successfully.")
                else:
                    log("Ollama", RED, f"Failed to pull model '{MODEL_NAME}'.")
    except Exception as err:
        log("Ollama", YELLOW, f"Could not verify models via tags endpoint: {err}")

    return ollama_proc


def start_backend() -> subprocess.Popen:
    """Start the FastAPI backend with uvicorn."""
    log("Backend", GREEN, f"Starting FastAPI backend on port {BACKEND_PORT}...")
    
    # Use uv run if uv is present, otherwise fallback to current python interpreter
    cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "src.server:app",
        "--host",
        "0.0.0.0",
        "--port",
        str(BACKEND_PORT),
    ]
    if (ROOT_DIR / ".venv").exists():
        uv_bin = shutil_which("uv")
        if uv_bin:
            cmd = ["uv", "run", "uvicorn", "src.server:app", "--host", "0.0.0.0", "--port", str(BACKEND_PORT)]

    proc = subprocess.Popen(
        cmd,
        cwd=str(ROOT_DIR),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )
    processes.append(proc)
    threading.Thread(
        target=stream_output,
        args=(proc.stdout, "Backend", GREEN),
        daemon=True,
    ).start()

    # Wait for backend to be ready
    health_url = f"http://localhost:{BACKEND_PORT}/api/health"
    start_time = time.time()
    while time.time() - start_time < 30:
        if check_url(health_url, timeout=1.0):
            log("Backend", GREEN, f"FastAPI backend is ready at http://localhost:{BACKEND_PORT}")
            break
        if proc.poll() is not None:
            log("Backend", RED, f"Backend process exited prematurely with code {proc.returncode}")
            sys.exit(1)
        time.sleep(0.5)
    else:
        log("Backend", YELLOW, "Backend took longer than 30s to respond to health check. Continuing...")

    return proc


def start_frontend() -> subprocess.Popen:
    """Start Vite dev server for the kiosk UI."""
    log("Frontend", MAGENTA, "Starting Vite Kiosk Frontend...")
    
    # Ensure node_modules exists
    if not (UI_DIR / "node_modules").exists():
        log("Frontend", YELLOW, "node_modules missing in ui/. Running 'npm install'...")
        npm_code = subprocess.call(["npm", "install"], cwd=str(UI_DIR))
        if npm_code != 0:
            log("Frontend", RED, "npm install failed.")
            sys.exit(1)

    cmd = ["npm", "run", "dev", "--", "--host", "--port", str(FRONTEND_PORT)]
    proc = subprocess.Popen(
        cmd,
        cwd=str(UI_DIR),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )
    processes.append(proc)
    threading.Thread(
        target=stream_output,
        args=(proc.stdout, "Frontend", MAGENTA),
        daemon=True,
    ).start()

    # Wait for frontend dev server
    start_time = time.time()
    while time.time() - start_time < 15:
        if check_url(f"http://localhost:{FRONTEND_PORT}", timeout=1.0):
            log("Frontend", GREEN, f"Vite Kiosk UI is ready at http://localhost:{FRONTEND_PORT}")
            break
        if proc.poll() is not None:
            log("Frontend", RED, f"Frontend process exited prematurely with code {proc.returncode}")
            sys.exit(1)
        time.sleep(0.5)
    else:
        log("Frontend", GREEN, f"Vite Kiosk UI is launching on port {FRONTEND_PORT}...")

    return proc


def shutil_which(cmd: str) -> str | None:
    import shutil
    return shutil.which(cmd)


def shutdown(signum=None, frame=None):
    """Gracefully terminate all child processes."""
    global shutting_down
    if shutting_down:
        return
    shutting_down = True

    print("\n", flush=True)
    log("Runner", YELLOW, "Shutting down all services gracefully...")

    for p in reversed(processes):
        if p and p.poll() is None:
            try:
                p.terminate()
            except Exception:
                pass

    time.sleep(1.0)

    for p in reversed(processes):
        if p and p.poll() is None:
            try:
                p.kill()
            except Exception:
                pass

    log("Runner", GREEN, "All services stopped. Goodbye!")
    sys.exit(0)


def main():
    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    print(f"{BOLD}===================================================={RESET}")
    print(f"{BOLD}      Drishti 2026 RAG Assistant — Full Stack       {RESET}")
    print(f"{BOLD}===================================================={RESET}\n")

    ensure_ollama()
    start_backend()
    start_frontend()

    print(f"\n{GREEN}{BOLD}✨ All services are up and running!{RESET}")
    print(f" • Kiosk Web UI:     {BOLD}http://localhost:{FRONTEND_PORT}{RESET}")
    print(f" • Backend API:      {BOLD}http://localhost:{BACKEND_PORT}{RESET}")
    print(f" • Static Posters:   {BOLD}http://localhost:{BACKEND_PORT}/posters/<image>{RESET}")
    print(f" • Ollama LLM:       {BOLD}{OLLAMA_HOST} ({MODEL_NAME}){RESET}")
    print(f"\n{YELLOW}Press Ctrl+C to stop all services.{RESET}\n")

    try:
        # Keep supervisor alive while children are running
        while True:
            for p in processes:
                if p.poll() is not None:
                    log("Runner", RED, f"Process {p.args} stopped unexpectedly (exit code {p.returncode}).")
                    shutdown()
            time.sleep(1.0)
    except KeyboardInterrupt:
        shutdown()


if __name__ == "__main__":
    main()
