import os
import shutil
import sys
from pathlib import Path

from agentwatch.consts import AGENTWATCH_INTERNAL

sys.path.insert(0, str(Path(__file__).parent.parent))
os.environ[AGENTWATCH_INTERNAL] = "1"

import argparse
import asyncio
import logging
import subprocess
import webbrowser
from pathlib import Path
from typing import Any

from agentwatch.visualization.app import run_fastapi
from agentwatch.visualization.consts import VISUALIZATION_SERVER_PORT

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

async def run_server() -> None:
    try:
        tasks = [run_fastapi("agentwatch.visualization.server:app")]
        await asyncio.sleep(1.0)
        webbrowser.open_new_tab(f"http://localhost:{VISUALIZATION_SERVER_PORT}/ui")
        await asyncio.gather(*tasks)
    except Exception:
        pass

def run_ui(args: argparse.Namespace) -> None:
    dist_folder = Path(__file__).parent / "visualization" / "frontend" / "dist"
    if args.rebuild:
        if dist_folder.exists():
            shutil.rmtree(str(dist_folder))

    if not dist_folder.exists():
        print("Building UI for the first time...")
        try:
            extra_args: dict[str, Any] = {"capture_output": True}
            if os.name == "nt":
                extra_args["shell"] = True
                extra_args["check"] = True

            subprocess.run(["npm", "i"], cwd=Path(__file__).parent / "visualization" / "frontend", **extra_args)
            subprocess.run(["npm", "run", "build"], cwd=Path(__file__).parent / "visualization" / "frontend", **extra_args)
        except FileNotFoundError:
            print("NPM not found. Please install Node.js and NPM.")
            return
        except Exception as e:
            print(f"Error: {e}")
            return

    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        pass
    
def main() -> None:
    parser = argparse.ArgumentParser(prog="agentwatch", description="agentwatch - a platform agnostic agentic ai observability framework")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # UI Command
    ui_parser = subparsers.add_parser("ui", help="Launch (and build, if necessary) the agentwatch")
    ui_parser.add_argument('-r', '--rebuild', action='store_true', help='Rebuilds the UI')

    ui_parser.set_defaults(func=run_ui)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":  # pragma: no cover
    main()
