# Docker for Data Science

A hands-on learning repository for Data Scientists to understand, practice, and apply Docker in real data science workflows. Every section is self-contained and builds on the previous one.

---

## Why Docker Matters for Data Scientists

When you ship ML code to an engineering team, environments differ:
- Different OS (Linux vs Windows vs Mac)
- Different Python versions
- Different library versions (numpy 1.x vs 2.x, CUDA drivers, etc.)

Docker solves this by packaging your **code + runtime + dependencies** into a single portable image that runs identically everywhere.

---

## Learning Path

Work through the sections in order for a structured progression from beginner to production-ready.

```
Docker_for_DS/
|
|-- README.md                     # This file -- overview and index
|-- CHEATSHEET.md                 # All essential Docker commands at a glance
|
|-- 01-basics/                    # Core concepts, installation, 10 essential commands
|-- 02-python-environment/        # Dockerize a Python data science environment
|-- 03-jupyter/                   # Run Jupyter Lab inside Docker with volume mounting
|-- 04-ml-pipeline/               # Training and inference containers
|-- 05-multi-container/           # Docker Compose -- Jupyter + PostgreSQL + pgAdmin
|-- 06-production/                # FastAPI model serving, multi-stage builds
```

### Estimated Time Per Section

| Section | Topic | Time |
|---------|-------|------|
| 01-basics | Docker fundamentals, images, containers, core commands | 1-2 hours |
| 02-python-environment | Build first custom DS image | 1 hour |
| 03-jupyter | Jupyter Lab in Docker, volumes, port mapping | 1 hour |
| 04-ml-pipeline | Training + serving containers, data flow | 2 hours |
| 05-multi-container | Docker Compose, multi-service setups | 2 hours |
| 06-production | REST API serving, multi-stage builds | 2-3 hours |

---

## Prerequisites

### 1. Install Docker Desktop (Windows)

1. Download from: https://www.docker.com/products/docker-desktop/
2. Run the installer (requires WSL2 on Windows -- installer will prompt)
3. Verify installation:

```powershell
docker --version
docker compose version
```

Expected output:
```
Docker version 27.x.x, build xxxxxxx
Docker Compose version v2.x.x
```

4. Test with hello-world:

```powershell
docker run hello-world
```

### 2. Create a Docker Hub Account (optional but recommended)

Docker Hub is the public registry where images are stored and shared.
- Create a free account at: https://hub.docker.com/
- Login from terminal: `docker login`

### 3. Python Virtual Environment

This workspace uses the shared `.venv` at `C:\Training\Microsoft\Copilot\.venv`.
Docker is separate from this -- Docker containers have their OWN isolated Python environments.

---

## Key Concepts at a Glance

| Term | What It Is |
|------|-----------|
| **Image** | Read-only blueprint (recipe) for a container. Built from a Dockerfile. |
| **Container** | A running instance of an image. Isolated process with its own filesystem. |
| **Dockerfile** | Text file with instructions for building an image (like a recipe card). |
| **Docker Hub** | Public registry for storing and sharing images (like GitHub for images). |
| **Volume** | Persistent storage that survives container restarts. Mount local folders into containers. |
| **Port mapping** | Expose container ports to your host machine (e.g., `-p 8888:8888`). |
| **Docker Compose** | Tool for defining and running multi-container applications via YAML config. |
| **Layer** | Each Dockerfile instruction creates a cached layer. Efficient rebuilding. |

---

## Quick Start -- 5 Minutes to First Container

```powershell
# Pull and run a Python container interactively
docker run -it python:3.12-slim bash

# Inside the container:
python --version
pip install pandas
python -c "import pandas; print(pandas.__version__)"
exit

# List all containers (including stopped)
docker ps -a

# Remove stopped containers
docker container prune
```

---

## Navigating This Repo

Each section has:
- **README.md** -- Concepts explained + step-by-step instructions
- **Dockerfile** (or docker-compose.yml) -- Working example to build and run
- **Supporting files** -- Python scripts, requirements, data, config

Start from `01-basics/` if you are new to Docker. Jump to a later section if you have prior experience.

---

## Resources

- [Docker Official Documentation](https://docs.docker.com/)
- [Docker Hub](https://hub.docker.com/) -- Browse public images
- [Docker for Data Science (Article)](https://towardsdatascience.com/docker-for-data-science-projects)
- [Play with Docker](https://labs.play-with-docker.com/) -- Browser-based Docker playground (no install needed)
- [Dockerfile Best Practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
