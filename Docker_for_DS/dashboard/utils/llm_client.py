"""
LLM client -- multi-backend abstraction for the AI Docker tutor.

Supports:
  - openai     : OpenAI API (gpt-4o / gpt-4o-mini)
  - azure      : Azure OpenAI Service
  - copilot    : GitHub Copilot SDK chat endpoint
  - offline    : Pre-written answers when no API key is available

The chat() function is a generator that yields text chunks for streaming.
"""

from __future__ import annotations

import os
from typing import Generator

from dotenv import load_dotenv

load_dotenv(override=False)


# ---- System prompt ----
SYSTEM_PROMPT = """You are a friendly, patient Docker tutor helping a data scientist who is
transitioning into a developer / AI-engineer role. The learner is experienced
with Python, pandas, scikit-learn, Jupyter notebooks, and basic ML workflows,
but is brand new to Docker, containers, and DevOps.

Guidelines:
- ALWAYS explain concepts using analogies the learner already knows.
  For example compare a Dockerfile to requirements.txt, an image to a .pkl
  model file, a container to a loaded model in memory, volumes to data
  folders, base images to conda environments.
- Start simple, then build up complexity. Never assume prior Docker knowledge.
- When showing commands, explain every flag and option.
- When relevant, tie back to the data-science workflow: training, serving,
  notebook environments, data pipelines, experiment tracking.
- Use short paragraphs. Use bullet points. Use code blocks for commands.
- If the learner asks something outside Docker, gently redirect but still
  help if you can.
- Be encouraging. Learning Docker alongside ML is a big step.
"""


def _load_env(key: str) -> str | None:
    """Return an environment variable or None."""
    return os.environ.get(key)


def chat(
    messages: list[dict[str, str]],
    backend: str = "openai",
) -> Generator[str, None, None]:
    """Stream a chat response from the configured LLM backend.

    Parameters
    ----------
    messages:
        Conversation history in OpenAI format
        ``[{"role": "user"|"assistant", "content": "..."}]``.
    backend:
        One of ``"openai"``, ``"azure"``, ``"copilot"``, ``"offline"``.

    Yields
    ------
    str
        Text chunks suitable for incremental display.
    """
    dispatch = {
        "openai": _chat_openai,
        "azure": _chat_azure,
        "copilot": _chat_copilot,
        "offline": _chat_offline,
    }
    fn = dispatch.get(backend, _chat_offline)
    yield from fn(messages)


# ---- Backend implementations ----

def _chat_openai(messages: list[dict[str, str]]) -> Generator[str, None, None]:
    """OpenAI API (requires OPENAI_API_KEY)."""
    try:
        from openai import OpenAI
    except ImportError:
        yield "The `openai` package is not installed. Run `pip install openai`."
        return

    api_key = _load_env("OPENAI_API_KEY")
    if not api_key:
        yield "No `OPENAI_API_KEY` found in environment. Add it to `.env` or switch to offline mode."
        return

    client = OpenAI(api_key=api_key)
    model = _load_env("OPENAI_MODEL") or "gpt-4o-mini"

    full_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages

    stream = client.chat.completions.create(
        model=model,
        messages=full_messages,
        stream=True,
        temperature=0.7,
        max_tokens=2048,
    )

    for chunk in stream:
        delta = chunk.choices[0].delta
        if delta.content:
            yield delta.content


def _chat_azure(messages: list[dict[str, str]]) -> Generator[str, None, None]:
    """Azure OpenAI Service (requires AZURE_OPENAI_KEY + AZURE_OPENAI_ENDPOINT)."""
    try:
        from openai import AzureOpenAI
    except ImportError:
        yield "The `openai` package is not installed. Run `pip install openai`."
        return

    api_key = _load_env("AZURE_OPENAI_KEY")
    endpoint = _load_env("AZURE_OPENAI_ENDPOINT")
    deployment = _load_env("AZURE_OPENAI_DEPLOYMENT") or "gpt-4o-mini"
    api_version = _load_env("AZURE_OPENAI_API_VERSION") or "2024-06-01"

    if not api_key or not endpoint:
        yield (
            "Azure OpenAI requires `AZURE_OPENAI_KEY` and `AZURE_OPENAI_ENDPOINT` "
            "in your `.env` file. Switch to offline mode if you don't have these."
        )
        return

    client = AzureOpenAI(
        api_key=api_key,
        azure_endpoint=endpoint,
        api_version=api_version,
    )

    full_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages

    stream = client.chat.completions.create(
        model=deployment,
        messages=full_messages,
        stream=True,
        temperature=0.7,
        max_tokens=2048,
    )

    for chunk in stream:
        delta = chunk.choices[0].delta
        if delta.content:
            yield delta.content


