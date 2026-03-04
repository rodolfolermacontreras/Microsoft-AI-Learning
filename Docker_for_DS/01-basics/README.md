# 01 - Docker Basics

Core concepts and essential commands. This section gets you from zero to confidently running containers.

---

## 1. Core Concepts

### Docker vs Container vs Image

These three terms are often confused. Here is the distinction:

```
Dockerfile          -->  Image              -->  Container
(recipe / blueprint)     (snapshot / class)      (running instance / object)

Like:
Python class file   -->  Your class def    -->  An object (instance)
```

**Dockerfile:** A plain text file with build instructions. Like a recipe.

**Image:** The built artifact from `docker build`. Read-only, immutable. Like a class definition. You can have one image and run many containers from it.

**Container:** A running (or stopped) instance of an image. Has its own isolated filesystem, process space, and network. Ephemeral by default -- when removed, all changes inside are gone (unless you use volumes).

**Registry:** Where images are stored and shared. Docker Hub is the default public registry. You can also use private registries (Azure Container Registry, GitHub Container Registry).

---

### How Docker Works

```
You write:          Dockerfile
You run:            docker build -t my-image .
Docker creates:     Image (stored locally)

You run:            docker run my-image
Docker creates:     Container (isolated process)
```

### Layers and Caching

Each `RUN`, `COPY`, `ADD` instruction in a Dockerfile creates a **layer**. Layers are cached. When you rebuild, Docker only re-runs instructions where something changed (and everything after that).

```
Layer 4: COPY . .            <-- code changed, rebuild from here
Layer 3: RUN pip install ... <-- cached (requirements.txt unchanged)
Layer 2: COPY requirements.txt . <-- cached
Layer 1: FROM python:3.12-slim   <-- cached
```

This is why you put stable things (base image, system deps) near the top, and frequently-changing things (your code) near the bottom.

---

## 2. Installation Verification

```powershell
# Check Docker version
docker --version

# Check Docker Compose version
docker compose version

# Verify Docker daemon is running
docker info

# Run the official hello-world test
docker run hello-world
```

Expected output from `hello-world`:
```
Hello from Docker!
This message shows that your installation appears to be working correctly.
```

---

## 3. The 10 Essential Commands

Work through each one to build muscle memory.

### Command 1: docker run

Create and start a container from an image.

```powershell
# Basic syntax
docker run IMAGE

# Example: run Ubuntu and list files
docker run ubuntu ls

# Run interactively with a shell
docker run -it ubuntu bash

# Run and auto-remove when done
docker run --rm ubuntu echo "hello from container"

# Run in background (detached)
docker run -d --name my-nginx nginx

# Run with port mapping (host:container)
docker run -d -p 8080:80 nginx
# Then visit http://localhost:8080
```

### Command 2: docker ps

List containers.

```powershell
# List only running containers
docker ps

# List ALL containers (running + stopped)
docker ps -a

# Show only container IDs
docker ps -q
```

### Command 3: docker stop

Gracefully stop a running container (sends SIGTERM, waits, then SIGKILL).

```powershell
# Stop by name
docker stop my-nginx

# Stop by container ID (get from docker ps)
docker stop a1b2c3d4

# Stop multiple at once
docker stop container1 container2

# Force-kill immediately (no graceful shutdown)
docker kill my-nginx
```

### Command 4: docker rm

Remove stopped containers.

```powershell
# Remove one stopped container
docker rm my-nginx

# Remove a running container (force)
docker rm -f my-nginx

# Remove ALL stopped containers
docker container prune

# Stop and remove in one step
docker stop my-nginx && docker rm my-nginx
```

### Command 5: docker images

List downloaded images.

```powershell
# List all local images
docker images

# List by name
docker images python

# Show image IDs only
docker images -q
```

### Command 6: docker pull

Download an image from a registry without running it.

```powershell
# Pull latest
docker pull python

# Pull specific version (always use specific tags in production)
docker pull python:3.12-slim

# Pull from a specific registry
docker pull mcr.microsoft.com/azureml/base:latest
```

### Command 7: docker build

Build an image from a Dockerfile.

```powershell
# Build from Dockerfile in current directory
# -t = tag (name:version)
docker build -t my-image:v1 .

# Build from specific Dockerfile
docker build -t my-image:v1 -f path/to/Dockerfile .

# Build without cache (clean build)
docker build --no-cache -t my-image:v1 .

# See build output verbosely
docker build --progress=plain -t my-image:v1 .
```

### Command 8: docker exec

Run a command inside an ALREADY RUNNING container.

```powershell
# Open an interactive shell inside running container
docker exec -it my-container bash

# Run a single command
docker exec my-container pip list

# Run as specific user
docker exec -u root my-container bash
```

### Command 9: docker logs

View container output.

```powershell
# View logs
docker logs my-container

# Follow logs in real-time (like tail -f)
docker logs -f my-container

# Show last 50 lines
docker logs --tail 50 my-container

# Show logs with timestamps
docker logs -t my-container
```

### Command 10: docker system prune

Clean up to free disk space.

```powershell
# Remove stopped containers, unused networks, dangling images
docker system prune

# Also remove unused images (more aggressive)
docker system prune -a

# Check disk usage first
docker system df
```

---

## 4. Practice Exercises

Work through these exercises in order:

### Exercise 1: Hello World

```powershell
docker run hello-world
```

Questions to answer:
- What happened exactly? (Read the output carefully)
- Run `docker ps -a`. What do you see?
- Run `docker images`. What images are now local?

### Exercise 2: Interactive Python Container

```powershell
docker run -it --rm python:3.12-slim bash
```

Inside the container:
```bash
python --version
pip install pandas numpy
python -c "import pandas as pd; print(pd.__version__)"
exit
```

Questions to answer:
- Run the same `docker run` command again. Is pandas still installed?
- Why or why not? (Think about container ephemerality)

### Exercise 3: Serve a Simple Web Page

```powershell
# Run nginx with port mapping
docker run -d --name learn-nginx -p 8080:80 nginx
```

- Open http://localhost:8080 in your browser
- Run `docker logs learn-nginx`
- Run `docker exec -it learn-nginx bash` and explore the filesystem
- Run `docker stop learn-nginx && docker rm learn-nginx`

### Exercise 4: Inspect and Clean Up

```powershell
docker ps -a
docker images
docker system df
docker system prune
docker system df
```

Compare disk usage before and after pruning.

---

## 5. Your First Dockerfile

See the `hello-world-custom/` folder. Build and run it:

```powershell
cd Docker_for_DS\01-basics\hello-world-custom
docker build -t my-hello:v1 .
docker run --rm my-hello:v1
```

Then modify the Dockerfile and rebuild. Notice which layers are cached and which are rebuilt.

---

## Key Takeaways

- Docker image = blueprint; container = running instance
- Images are built from Dockerfiles layer by layer, with caching
- Containers are ephemeral -- save outputs with volumes or `docker cp`
- Use `--rm` for disposable containers to avoid accumulating stopped containers
- Use `docker system prune` regularly to free disk space
