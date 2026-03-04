# Docker Cheat Sheet for Data Scientists

Quick reference for the most common Docker commands and patterns.

---

## Image Commands

| Command | What It Does |
|---------|-------------|
| `docker pull python:3.12-slim` | Download image from Docker Hub |
| `docker images` | List all local images |
| `docker build -t my-image:v1 .` | Build image from Dockerfile in current dir |
| `docker build -t my-image:v1 -f path/Dockerfile .` | Build using specific Dockerfile |
| `docker rmi my-image:v1` | Remove an image |
| `docker image prune` | Remove all unused images |
| `docker tag my-image:v1 myuser/my-image:v1` | Tag image for Docker Hub |
| `docker push myuser/my-image:v1` | Push image to Docker Hub |
| `docker history my-image:v1` | Show image layer history |
| `docker inspect my-image:v1` | Detailed image metadata |

---

## Container Commands

| Command | What It Does |
|---------|-------------|
| `docker run my-image` | Create and start a container |
| `docker run -it my-image bash` | Interactive mode with shell |
| `docker run -d my-image` | Detached (background) mode |
| `docker run --rm my-image` | Auto-remove container after exit |
| `docker run --name my-container my-image` | Name the container |
| `docker run -p 8888:8888 my-image` | Map host port 8888 to container port 8888 |
| `docker run -v $(pwd)/data:/app/data my-image` | Mount local folder into container |
| `docker run -e MY_VAR=value my-image` | Set environment variable |
| `docker ps` | List running containers |
| `docker ps -a` | List all containers (including stopped) |
| `docker stop my-container` | Gracefully stop container |
| `docker kill my-container` | Force-stop container |
| `docker start my-container` | Start a stopped container |
| `docker restart my-container` | Restart container |
| `docker rm my-container` | Remove stopped container |
| `docker container prune` | Remove all stopped containers |
| `docker logs my-container` | View container logs |
| `docker logs -f my-container` | Follow logs in real-time |
| `docker exec -it my-container bash` | Open shell in running container |
| `docker cp my-container:/app/output.csv ./output.csv` | Copy file from container |
| `docker stats` | Live resource usage (CPU, memory) |

---

## Volume Commands

| Command | What It Does |
|---------|-------------|
| `docker volume create my-vol` | Create a named volume |
| `docker volume ls` | List volumes |
| `docker volume inspect my-vol` | Volume details |
| `docker volume rm my-vol` | Remove a volume |
| `docker volume prune` | Remove all unused volumes |
| `docker run -v my-vol:/app/data my-image` | Mount named volume |
| `docker run -v $(pwd):/app my-image` | Mount current directory (bind mount) |

---

## Docker Compose Commands

| Command | What It Does |
|---------|-------------|
| `docker compose up` | Start all services |
| `docker compose up -d` | Start all services in background |
| `docker compose up --build` | Rebuild images before starting |
| `docker compose down` | Stop and remove containers |
| `docker compose down -v` | Stop, remove containers and volumes |
| `docker compose ps` | List service containers |
| `docker compose logs` | View all service logs |
| `docker compose logs -f service-name` | Follow logs for one service |
| `docker compose exec service-name bash` | Shell into a running service |
| `docker compose build` | Build all service images |
| `docker compose pull` | Pull latest images |
| `docker compose restart service-name` | Restart one service |
| `docker compose stop` | Stop without removing |
| `docker compose config` | Validate and print resolved config |

---

## System Cleanup

```powershell
# Remove all stopped containers, unused networks, dangling images
docker system prune

# Remove everything including unused images (free up disk space)
docker system prune -a

# Check disk usage
docker system df
```

---

## Dockerfile Instruction Reference

```dockerfile
FROM python:3.12-slim          # Base image (always first)
WORKDIR /app                   # Set working directory inside container
COPY requirements.txt .        # Copy files from host to container
RUN pip install -r requirements.txt  # Execute commands during BUILD
COPY . .                       # Copy remaining files
ENV PYTHONUNBUFFERED=1         # Set environment variable
EXPOSE 8888                    # Document port (does not publish it)
VOLUME ["/app/data"]           # Declare a mount point
USER nonroot                   # Switch to non-root user
ENTRYPOINT ["python"]          # Fixed executable (cannot be overridden easily)
CMD ["app.py"]                 # Default arguments (can be overridden at runtime)
```

| Instruction | Build vs Run | Purpose |
|-------------|-------------|---------|
| `FROM` | Build | Set base image |
| `RUN` | Build | Execute command (creates a layer) |
| `COPY` | Build | Copy files from host |
| `ADD` | Build | Copy files (also handles URLs, tar files) |
| `ENV` | Both | Set environment variable |
| `ARG` | Build only | Build-time variable |
| `WORKDIR` | Both | Set/create working directory |
| `EXPOSE` | Runtime | Document port (informational only) |
| `CMD` | Runtime | Default command when container starts |
| `ENTRYPOINT` | Runtime | Fixed entry point |
| `VOLUME` | Runtime | Declare mount point |
| `USER` | Both | Switch user |

---

## Common Patterns for Data Science

### Run a Python Script and Exit

```powershell
docker run --rm -v ${PWD}:/app my-ds-image python train.py
```

### Interactive Python Shell

```powershell
docker run -it --rm my-ds-image python
```

### Jupyter Lab with Volume (Windows PowerShell)

```powershell
docker run --rm -p 8888:8888 -v ${PWD}:/home/jovyan/work jupyter/datascience-notebook
```

### Pass Environment Variables from .env File

```powershell
docker run --env-file .env my-image
```

### Resource Limits (prevent runaway containers)

```powershell
docker run --memory="4g" --cpus="2.0" my-image
```

### Copy Output Files Out of Container

```powershell
# After container finishes, copy results
docker run --name trainer my-image python train.py
docker cp trainer:/app/model.pkl ./model.pkl
docker rm trainer
```

---

## Dockerfile Optimization Tips

1. **Order matters for cache** -- put things that change least at the top:
   ```dockerfile
   # Stable: base image and system deps first
   FROM python:3.12-slim
   RUN apt-get update && apt-get install -y gcc
   
   # Changes occasionally: requirements
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   
   # Changes often: source code last
   COPY . .
   ```

2. **Combine RUN commands** to reduce layers:
   ```dockerfile
   # Bad: 3 layers
   RUN apt-get update
   RUN apt-get install -y gcc
   RUN rm -rf /var/lib/apt/lists/*
   
   # Good: 1 layer
   RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*
   ```

3. **Use .dockerignore** to exclude unnecessary files:
   ```
   __pycache__/
   *.pyc
   .venv/
   .git/
   *.ipynb_checkpoints/
   data/raw/
   models/
   ```

4. **Use `slim` base images** -- `python:3.12-slim` is ~180MB vs `python:3.12` at ~1GB.

5. **Never run as root in production** -- add a non-root user.
