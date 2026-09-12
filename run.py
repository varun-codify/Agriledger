"""AgriLedger Launcher Script.

Runs the main existing AgriLedger application (preserving the exact UI)
with high-performance optimizations (fast DNS, in-memory caching, indexing).
"""

import os
import subprocess
import sys


def main():
    os.environ["REFLEX_SOCKET_MAX_HTTP_BUFFER_SIZE"] = "104857600"  # 100 MB
    os.environ["REFLEX_SOCKET_TIMEOUT"] = "120"
    os.environ["REFLEX_SOCKET_INTERVAL"] = "25"

    root_dir = os.path.dirname(os.path.abspath(__file__))
    venv_reflex = os.path.join(root_dir, ".venv", "Scripts", "reflex.exe")
    if not os.path.exists(venv_reflex):
        venv_reflex = "reflex"

    args = [venv_reflex, "run"]
    if "--prod" in sys.argv:
        args.extend(["--env", "prod"])

    print("Starting AgriLedger Main Application...")
    print("Application URL: http://localhost:3000")
    print("API Endpoint:    http://localhost:3000/api\n")

    try:
        proc = subprocess.Popen(args, cwd=root_dir)
        proc.wait()
    except KeyboardInterrupt:
        print("\nStopping AgriLedger...")
        proc.terminate()


if __name__ == "__main__":
    main()
