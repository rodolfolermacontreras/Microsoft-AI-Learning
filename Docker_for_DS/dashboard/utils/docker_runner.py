"""
Safe Docker command runner.

Executes Docker CLI commands via subprocess and captures output.
Includes:
  - An allowlist of safe commands
  - Timeout enforcement
  - Structured output (stdout, stderr, exit code, duration)
  - A simulation mode that returns mock output without running real commands
"""

from __future__ import annotations

import os
import shlex
import subprocess
import time
from dataclasses import dataclass, field


# ---- Safety: these are the only top-level docker verbs allowed ----
ALLOWED_VERBS = {
    "ps", "images", "info", "version", "stats",
    "inspect", "logs", "top", "diff", "port",
    "run", "start", "stop", "rm", "rmi",
    "pull", "build", "tag", "push",
    "exec", "cp",
    "volume", "network", "system",
    "compose",
}

# Verbs that mutate system state -- warn user before running
MUTATING_VERBS = {"run", "start", "stop", "rm", "rmi", "pull", "build", "push", "exec"}

# Flags that are always blocked for safety
BLOCKED_FLAGS = {"--privileged", "--cap-add", "--pid=host", "--net=host"}

DEFAULT_TIMEOUT = 30  # seconds


@dataclass
class CommandResult:
    """Result of a Docker command execution."""
    command: str
    stdout: str
    stderr: str
    exit_code: int
    duration_ms: float
    simulated: bool = False
    error_message: str = ""

    @property
    def success(self) -> bool:
        return self.exit_code == 0

    @property
    def output(self) -> str:
        """Combined readable output."""
        parts = []
        if self.stdout.strip():
            parts.append(self.stdout.strip())
        if self.stderr.strip():
            parts.append(self.stderr.strip())
        return "\n".join(parts)


