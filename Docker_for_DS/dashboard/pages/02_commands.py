"""
Page 2 -- Docker Commands reference + sandbox.

Every command includes:
  - A plain-English explanation for beginners
  - What each flag does
  - A 'When you would use this' DS scenario
  - A live sandbox to try commands (real or simulated)
"""

from __future__ import annotations

import os
import sys

import streamlit as st
from dotenv import load_dotenv

_HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

load_dotenv(os.path.join(_HERE, ".env"), override=False)

from utils.docker_runner import (
    ALLOWED_VERBS,
    MUTATING_VERBS,
    CommandResult,
    is_docker_available,
    run_command,
    validate_command,
)


st.set_page_config(page_title="Commands | Docker for DS", layout="wide")
st.title("Docker Commands")
st.markdown(
    "A practical reference for every Docker command you will encounter in the labs. "
    "Each command is explained in plain English with a data-science scenario."
)

docker_live = is_docker_available()
if docker_live:
    st.success("Docker daemon is running -- commands will execute for real.")
else:
    st.warning(
        "Docker daemon not detected. Commands will run in **simulation mode** "
        "so you can explore the output without Docker installed. "
        "Install Docker Desktop to run commands for real."
    )


# ---- Command reference data ----
# Each entry: (command, plain_english, ds_scenario, flag_breakdown)
COMMAND_GROUPS = {
    "Getting Started (Images)": {
        "description": (
            "Images are the starting point for everything in Docker. "
            "Think of them like pre-built conda environments that you download and use."
        ),
        "commands": [
            {
                "cmd": "docker images",
                "plain": "Show all Docker images stored on your computer.",
                "scenario": "You want to see what you have available before running anything.",
                "flags": None,
            },
            {
                "cmd": "docker pull python:3.12-slim",
                "plain": "Download the Python 3.12 slim image from Docker Hub to your computer.",
                "scenario": "You need a Python environment and want to start from an official image.",
                "flags": "`python:3.12-slim` = image name + tag. Tags are like versions -- `slim` means a smaller image without optional extras.",
            },
            {
                "cmd": "docker build -t my-ds-project:v1 .",
                "plain": "Read the Dockerfile in the current directory and build a new image from it.",
                "scenario": "You wrote a Dockerfile for your ML project and want to create the image.",
                "flags": "`-t my-ds-project:v1` = name and tag the image. `.` = look for Dockerfile in the current directory.",
            },
            {
                "cmd": "docker rmi python:3.12-slim",
                "plain": "Delete an image from your computer to free up disk space.",
                "scenario": "You are done with an old image and want to reclaim disk space.",
                "flags": "`rmi` = remove image. You cannot remove an image if a container is using it.",
            },
            {
                "cmd": "docker tag my-app:latest my-app:v2.0",
                "plain": "Create a new tag (alias) for an existing image.",
                "scenario": "You want to version your image before pushing to a registry.",
                "flags": "Does not copy the image -- it just adds another name pointing to the same layers.",
            },
            {
                "cmd": "docker history python:3.12-slim",
                "plain": "Show every layer that makes up this image and how big each one is.",
                "scenario": "Your image is unexpectedly large and you want to find which step adds the most size.",
                "flags": "Each line is one Dockerfile instruction, showing the command that ran and the size added.",
            },
        ],
    },
    "Running Containers": {
        "description": (
            "Containers are running instances of images. "
            "This is where your code actually executes."
        ),
        "commands": [
            {
                "cmd": "docker run python:3.12-slim python --version",
                "plain": "Create a new container from the Python image, run `python --version`, then stop.",
                "scenario": "Quick check: is the Python version in this image what you expect?",
                "flags": "Everything after the image name (`python --version`) is the command to run inside the container.",
            },
            {
                "cmd": "docker run --rm python:3.12-slim python -c \"print('hello')\"",
                "plain": "Run a one-off Python command and auto-delete the container when done.",
                "scenario": "Test a quick Python snippet without leaving zombie containers behind.",
                "flags": "`--rm` = automatically remove the container when it exits. Great for throwaway runs.",
            },
            {
                "cmd": "docker run -it python:3.12-slim bash",
                "plain": "Start an interactive terminal (bash shell) inside a Python container.",
                "scenario": "Explore what is inside the image -- check installed packages, poke around.",
                "flags": "`-i` = keep stdin open (interactive). `-t` = allocate a pseudo-terminal. Together they give you a shell.",
            },
            {
                "cmd": "docker run -d -p 8888:8888 --name jupyter my-jupyter-image",
                "plain": "Start a container in the background with port 8888 exposed and name it 'jupyter'.",
                "scenario": "Launch Jupyter Lab and access it from your browser at http://localhost:8888.",
                "flags": (
                    "`-d` = detached (background). `-p 8888:8888` = map host port to container port. "
                    "`--name jupyter` = give it a human-readable name instead of a random id."
                ),
            },
            {
                "cmd": "docker run -v ${PWD}/data:/app/data my-image",
                "plain": "Run a container with your local `data/` folder mounted inside it.",
                "scenario": "Your training script needs to read a CSV from your local `data/` folder.",
                "flags": "`-v host:container` = volume mount. `${PWD}` = current directory (PowerShell). Files are shared in real-time.",
            },
        ],
    },
    "Managing Containers": {
        "description": (
            "Once containers are running, these commands let you inspect, stop, and clean up."
        ),
        "commands": [
            {
                "cmd": "docker ps",
                "plain": "List all currently running containers.",
                "scenario": "Check what is running right now -- is your Jupyter container up?",
                "flags": "Shows container ID, image, status, ports, and name.",
            },
            {
                "cmd": "docker ps -a",
                "plain": "List ALL containers, including stopped ones.",
                "scenario": "Find containers you forgot to clean up.",
                "flags": "`-a` = all. Without it, only running containers are shown.",
            },
            {
                "cmd": "docker logs jupyter",
                "plain": "Show the stdout/stderr output from a container.",
                "scenario": "Your Jupyter container started but you cannot access it -- check the logs for the token URL.",
                "flags": "Use `docker logs -f jupyter` to follow logs in real-time (like `tail -f`).",
            },
            {
                "cmd": "docker exec -it jupyter bash",
                "plain": "Open a shell inside a running container.",
                "scenario": "Jupyter is running but you need to pip install a package or check a file.",
                "flags": "`exec` runs a command inside an *already running* container (unlike `run` which creates a new one).",
            },
            {
                "cmd": "docker stop jupyter",
                "plain": "Gracefully stop a running container.",
                "scenario": "You are done with Jupyter for today.",
                "flags": "Sends SIGTERM, waits 10 seconds, then SIGKILL. The container still exists but is stopped.",
            },
            {
                "cmd": "docker rm jupyter",
                "plain": "Delete a stopped container.",
                "scenario": "Clean up after stopping a container.",
                "flags": "Does NOT delete the image -- just the container instance.",
            },
            {
                "cmd": "docker stats",
                "plain": "Show live CPU, memory, and network usage for all running containers.",
                "scenario": "Your training container is running and you want to see if it is using all the CPU.",
                "flags": "Press Ctrl+C to exit. Shows real-time metrics like `top` or `htop`.",
            },
        ],
    },
    "Volumes and Data": {
        "description": (
            "Volumes are how you persist data and share files between your host and containers."
        ),
        "commands": [
            {
                "cmd": "docker volume ls",
                "plain": "List all named volumes managed by Docker.",
                "scenario": "See what persistent storage Docker is managing on your system.",
                "flags": None,
            },
            {
                "cmd": "docker volume create model-data",
                "plain": "Create a named volume that persists even after containers are removed.",
                "scenario": "You want a dedicated place for trained model artifacts.",
                "flags": "Named volumes are stored internally by Docker -- use `inspect` to find the path.",
            },
            {
                "cmd": "docker volume inspect model-data",
                "plain": "Show details about a volume (driver, mount path, labels).",
                "scenario": "Find the actual path on your host where Docker stores the volume data.",
                "flags": None,
            },
            {
                "cmd": "docker volume rm model-data",
                "plain": "Delete a named volume and all data in it.",
                "scenario": "Clean up old model artifacts you no longer need.",
                "flags": "This permanently deletes the data. Make sure you have a backup if needed.",
            },
        ],
    },
    "Docker Compose": {
        "description": (
            "Compose commands manage multi-container stacks defined in a `docker-compose.yml` file."
        ),
        "commands": [
            {
                "cmd": "docker compose up -d",
                "plain": "Start all services defined in your docker-compose.yml in the background.",
                "scenario": "Boot up your full DS stack (Jupyter + Postgres + pgAdmin) with one command.",
                "flags": "`-d` = detached. Without it, all logs print to your terminal and Ctrl+C stops everything.",
            },
            {
                "cmd": "docker compose down",
                "plain": "Stop and remove all containers, networks created by the compose file.",
                "scenario": "Shut down the whole stack at the end of the day.",
                "flags": "Does NOT remove named volumes by default -- your data is safe. Add `--volumes` to also delete volumes.",
            },
            {
                "cmd": "docker compose ps",
                "plain": "Show the status of all services in the compose stack.",
                "scenario": "Check which services are running and which ones failed.",
                "flags": None,
            },
            {
                "cmd": "docker compose logs -f jupyter",
                "plain": "Follow the logs from the jupyter service in real-time.",
                "scenario": "Jupyter is not loading -- check its logs for errors.",
                "flags": "`-f` = follow. Omit the service name to see logs from all services.",
            },
            {
                "cmd": "docker compose build",
                "plain": "Build (or rebuild) images for services that use a Dockerfile.",
                "scenario": "You changed your Dockerfile and need to rebuild before restarting.",
                "flags": None,
            },
        ],
    },
    "System and Cleanup": {
        "description": (
            "Docker can accumulate unused images, containers, and volumes on disk. "
            "These commands help you monitor and clean up."
        ),
        "commands": [
            {
                "cmd": "docker system df",
                "plain": "Show disk space used by images, containers, volumes, and build cache.",
                "scenario": "Your disk is filling up and you suspect Docker is the cause.",
                "flags": "Think of it as `df -h` but for Docker specifically.",
            },
            {
                "cmd": "docker system prune",
                "plain": "Delete ALL stopped containers, unused networks, dangling images, and build cache.",
                "scenario": "Free up disk space after weeks of experimentation.",
                "flags": "Add `-a` to also remove images not used by any container (more aggressive). Add `--volumes` to also remove unused volumes.",
            },
            {
                "cmd": "docker version",
                "plain": "Show Docker client and daemon version information.",
                "scenario": "Verify Docker is installed and check which version you have.",
                "flags": None,
            },
            {
                "cmd": "docker info",
                "plain": "Detailed information about the Docker daemon (containers, images, storage driver, CPUs).",
                "scenario": "Debug whether Docker is running and see system configuration.",
                "flags": None,
            },
        ],
    },
}


