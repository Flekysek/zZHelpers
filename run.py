from __future__ import annotations

import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path


def _project_root() -> Path:
    return Path(__file__).resolve().parent


def _venv_python(root: Path) -> Path | None:
    if sys.platform == "win32":
        p = root / ".venv" / "Scripts" / "python.exe"
    else:
        p = root / ".venv" / "bin" / "python"
    return p if p.is_file() else None


def _python_exe(root: Path) -> Path:
    v = _venv_python(root)
    return v if v else Path(sys.executable)


def _wait_api(base: str = "http://127.0.0.1:5000", timeout_s: float = 15.0) -> None:
    url = base.rstrip("/") + "/api/health"
    deadline = time.monotonic() + timeout_s
    last_err: Exception | None = None
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=1.0) as r:
                if r.status == 200 and (r.read() or b"").strip().lower() == b"ok":
                    return
        except (urllib.error.URLError, OSError, TimeoutError) as e:
            last_err = e
        time.sleep(0.2)
    msg = f"API se nepodařilo nastartovat včas: {url}"
    if last_err:
        msg += f" ({last_err})"
    raise RuntimeError(msg)


def main() -> None:
    root = _project_root()
    py = _python_exe(root)
    env = os.environ.copy()

    flask_cmd = [str(py), str(root / "apps" / "flask_app.py")]
    streamlit_cmd = [
        str(py),
        "-m",
        "streamlit",
        "run",
        str(root / "apps" / "streamlit_app.py"),
        "--server.address",
        "127.0.0.1",
        "--server.port",
        "8501",
        "--server.headless",
        "true",
        "--browser.gatherUsageStats",
        "false",
    ]

    print(f"Spouštím API: {flask_cmd[1]}")
    flask_proc = subprocess.Popen(flask_cmd, cwd=str(root), env=env)
    try:
        _wait_api()
        print("API OK (http://127.0.0.1:5000). Spouštím Streamlit (http://127.0.0.1:8501) …")
        subprocess.run(streamlit_cmd, cwd=str(root), env=env, check=False)
    except KeyboardInterrupt:
        pass
    finally:
        flask_proc.terminate()
        try:
            flask_proc.wait(timeout=8)
        except subprocess.TimeoutExpired:
            flask_proc.kill()
            flask_proc.wait(timeout=5)


if __name__ == "__main__":
    main()