def is_docker_available() -> bool:
    """Check if Docker CLI is installed and the daemon is running."""
    try:
        result = subprocess.run(
            ["docker", "info"],
            capture_output=True,
            timeout=5,
            text=True,
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def _load_allow_real() -> bool:
    """Check if real Docker execution is allowed (from env)."""
    try:
        from dotenv import load_dotenv
        env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
        load_dotenv(env_path, override=False)
    except ImportError:
        pass
    return os.environ.get("ALLOW_REAL_DOCKER", "true").lower() != "false"


def validate_command(command: str) -> tuple[bool, str]:
    """
    Validate a Docker command for safety.

    Returns:
        (is_valid, error_message) -- error_message is "" if valid
    """
    command = command.strip()

    if not command:
        return False, "Empty command."

    # Must start with "docker"
    parts = shlex.split(command)
    if not parts:
        return False, "Empty command."

    if parts[0] != "docker":
        return False, "Command must start with 'docker'."

    if len(parts) < 2:
        return False, "Incomplete command. Example: docker ps"

    # Check verb allowlist
    verb = parts[1]
    if verb not in ALLOWED_VERBS:
        return False, (
            f"The verb '{verb}' is not in the allowed list for the playground.\n"
            f"Allowed: {', '.join(sorted(ALLOWED_VERBS))}"
        )

    # Check for blocked flags
    for flag in BLOCKED_FLAGS:
        if flag in parts:
            return False, f"Flag '{flag}' is blocked for safety."

    return True, ""


def run_command(
    command: str,
    timeout: int = DEFAULT_TIMEOUT,
    simulate: bool = False,
) -> CommandResult:
    """
    Execute a Docker command and return structured output.

    Args:
        command:  Full command string, e.g. "docker ps -a"
        timeout:  Max execution time in seconds
        simulate: If True, return simulation without calling Docker

    Returns:
        CommandResult with stdout, stderr, exit_code, duration
    """
    is_valid, error = validate_command(command)
    if not is_valid:
        return CommandResult(
            command=command,
            stdout="",
            stderr=error,
            exit_code=1,
            duration_ms=0,
            error_message=error,
        )

    allow_real = _load_allow_real()
    if simulate or not allow_real or not is_docker_available():
        return _simulate_command(command)

    parts = shlex.split(command)
    start = time.perf_counter()
    try:
        proc = subprocess.run(
            parts,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        duration = (time.perf_counter() - start) * 1000
        return CommandResult(
            command=command,
            stdout=proc.stdout,
            stderr=proc.stderr,
            exit_code=proc.returncode,
            duration_ms=round(duration, 1),
        )
    except subprocess.TimeoutExpired:
        return CommandResult(
            command=command,
            stdout="",
            stderr=f"Command timed out after {timeout}s.",
            exit_code=124,
            duration_ms=timeout * 1000,
            error_message=f"Timeout after {timeout}s",
        )
    except FileNotFoundError:
        return CommandResult(
            command=command,
            stdout="",
            stderr="Docker CLI not found. Is Docker Desktop installed?",
            exit_code=127,
            duration_ms=0,
            error_message="Docker not found",
        )


# ---- Simulation responses ----

_SIMULATIONS: dict[str, str] = {
    "docker ps": (
        "CONTAINER ID   IMAGE         COMMAND                  CREATED        STATUS         "
        "PORTS                    NAMES\n"
        "a1b2c3d4e5f6   nginx:latest  \"/docker-entrypoint.…\"   2 hours ago    Up 2 hours     "
        "0.0.0.0:8080->80/tcp     my-nginx\n"
        "b2c3d4e5f6a1   redis:alpine  \"docker-entrypoint.s…\"   5 hours ago    Up 5 hours     "
        "0.0.0.0:6379->6379/tcp   ds-redis"
    ),
    "docker ps -a": (
        "CONTAINER ID   IMAGE              COMMAND    CREATED        STATUS                      NAMES\n"
        "a1b2c3d4e5f6   nginx:latest       \"/docker…\"  2 hours ago    Up 2 hours                  my-nginx\n"
        "c3d4e5f6a1b2   python:3.12-slim   \"python\"   3 hours ago    Exited (0) 3 hours ago      ds-test\n"
        "d4e5f6a1b2c3   hello-world        \"/hello\"   1 day ago      Exited (0) 1 day ago        hello"
    ),
    "docker images": (
        "REPOSITORY          TAG         IMAGE ID       CREATED        SIZE\n"
        "python              3.12-slim   abc123def456   2 days ago     130MB\n"
        "jupyter/datascience-notebook   python-3.11   def456abc123   1 week ago     3.87GB\n"
        "nginx               latest      789ghi012jkl   2 weeks ago    187MB\n"
        "redis               alpine      012jkl345mno   3 weeks ago    42.4MB\n"
        "hello-world         latest      345mno678pqr   1 month ago    13.3kB"
    ),
    "docker version": (
        "Client:\n"
        " Cloud integration: v1.0.35+desktop.13\n"
        " Version:           27.0.3\n"
        " API version:       1.47\n"
        " Go version:        go1.21.11\n"
        " OS/Arch:           linux/amd64 (simulated)\n\n"
        "Server: Docker Engine - Community\n"
        " Engine:\n"
        "  Version:          27.0.3\n"
        "  API version:      1.47 (minimum version 1.24)\n"
    ),
    "docker system df": (
        "TYPE            TOTAL     ACTIVE    SIZE      RECLAIMABLE\n"
        "Images          8         3         4.21GB    2.87GB (68%)\n"
        "Containers      3         1         142MB     98MB (69%)\n"
        "Local Volumes   4         2         891MB     445MB (49%)\n"
        "Build Cache     12        0         234MB     234MB"
    ),
    "docker info": (
        "Client:\n"
        " Context:    default\n"
        " Debug Mode: false\n\n"
        "Server:\n"
        " Containers: 3\n"
        "  Running: 1\n"
        "  Paused: 0\n"
        "  Stopped: 2\n"
        " Images: 8\n"
        " Server Version: 27.0.3\n"
        " Storage Driver: overlay2\n"
        " Total Memory: 15.51GiB\n"
        " CPUs: 8\n"
    ),
}


def _simulate_command(command: str) -> CommandResult:
    """Return a simulated response for demo/offline use."""
    cmd_clean = " ".join(command.split())  # normalize whitespace

    # Look for exact match first
    if cmd_clean in _SIMULATIONS:
        return CommandResult(
            command=command,
            stdout=_SIMULATIONS[cmd_clean],
            stderr="",
            exit_code=0,
            duration_ms=42.0,
            simulated=True,
        )

    # Partial matches
    for key, output in _SIMULATIONS.items():
        if cmd_clean.startswith(key):
            return CommandResult(
                command=command,
                stdout=output,
                stderr="",
                exit_code=0,
                duration_ms=38.0,
                simulated=True,
            )

    # Generic simulation
    parts = cmd_clean.split()
    verb = parts[1] if len(parts) > 1 else "?"

    if verb in ("pull",):
        image = parts[2] if len(parts) > 2 else "image"
        stdout = (
            f"Using default tag: latest\n"
            f"latest: Pulling from library/{image.split(':')[0]}\n"
            f"Digest: sha256:abc123...\n"
            f"Status: Downloaded newer image for {image}\n"
            f"docker.io/library/{image}"
        )
        return CommandResult(command=command, stdout=stdout, stderr="", exit_code=0, duration_ms=1200.0, simulated=True)

    if verb in ("stop", "start", "rm"):
        target = parts[2] if len(parts) > 2 else "container"
        return CommandResult(command=command, stdout=target + "\n", stderr="", exit_code=0, duration_ms=150.0, simulated=True)

    if verb == "run":
        return CommandResult(
            command=command,
            stdout="[Container output would appear here in real execution]\n",
            stderr="",
            exit_code=0,
            duration_ms=800.0,
            simulated=True,
        )

    return CommandResult(
        command=command,
        stdout=f"[Simulation] Command '{cmd_clean}' executed successfully.\n",
        stderr="",
        exit_code=0,
        duration_ms=25.0,
        simulated=True,
    )