# ---- Tabs: Reference | Sandbox | Cheat Sheet ----
tab_ref, tab_sandbox, tab_cheatsheet = st.tabs(["Command Reference", "Sandbox", "Cheat Sheet"])


with tab_ref:
    category = st.selectbox(
        "Category",
        list(COMMAND_GROUPS.keys()),
        key="cmd_cat",
    )
    group = COMMAND_GROUPS[category]
    st.markdown(f"_{group['description']}_")
    st.markdown("---")

    for entry in group["commands"]:
        with st.expander(f"`{entry['cmd']}`", expanded=False):
            st.markdown(f"**In plain English:** {entry['plain']}")
            st.markdown(f"**When you would use this:** _{entry['scenario']}_")
            if entry.get("flags"):
                st.markdown(f"**Flags explained:** {entry['flags']}")
            st.code(entry["cmd"], language="bash")

            col_try, col_ask = st.columns(2)
            with col_try:
                safe_key = entry["cmd"].replace(" ", "_").replace("/", "_").replace(".", "_").replace("$", "D").replace("{", "").replace("}", "").replace("\"", "")[:50]
                if st.button("Try in sandbox", key=f"try_{safe_key}"):
                    runnable = (
                        entry["cmd"]
                        .replace("<name>", "my-container")
                        .replace("<image>", "python:3.12-slim")
                        .replace("${PWD}", ".")
                        .replace("$(pwd)", ".")
                    )
                    st.session_state["sandbox_prefill"] = runnable
                    st.rerun()
            with col_ask:
                if st.button("Ask AI to explain", key=f"ask_{safe_key}"):
                    prompt = (
                        f"Explain this Docker command to a data scientist who is new to Docker:\n\n"
                        f"```\n{entry['cmd']}\n```\n\n"
                        f"Break down every flag and option. Give a practical example."
                    )
                    st.session_state["chat_prefill"] = prompt
                    st.switch_page("pages/04_chat.py")


