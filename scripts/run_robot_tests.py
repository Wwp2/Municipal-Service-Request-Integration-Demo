import argparse
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"
DEFAULT_OUTPUT_DIR = ROOT_DIR / "reports" / "robot"


def wait_for_health(
    base_url: str,
    timeout_seconds: float,
    server_process: subprocess.Popen,
) -> None:
    health_url = f"{base_url}/health"
    deadline = time.monotonic() + timeout_seconds
    last_error: Exception | None = None

    while time.monotonic() < deadline:
        if server_process.poll() is not None:
            raise RuntimeError(
                "API server exited before becoming healthy: "
                f"{server_process.returncode}"
            )

        try:
            with urllib.request.urlopen(health_url, timeout=1) as response:
                if response.status == 200:
                    return
        except (OSError, urllib.error.URLError) as error:
            last_error = error

        time.sleep(0.25)

    raise RuntimeError(f"API did not become healthy at {health_url}: {last_error}")


def reset_integration_data(base_url: str) -> None:
    request = urllib.request.Request(
        f"{base_url}/api/v1/admin/integration-data",
        method="DELETE",
    )
    with urllib.request.urlopen(request, timeout=5):
        return


def build_environment(base_url: str) -> dict[str, str]:
    environment = os.environ.copy()
    existing_pythonpath = environment.get("PYTHONPATH")
    pythonpath_parts = [str(SRC_DIR)]

    if existing_pythonpath:
        pythonpath_parts.append(existing_pythonpath)

    environment["PYTHONPATH"] = os.pathsep.join(pythonpath_parts)
    environment["API_BASE_URL"] = base_url
    return environment


def start_server(host: str, port: int, environment: dict[str, str]) -> subprocess.Popen:
    command = [
        sys.executable,
        "-m",
        "uvicorn",
        "integration_demo.main:app",
        "--host",
        host,
        "--port",
        str(port),
        "--log-level",
        "warning",
    ]
    return subprocess.Popen(command, cwd=ROOT_DIR, env=environment)


def stop_server(server_process: subprocess.Popen) -> None:
    if server_process.poll() is not None:
        return

    server_process.terminate()

    try:
        server_process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        server_process.kill()
        server_process.wait(timeout=10)


def run_robot_tests(output_dir: Path, environment: dict[str, str]) -> int:
    output_dir.mkdir(parents=True, exist_ok=True)
    command = [
        sys.executable,
        "-m",
        "robot",
        "--outputdir",
        str(output_dir),
        "--variable",
        f"BASE_URL:{environment['API_BASE_URL']}",
        str(ROOT_DIR / "tests" / "robot"),
    ]
    return subprocess.run(command, cwd=ROOT_DIR, env=environment).returncode


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Start the API, run Robot Framework tests, and stop the API.",
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=8000, type=int)
    parser.add_argument("--startup-timeout", default=20.0, type=float)
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR, type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_arguments()
    base_url = f"http://{args.host}:{args.port}"
    environment = build_environment(base_url)
    server_process = start_server(args.host, args.port, environment)

    try:
        wait_for_health(base_url, args.startup_timeout, server_process)
        reset_integration_data(base_url)
        return run_robot_tests(args.output_dir, environment)
    finally:
        try:
            reset_integration_data(base_url)
        except Exception as error:
            print(
                f"Warning: failed to reset integration data: {error}",
                file=sys.stderr,
            )

        stop_server(server_process)


if __name__ == "__main__":
    raise SystemExit(main())
