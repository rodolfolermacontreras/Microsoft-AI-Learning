# 03 - Jupyter Lab in Docker

Run Jupyter Lab inside a Docker container, with your local notebooks persisted on your host machine. This is one of the most practical Docker patterns for data scientists.

---

## What This Section Covers

- Running Jupyter Lab as a Docker container
- Volume mounting to persist notebooks
- Port mapping to access Jupyter from your browser
- Using Docker Compose for repeatable startup
- Custom Jupyter image with additional DS libraries

---

## Files in This Section

```
03-jupyter/
|-- README.md              # This file
|-- Dockerfile             # Custom Jupyter image
|-- docker-compose.yml     # Repeatable startup config
|-- notebooks/             # Your notebooks live here (persisted via volume)
|-- .dockerignore          # Build context exclusions
```

---

## Quick Start (Pre-built Image)

The fastest way to start -- use Jupyter's official image with no build required:

```powershell
# Navigate to this folder
cd C:\Training\Microsoft\Copilot\Docker_for_DS\03-jupyter

# Create notebooks folder (persisted on your host)
New-Item -ItemType Directory -Force -Path notebooks

# Run Jupyter Lab using the official full DS image
docker run --rm -p 8888:8888 \
  -v ${PWD}/notebooks:/home/jovyan/work \
  jupyter/datascience-notebook
```

Copy the URL from the terminal output (the one with `127.0.0.1:8888/?token=...`) and open it in your browser.

Your notebooks will be saved to `03-jupyter/notebooks/` on your host.

---

## Custom Jupyter Image

Build a custom image based on the official Jupyter image but with YOUR specific packages:

### Step 1: Build

```powershell
cd C:\Training\Microsoft\Copilot\Docker_for_DS\03-jupyter
docker build -t my-jupyter:v1 .
```

### Step 2: Run

```powershell
docker run --rm -p 8888:8888 \
  -v ${PWD}/notebooks:/home/jovyan/work \
  my-jupyter:v1
```

---

## Docker Compose (Recommended)

Docker Compose remembers all the run options so you don't have to type them every time.

### Start Jupyter

```powershell
cd C:\Training\Microsoft\Copilot\Docker_for_DS\03-jupyter
docker compose up
```

### Start in Background

```powershell
docker compose up -d
docker compose logs -f  # follow logs to get the token URL
```

### Stop Jupyter

```powershell
docker compose down
```

---

## Accessing Jupyter

When Jupyter starts, look in the terminal for a line like:

```
http://127.0.0.1:8888/lab?token=abc123def456...
```

Copy that URL into your browser. The token is your password for this session.

To use a fixed password instead:

```yaml
# In docker-compose.yml, add to the command:
command: start-notebook.sh --NotebookApp.password='sha1:...'
```

Or set `JUPYTER_TOKEN`:
```yaml
environment:
  - JUPYTER_TOKEN=mypassword
```

---

## Volume Mounting Explained

The `-v ${PWD}/notebooks:/home/jovyan/work` flag does:

```
Your host machine                 Inside container
C:\Training\...\03-jupyter\notebooks  <---->  /home/jovyan/work
```

Everything you do in the `/home/jovyan/work` directory inside Jupyter is saved to your host's `notebooks/` folder. This means:
- Notebooks persist when the container stops
- You can edit notebooks with your host IDE while the container runs
- No data loss when you update the image

---

## Exercises

### Exercise 1: Basic Notebook

1. Start Jupyter with `docker compose up`
2. Create a new notebook
3. Run:
   ```python
   import pandas as pd
   import numpy as np
   df = pd.DataFrame({"x": range(10), "y": np.random.randn(10)})
   df.plot()
   ```
4. Stop Jupyter with `docker compose down`
5. Restart with `docker compose up`
6. Verify your notebook is still there

### Exercise 2: Install a Package at Runtime

Inside a Jupyter cell:
```python
import subprocess
subprocess.run(["pip", "install", "yfinance"])
import yfinance as yf
```

This works but is NOT persistent -- if you rebuild the image, the package is gone.
To make it permanent: add to `requirements.txt`, rebuild.

### Exercise 3: Multiple Jupyter Instances

Open two terminals and run:
```powershell
# Terminal 1
docker run --rm -p 8888:8888 -v ${PWD}/notebooks:/home/jovyan/work my-jupyter:v1

# Terminal 2
docker run --rm -p 8889:8888 -v ${PWD}/notebooks:/home/jovyan/work my-jupyter:v1
```

Two Jupyter instances, same notebooks folder, different ports (8888 and 8889).

---

## Common Issues

| Problem | Cause | Fix |
|---------|-------|-----|
| `Permission denied` on notebooks folder | User ID mismatch | Add `--user root` flag or `CHOWN_HOME=yes` env var |
| Can't access `localhost:8888` | Port already in use | Change host port: `-p 8899:8888` |
| Token not shown | Jupyter started too fast | Run `docker compose logs` to find it |
| Kernel dies on large datasets | Memory limit | Add `--memory="8g"` to docker run |
| Packages missing after rebuild | Not in requirements.txt | Add them, rebuild |
