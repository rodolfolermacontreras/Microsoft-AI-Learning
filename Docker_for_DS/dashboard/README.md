# Docker Learning Dashboard

An interactive Streamlit dashboard for learning Docker dynamically — with an AI tutor, live command execution, concept visualizations, and guided exercises.

---

## Features

| Tab | What It Does |
|-----|-------------|
| **Docker Tutor** | Chat with an AI tutor specialized in Docker and data science workflows |
| **Command Playground** | Run Docker commands live and see real output in the browser |
| **Concept Explorer** | Interactive visual cards for every Docker concept |
| **Guided Exercises** | Step-by-step exercises with hints and AI-powered feedback |
| **System Status** | Live view of running containers, images, and disk usage |

---

## Setup

### 1. Install Dependencies

```powershell
cd C:\Training\Microsoft\Copilot
.\.venv\Scripts\Activate.ps1

pip install -r Docker_for_DS\dashboard\requirements.txt
```

### 2. Configure LLM Access

```powershell
Copy-Item Docker_for_DS\dashboard\.env.example Docker_for_DS\dashboard\.env
# Edit .env with your API key
```

**Supported LLM backends** (configure in `.env`):

| Backend | Environment Variable | Notes |
|---------|---------------------|-------|
| OpenAI | `OPENAI_API_KEY` | Recommended for best experience |
| Azure OpenAI | `AZURE_OPENAI_KEY` + `AZURE_OPENAI_ENDPOINT` | Enterprise |
| GitHub Copilot SDK | `COPILOT_SDK=true` | Requires Copilot CLI installed |
| Offline mode | (no key) | Concept cards + playground work, no chat |

### 3. Run the Dashboard

```powershell
cd C:\Training\Microsoft\Copilot
.\.venv\Scripts\Activate.ps1
streamlit run Docker_for_DS\dashboard\app.py
```

Opens at http://localhost:8501

---

## Run in Docker (Meta-Learning!)

Once you've learned enough Docker to appreciate the irony:

```powershell
cd Docker_for_DS\dashboard
docker compose up
# Dashboard at http://localhost:8501
```

---

## Architecture

```
dashboard/
|-- app.py                 # Main entry point, navigation, session state
|-- pages/
|   |-- tutor.py           # AI chat tutor page
|   |-- playground.py      # Live Docker command execution
|   |-- concepts.py        # Interactive concept visualizer
|   |-- exercises.py       # Guided exercises
|   |-- status.py          # Docker system status
|-- utils/
|   |-- docker_runner.py   # Safe subprocess wrapper for Docker commands
|   |-- llm_client.py      # Unified LLM client (OpenAI / Copilot SDK)
|   |-- concepts_data.py   # All Docker concept definitions
|   |-- exercises_data.py  # Exercise library
|-- .env.example           # Config template
|-- requirements.txt       # Python dependencies
|-- Dockerfile             # Containerized version of the dashboard
|-- docker-compose.yml     # Run dashboard in Docker
```