with tab_sandbox:
    st.markdown("### Docker command sandbox")
    st.markdown(
        "Type any Docker command below and run it. The dashboard validates commands "
        "for safety before execution. If Docker is not running, output is simulated.\n\n"
        "**Safe to experiment** -- the sandbox blocks dangerous flags like `--privileged`."
    )

    prefill = st.session_state.pop("sandbox_prefill", "docker ps")
    command_input = st.text_input(
        "Command",
        value=prefill,
        placeholder="docker ps -a",
        key="sandbox_cmd",
    )

    col_run, col_validate, col_explain = st.columns([0.15, 0.2, 0.65])
    with col_run:
        run_pressed = st.button("Run", type="primary")
    with col_validate:
        validate_pressed = st.button("Validate only")
    with col_explain:
        explain_pressed = st.button("Ask AI what this does")

    if validate_pressed and command_input:
        is_valid, error = validate_command(command_input.strip())
        if is_valid:
            verb = command_input.strip().split()[1] if len(command_input.strip().split()) > 1 else ""
            if verb in MUTATING_VERBS:
                st.warning(
                    f"Valid command -- but `{verb}` modifies your system. "
                    f"It will create, stop, or delete resources when run."
                )
            else:
                st.success("Command is valid and safe (read-only).")
        else:
            st.error(f"Validation failed: {error}")

    if run_pressed and command_input:
        cmd = command_input.strip()
        is_valid, error = validate_command(cmd)
        if not is_valid:
            st.error(f"Blocked: {error}")
        else:
            with st.spinner("Running..."):
                result = run_command(cmd, simulate=(not docker_live))

            if result.simulated:
                st.info("Simulated output -- Docker is not running. Install Docker Desktop for live execution.")

            st.text_area(
                "Output",
                value=result.output if result.output else "(no output)",
                height=200,
                key="sandbox_output",
                disabled=True,
            )

            meta_cols = st.columns(3)
            meta_cols[0].metric("Exit code", result.exit_code)
            meta_cols[1].metric("Duration", f"{result.duration_ms:.0f} ms")
            meta_cols[2].metric("Mode", "Live" if not result.simulated else "Simulated")

            if not result.success:
                st.error(
                    "Command returned a non-zero exit code. "
                    "Check the output for error details, or ask the AI Tutor for help."
                )

    if explain_pressed and command_input:
        prompt = (
            f"I am a data scientist new to Docker. Explain this command to me step by step:\n\n"
            f"```\n{command_input}\n```\n\n"
            f"Break down every part, explain what each flag does, and tell me what to expect."
        )
        st.session_state["chat_prefill"] = prompt
        st.switch_page("pages/04_chat.py")


