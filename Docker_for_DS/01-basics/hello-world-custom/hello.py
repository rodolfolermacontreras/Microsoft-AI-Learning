"""
Hello World from Docker.

This script runs inside a Docker container. Notice:
- The Python version may differ from your host machine
- No libraries other than the stdlib are available (we did not install any)
- The working directory is /app (set in Dockerfile)
"""

import sys
import platform
import os


def main() -> None:
    """Print environment info from inside the container."""
    print("=" * 50)
    print("Hello from inside a Docker container!")
    print("=" * 50)
    print(f"Python version : {sys.version}")
    print(f"Platform       : {platform.system()} {platform.release()}")
    print(f"Working dir    : {os.getcwd()}")
    print(f"Files here     : {os.listdir('.')}")
    print("=" * 50)


if __name__ == "__main__":
    main()
