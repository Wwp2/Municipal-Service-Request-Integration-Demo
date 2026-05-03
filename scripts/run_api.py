import argparse
import os
import sys
from pathlib import Path

import uvicorn


ROOT_DIR = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT_DIR / "src"


def add_src_to_pythonpath() -> None:
    src_path = str(SRC_DIR)

    if src_path not in sys.path:
        sys.path.insert(0, src_path)

    existing_pythonpath = os.environ.get("PYTHONPATH")

    if existing_pythonpath:
        os.environ["PYTHONPATH"] = os.pathsep.join([src_path, existing_pythonpath])
    else:
        os.environ["PYTHONPATH"] = src_path


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the Municipal Service Request Integration Demo API.",
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=8000, type=int)
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Restart the API automatically when source files change.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    add_src_to_pythonpath()

    base_url = f"http://{args.host}:{args.port}"
    print(f"API running at {base_url}")
    print(f"Interactive docs at {base_url}/docs")
    print(f"Health check at {base_url}/health")
    print("Press Ctrl+C to stop")

    uvicorn.run(
        "integration_demo.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
    )


if __name__ == "__main__":
    main()