with tab_cheatsheet:
    st.markdown("### One-page cheat sheet")
    st.markdown(
        "The 10 commands you will use most often, in the order you will learn them."
    )

    cheatsheet = [
        ("docker pull python:3.12-slim", "Download an image", "Like `pip install`"),
        ("docker build -t myapp .", "Build image from Dockerfile", "Like saving a trained model"),
        ("docker run --rm myapp", "Run and auto-clean", "Like `python script.py`"),
        ("docker run -d -p 8888:8888 myapp", "Run in background with port", "Like starting Jupyter"),
        ("docker run -v ./data:/app/data myapp", "Run with data mounted", "Like mounting a drive"),
        ("docker ps", "List running containers", "Like `ps aux | grep python`"),
        ("docker logs my-container", "See container output", "Like checking print() statements"),
        ("docker stop my-container", "Stop a container", "Like Ctrl+C"),
        ("docker compose up -d", "Start multi-service stack", "Like running a Makefile"),
        ("docker compose down", "Stop multi-service stack", "Like cleaning up"),
    ]

    col_cmd, col_what, col_ds = st.columns([0.4, 0.3, 0.3])
    with col_cmd:
        st.markdown("**Command**")
    with col_what:
        st.markdown("**What it does**")
    with col_ds:
        st.markdown("**DS analogy**")

    for cmd, what, ds in cheatsheet:
        col_cmd, col_what, col_ds = st.columns([0.4, 0.3, 0.3])
        with col_cmd:
            st.code(cmd, language="bash")
        with col_what:
            st.markdown(what)
        with col_ds:
            st.markdown(f"_{ds}_")
