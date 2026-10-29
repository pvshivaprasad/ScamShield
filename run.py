"""One-command launcher: python run.py [--port 8000] [--no-browser]"""
import argparse
import threading
import webbrowser
import uvicorn

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8000)
    ap.add_argument("--no-browser", action="store_true")
    a = ap.parse_args()
    if not a.no_browser:
        threading.Timer(1.5, lambda: webbrowser.open(f"http://{a.host}:{a.port}")).start()
    uvicorn.run("api:app", host=a.host, port=a.port, log_level="warning")