def _chat_copilot(messages: list[dict[str, str]]) -> Generator[str, None, None]:
    """GitHub Copilot Chat via the Copilot SDK / tokens endpoint."""
    try:
        from openai import OpenAI
    except ImportError:
        yield "The `openai` package is not installed. Run `pip install openai`."
        return

    token = _load_env("COPILOT_TOKEN") or _load_env("GITHUB_TOKEN")
    if not token:
        yield (
            "No `COPILOT_TOKEN` or `GITHUB_TOKEN` found. "
            "Set one in `.env` or switch to a different backend."
        )
        return

    base_url = _load_env("COPILOT_BASE_URL") or "https://api.githubcopilot.com"
    model = _load_env("COPILOT_MODEL") or "gpt-4o"

    client = OpenAI(
        api_key=token,
        base_url=base_url,
    )

    full_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages

    stream = client.chat.completions.create(
        model=model,
        messages=full_messages,
        stream=True,
        temperature=0.7,
        max_tokens=2048,
    )

    for chunk in stream:
        delta = chunk.choices[0].delta
        if delta.content:
            yield delta.content


def _chat_offline(messages: list[dict[str, str]]) -> Generator[str, None, None]:
    """Offline fallback -- pattern-match common questions with pre-written answers."""
    if not messages:
        yield "I didn't receive a message. Try asking a question about Docker!"
        return

    last_message = messages[-1].get("content", "").lower()

    responses = {
        "what is docker": (
            "**Docker is a tool that packages your code + dependencies into a portable unit called a container.**\n\n"
            "Think of it this way:\n"
            "- You know how `requirements.txt` lists your Python packages?\n"
            "- A **Dockerfile** is like that, but for your *entire environment* -- OS, Python version, packages, files, everything.\n"
            "- When you `docker build`, it creates an **image** (like a `.pkl` model file -- a snapshot you can share).\n"
            "- When you `docker run`, it starts a **container** (like loading your model into memory -- it's alive and running).\n\n"
            "The magic: if it works in a container on your laptop, it will work *identically* on a server, "
            "a colleague's machine, or in the cloud."
        ),
        "difference between image and container": (
            "**Image = blueprint. Container = running instance.**\n\n"
            "DS analogy:\n"
            "- **Image** = a trained model saved as a `.pkl` file. It sits on disk, ready to use.\n"
            "- **Container** = that model loaded into memory and serving predictions. It's alive.\n\n"
            "You can create many containers from one image (like loading the same model in 5 different notebooks).\n"
            "Images are immutable -- once built, they don't change. Containers can be started, stopped, and deleted."
        ),
        "dockerfile": (
            "**A Dockerfile is a recipe for building a Docker image.**\n\n"
            "It's like `requirements.txt` + setup instructions combined:\n\n"
            "```dockerfile\n"
            "FROM python:3.12-slim          # Start from a Python environment\n"
            "WORKDIR /app                    # Set the working directory\n"
            "COPY requirements.txt .         # Copy your dependency list\n"
            "RUN pip install -r requirements.txt  # Install dependencies\n"
            "COPY . .                        # Copy your code\n"
            "CMD [\"python\", \"train.py\"]     # Default command to run\n"
            "```\n\n"
            "Each line creates a **layer**. Docker caches layers, so if you only change `train.py`, "
            "it won't reinstall your packages -- just like how changing one cell in a notebook "
            "doesn't re-run the whole thing."
        ),
        "volume": (
            "**Volumes let containers access files from your host machine.**\n\n"
            "Without a volume, a container's files disappear when it stops (like losing unsaved notebook changes).\n\n"
            "Use `-v` to mount a folder:\n"
            "```bash\n"
            "docker run -v ./data:/app/data my-image\n"
            "```\n\n"
            "This maps your local `data/` folder to `/app/data` inside the container. "
            "Changes from either side are visible in real-time. "
            "Perfect for training data, model outputs, and notebooks."
        ),
        "compose": (
            "**Docker Compose lets you run multiple services with one command.**\n\n"
            "Instead of running separate `docker run` commands for your app, database, and Jupyter, "
            "you define them all in `docker-compose.yml`:\n\n"
            "```yaml\n"
            "services:\n"
            "  jupyter:\n"
            "    build: .\n"
            "    ports: ['8888:8888']\n"
            "  db:\n"
            "    image: postgres:16\n"
            "```\n\n"
            "Then `docker compose up -d` starts everything. "
            "Services can talk to each other by name (e.g., connect to `db` from Jupyter)."
        ),
    }

    # Find the best matching pre-written response
    for keyword, response in responses.items():
        if keyword in last_message:
            yield response
            return

    # Generic fallback
    yield (
        "I'm running in **offline mode** so I can only answer a few pre-written questions.\n\n"
        "Try asking about:\n"
        "- What is Docker?\n"
        "- Difference between image and container\n"
        "- What is a Dockerfile?\n"
        "- What are volumes?\n"
        "- What is Docker Compose?\n\n"
        "For full AI-powered answers, add your API key to `.env` and switch to the `openai` backend."
    )
