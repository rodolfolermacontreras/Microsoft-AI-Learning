"""
Page 3 -- Guided hands-on exercises.

Each exercise maps to one of the 5 Docker_for_DS lab folders and walks the
learner step by step with:
  - What you will learn (learning objectives)
  - Prerequisites
  - Difficulty rating
  - Why this matters for data scientists
  - Step-by-step instructions with hints
  - Common mistakes to avoid
  - Self-check to confirm completion
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

from utils.docker_runner import is_docker_available, run_command, validate_command


st.set_page_config(page_title="Exercises | Docker for DS", layout="wide")
st.title("Guided Exercises")
st.markdown(
    "Hands-on labs that mirror what you would do as a data scientist "
    "entering the world of containers and production deployments. "
    "Each exercise builds on the previous one."
)

docker_live = is_docker_available()
if not docker_live:
    st.info(
        "Docker is not running. You can still read the instructions and "
        "use **simulation mode** for command output. "
        "Install Docker Desktop to run commands for real."
    )


EXERCISES: list[dict] = [
    {
        "title": "Lab 1 -- Hello Docker",
        "folder": "01-basics",
        "difficulty": "Beginner",
        "time": "10 min",
        "what_you_learn": [
            "How to write your first Dockerfile",
            "How to build an image from a Dockerfile",
            "How to run a container and see its output",
            "Build-Run-Done cycle that every Docker workflow follows",
        ],
        "prerequisites": [
            "Docker Desktop installed (or use simulation mode)",
            "A terminal / command prompt open",
        ],
        "why_ds": (
            "Even the simplest ML script benefits from being containerized. "
            "This lab teaches the exact 3-step workflow (write Dockerfile, build, run) "
            "that you will use for every project -- from a quick script to a full pipeline."
        ),
        "steps": [
            {
                "instruction": (
                    "Navigate to the project folder and look at the Dockerfile. "
                    "Notice how it uses `FROM`, `COPY`, and `CMD` -- these three instructions "
                    "are all you need for a basic image."
                ),
                "command": None,
                "hint": (
                    "`FROM` picks a base image (like choosing a conda env). "
                    "`COPY` puts your files in. `CMD` says what to run."
                ),
            },
            {
                "instruction": "Build the image and tag it `hello-docker:v1`.",
                "command": "docker build -t hello-docker:v1 .",
                "hint": "`-t` gives the image a name:tag. `.` means 'use the Dockerfile in the current directory'.",
            },
            {
                "instruction": "Run a container from your new image.",
                "command": "docker run --rm hello-docker:v1",
                "hint": "`--rm` deletes the container after it finishes so you don't leave clutter.",
            },
            {
                "instruction": "Verify the image appears in your local image list.",
                "command": "docker images",
                "hint": "Look for `hello-docker` with tag `v1` in the output.",
            },
        ],
        "common_mistakes": [
            "Forgetting the `.` at the end of `docker build` (it specifies where the Dockerfile is).",
            "Running `docker build` from the wrong directory -- make sure you `cd` to the folder first.",
        ],
        "self_check": [
            "You see 'Hello from Docker!' printed when running the container.",
            "`docker images` shows `hello-docker   v1` in the list.",
        ],
    },
    {
        "title": "Lab 2 -- Python Environment",
        "folder": "02-python-environment",
        "difficulty": "Beginner",
        "time": "15 min",
        "what_you_learn": [
            "How to install pip packages inside a Docker image",
            "How to structure a Python project for Docker",
            "How `.dockerignore` works (like .gitignore for Docker)",
            "How to keep images small with best practices",
        ],
        "prerequisites": [
            "Completed Lab 1 or comfortable with `docker build` + `docker run`",
        ],
        "why_ds": (
            "Every DS project has dependencies (pandas, scikit-learn, etc.). "
            "This lab shows you how to replicate your `requirements.txt` inside a container "
            "so it works identically on your laptop, your colleague's laptop, and a server."
        ),
        "steps": [
            {
                "instruction": (
                    "Examine the Dockerfile. Notice `RUN pip install -r requirements.txt` -- "
                    "this is the Docker equivalent of setting up a conda/venv environment."
                ),
                "command": None,
                "hint": "Each `RUN` instruction creates a layer in the image. Docker caches layers, so put things that change least at the top.",
            },
            {
                "instruction": "Look at `.dockerignore`. This tells Docker which files NOT to copy into the image.",
                "command": None,
                "hint": "Without `.dockerignore`, Docker copies everything -- including your data files, .git, __pycache__, etc.",
            },
            {
                "instruction": "Build the image.",
                "command": "docker build -t ds-env:v1 .",
                "hint": "Watch the output -- you will see pip installing packages. This is cached on subsequent builds.",
            },
            {
                "instruction": "Run the container and check the output.",
                "command": "docker run --rm ds-env:v1",
                "hint": "The script should show the versions of numpy, pandas, and scikit-learn.",
            },
            {
                "instruction": "Try modifying `explore_env.py` and rebuilding. Notice which layers are cached.",
                "command": "docker build -t ds-env:v2 .",
                "hint": "Only layers after the change are rebuilt. Since `requirements.txt` didn't change, pip install is cached!",
            },
        ],
        "common_mistakes": [
            "Editing `requirements.txt` and not rebuilding -- changes to dependencies require a rebuild.",
            "Not using `.dockerignore` -- results in huge images because data files get copied in.",
        ],
        "self_check": [
            "The container prints library versions matching `requirements.txt`.",
            "Rebuilding after editing only the Python script is fast (dependency layer is cached).",
        ],
    },
    {
        "title": "Lab 3 -- Jupyter in Docker",
        "folder": "03-jupyter",
        "difficulty": "Intermediate",
        "time": "20 min",
        "what_you_learn": [
            "How to expose a port from a container to your browser",
            "How to use Docker Compose for single-service setup",
            "How to mount local notebooks into the container",
            "How to access Jupyter Lab running in Docker",
        ],
        "prerequisites": [
            "Completed Lab 2 or comfortable with Dockerfiles and pip",
            "Understand what port mapping means (host_port:container_port)",
        ],
        "why_ds": (
            "Jupyter is the tool you live in. Running it in Docker means you can ship "
            "your entire notebook environment to anyone -- same Python, same packages, "
            "same extensions. No more 'it works on my machine' with notebooks."
        ),
        "steps": [
            {
                "instruction": (
                    "Examine `docker-compose.yml`. This file defines the Jupyter service, "
                    "the port mapping, the volume mount, and the build context."
                ),
                "command": None,
                "hint": "Compose files are YAML -- indentation matters. The `volumes:` section mounts your local notebooks folder.",
            },
            {
                "instruction": "Start the Jupyter service using Compose.",
                "command": "docker compose up -d",
                "hint": "`-d` runs in the background. Without it, logs print to your terminal.",
            },
            {
                "instruction": "Check that the service is running.",
                "command": "docker compose ps",
                "hint": "You should see one service with status 'running' and port 8888 mapped.",
            },
            {
                "instruction": "Check the logs to find the Jupyter token URL.",
                "command": "docker compose logs jupyter",
                "hint": "Look for a URL like `http://127.0.0.1:8888/lab?token=abc123`. Open it in your browser.",
            },
            {
                "instruction": "Open Jupyter in your browser and verify your notebooks are visible.",
                "command": None,
                "hint": "Any `.ipynb` files in your local notebooks folder should appear because of the volume mount.",
            },
            {
                "instruction": "Stop and clean up.",
                "command": "docker compose down",
                "hint": "This stops and removes the container but preserves your notebooks (they are on your host).",
            },
        ],
        "common_mistakes": [
            "Port conflict: another process is already using port 8888 -- change the host port in compose.",
            "Not checking logs for the token URL -- Jupyter requires a token on first access.",
        ],
        "self_check": [
            "Jupyter Lab opens in your browser at http://localhost:8888.",
            "You can create and save notebooks, and they persist on your host.",
        ],
    },
    {
        "title": "Lab 4 -- ML Pipeline (Train + Serve)",
        "folder": "04-ml-pipeline",
        "difficulty": "Intermediate",
        "time": "25 min",
        "what_you_learn": [
            "How to build separate containers for training and serving",
            "How to share model artifacts between containers using volumes",
            "The Train -> Save -> Serve pattern used in production ML",
            "How to hit a prediction endpoint from outside Docker",
        ],
        "prerequisites": [
            "Comfortable with `docker build`, `docker run`, and volume mounts",
        ],
        "why_ds": (
            "This is the real deal. In production, training and serving are separate processes -- "
            "often on different machines. This lab teaches the exact pattern used in ML platforms: "
            "train in one container, save the model to a volume, serve from another container."
        ),
        "steps": [
            {
                "instruction": (
                    "Look at the project structure: `train/` and `serve/` are separate apps, "
                    "each with their own Dockerfile and requirements."
                ),
                "command": None,
                "hint": "Separation of concerns: the training container has sklearn, the serving container has Flask.",
            },
            {
                "instruction": "Build the training image.",
                "command": "docker build -t ml-train:v1 train/",
                "hint": "Note we point to the `train/` directory -- Docker uses the Dockerfile inside it.",
            },
            {
                "instruction": (
                    "Run the training container with a volume to save the model. "
                    "The trained model file will appear in `./models/`."
                ),
                "command": "docker run --rm -v ${PWD}/models:/app/models ml-train:v1",
                "hint": "The volume `-v ${PWD}/models:/app/models` maps a local `models/` folder so the model file persists.",
            },
            {
                "instruction": "Build the serving image.",
                "command": "docker build -t ml-serve:v1 serve/",
                "hint": "This image contains a Flask API that loads and serves the model.",
            },
            {
                "instruction": "Run the serving container with the model mounted and port exposed.",
                "command": "docker run -d -p 5000:5000 -v ${PWD}/models:/app/models --name model-api ml-serve:v1",
                "hint": "`-p 5000:5000` exposes the Flask API. The same volume mount gives it access to the model.",
            },
            {
                "instruction": "Test the prediction endpoint.",
                "command": "docker exec model-api python -c \"import requests; print(requests.get('http://localhost:5000/predict').text)\"",
                "hint": "Or use curl/Postman to hit http://localhost:5000/predict from your host.",
            },
            {
                "instruction": "Clean up.",
                "command": "docker stop model-api && docker rm model-api",
                "hint": "Stop the serving container. The model file remains in `./models/` on your host.",
            },
        ],
        "common_mistakes": [
            "Forgetting the volume mount for the serve container -- it cannot find the model file.",
            "Running the serve container before training -- the model file does not exist yet.",
        ],
        "self_check": [
            "A model file (`.pkl`) exists in `./models/` after training.",
            "The `/predict` endpoint returns predictions from the trained model.",
        ],
    },
    {
        "title": "Lab 5 -- Multi-Container Stack",
        "folder": "05-multi-container",
        "difficulty": "Advanced",
        "time": "30 min",
        "what_you_learn": [
            "How to run multiple services (app + database) together",
            "How Docker networks let containers talk to each other",
            "How environment variables configure services",
            "The docker-compose.yml pattern for real projects",
        ],
        "prerequisites": [
            "Completed Labs 1-4",
            "Basic understanding of databases (SQL, connection strings)",
        ],
        "why_ds": (
            "Real-world DS projects rarely run alone -- you need a database for features, "
            "a cache for fast retrieval, maybe a dashboard. Compose lets you define all "
            "of these in one file and bring the whole stack up with a single command. "
            "This is how production environments are structured."
        ),
        "steps": [
            {
                "instruction": (
                    "Read `docker-compose.yml` carefully. Notice the two services, "
                    "the network they share, the environment variables, and the volumes."
                ),
                "command": None,
                "hint": "The services can reach each other by name (e.g., `db` as a hostname) because Compose creates a shared network.",
            },
            {
                "instruction": "Check the `.env.example` file. Copy it to `.env` and fill in values.",
                "command": None,
                "hint": "Environment variables keep secrets out of your compose file. Never hardcode passwords.",
            },
            {
                "instruction": "Start the full stack.",
                "command": "docker compose up -d",
                "hint": "`-d` runs everything in the background. Docker pulls any missing images automatically.",
            },
            {
                "instruction": "Verify all services are running.",
                "command": "docker compose ps",
                "hint": "Both services should show status 'running'. If one shows 'exited', check its logs.",
            },
            {
                "instruction": "Check the logs for any errors.",
                "command": "docker compose logs",
                "hint": "If the app cannot connect to the database, it might be starting too fast. Check the depends_on setting.",
            },
            {
                "instruction": "Test the running application.",
                "command": None,
                "hint": "Open the exposed port in your browser or use curl to test the API.",
            },
            {
                "instruction": "Stop the stack and clean up.",
                "command": "docker compose down",
                "hint": "Add `--volumes` to also remove database data. Without it, data persists for next time.",
            },
        ],
        "common_mistakes": [
            "Missing `.env` file -- the compose file references variables that don't exist.",
            "App starts before database is ready -- add health checks or retry logic.",
            "Port conflicts -- if another service uses the same port, change the host port in compose.",
        ],
        "self_check": [
            "`docker compose ps` shows all services running.",
            "The application can connect to the database and return data.",
            "Data persists after `docker compose down` (without `--volumes`).",
        ],
    },
]


# ---- UI ----

# Progress tracker
st.markdown("### Your progress")
progress_key = "exercise_progress"
if progress_key not in st.session_state:
    st.session_state[progress_key] = {ex["folder"]: False for ex in EXERCISES}

progress_count = sum(st.session_state[progress_key].values())
st.progress(progress_count / len(EXERCISES))
st.caption(f"{progress_count} of {len(EXERCISES)} labs completed")

st.markdown("---")

# Exercise selector
exercise_titles = [f"{ex['difficulty']} -- {ex['title']}" for ex in EXERCISES]
selected_idx = st.selectbox(
    "Select an exercise",
    range(len(EXERCISES)),
    format_func=lambda i: exercise_titles[i],
    key="exercise_select",
)
ex = EXERCISES[selected_idx]

# Header
st.header(ex["title"])
meta_cols = st.columns(3)
meta_cols[0].metric("Difficulty", ex["difficulty"])
meta_cols[1].metric("Time", ex["time"])
meta_cols[2].metric("Folder", ex["folder"])

# Why this matters
st.info(f"**Why this matters for data scientists:** {ex['why_ds']}")

# Learning objectives
with st.expander("What you will learn", expanded=True):
    for obj in ex["what_you_learn"]:
        st.markdown(f"- {obj}")

# Prerequisites
if ex.get("prerequisites"):
    with st.expander("Prerequisites"):
        for prereq in ex["prerequisites"]:
            st.markdown(f"- {prereq}")

st.markdown("---")

# Steps
st.subheader("Steps")
step_progress_key = f"steps_{ex['folder']}"
if step_progress_key not in st.session_state:
    st.session_state[step_progress_key] = [False] * len(ex["steps"])

for i, step in enumerate(ex["steps"]):
    step_num = i + 1
    done = st.session_state[step_progress_key][i]
    checked = st.checkbox(
        f"Step {step_num}",
        value=done,
        key=f"step_check_{ex['folder']}_{i}",
    )
    st.session_state[step_progress_key][i] = checked

    with st.container():
        st.markdown(f"**{step_num}.** {step['instruction']}")

        if step.get("command"):
            st.code(step["command"], language="bash")

            btn_cols = st.columns([0.15, 0.15, 0.2, 0.5])
            with btn_cols[0]:
                run_btn = st.button("Run", key=f"run_{ex['folder']}_{i}", type="primary")
            with btn_cols[1]:
                hint_btn = st.button("Hint", key=f"hint_{ex['folder']}_{i}")
            with btn_cols[2]:
                ask_btn = st.button("Ask AI", key=f"ask_{ex['folder']}_{i}")

            if run_btn:
                cmd = step["command"]
                is_valid, error = validate_command(cmd)
                if not is_valid:
                    st.error(f"Cannot run: {error}")
                else:
                    with st.spinner("Running..."):
                        result = run_command(cmd, simulate=(not docker_live))
                    if result.simulated:
                        st.caption("Simulated output")
                    st.text_area(
                        "Output",
                        value=result.output if result.output else "(no output)",
                        height=120,
                        key=f"output_{ex['folder']}_{i}",
                        disabled=True,
                    )

            if hint_btn:
                st.info(f"**Hint:** {step['hint']}")

            if ask_btn:
                prompt = (
                    f"I am on {ex['title']}, step {step_num}. "
                    f"The instruction says: '{step['instruction']}' "
                    f"The command is: `{step['command']}`. "
                    f"Explain what this does and help me understand it."
                )
                st.session_state["chat_prefill"] = prompt
                st.switch_page("pages/04_chat.py")
        else:
            hint_btn = st.button("Hint", key=f"hint_{ex['folder']}_{i}")
            if hint_btn:
                st.info(f"**Hint:** {step['hint']}")

        st.markdown("")

# Common mistakes
if ex.get("common_mistakes"):
    st.markdown("---")
    with st.expander("Common mistakes to avoid"):
        for mistake in ex["common_mistakes"]:
            st.markdown(f"- {mistake}")

# Self-check
if ex.get("self_check"):
    with st.expander("Self-check -- how to verify you completed this lab"):
        for check in ex["self_check"]:
            st.markdown(f"- {check}")

# Mark complete
st.markdown("---")
mark_done = st.checkbox(
    f"Mark **{ex['title']}** as completed",
    value=st.session_state[progress_key].get(ex["folder"], False),
    key=f"mark_done_{ex['folder']}",
)
st.session_state[progress_key][ex["folder"]] = mark_done
