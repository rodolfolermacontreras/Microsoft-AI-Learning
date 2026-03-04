# 02 - Python Data Science Environment

Build a custom Docker image with all your data science libraries pre-installed. This is your "DS workbench" image -- a foundation you can reuse across projects.

---

## What This Section Covers

- Writing a Dockerfile for a Python DS environment
- Pinning dependency versions for reproducibility
- Using .dockerignore to keep images lean
- Mounting local data directories into the container

---

## Files in This Section

```
02-python-environment/
|-- README.md              # This file
|-- Dockerfile             # Image definition
|-- requirements.txt       # DS dependencies (pinned versions)
|-- .dockerignore          # Files to exclude from build context
|-- explore_env.py         # Script to verify the environment
```

---

## Step-by-Step Instructions

### Step 1: Review the Dockerfile

Open `Dockerfile` and read the comments. Pay attention to:
- The base image chosen and why
- The layer ordering (what changes least is first)
- The non-root user setup

### Step 2: Build the Image

```powershell
# Navigate to this section folder
cd C:\Training\Microsoft\Copilot\Docker_for_DS\02-python-environment

# Build the image
# -t = name:tag
# . = build context (current directory)
docker build -t ds-env:v1 .
```

Watch the output. Notice:
- Which layers are downloaded
- How pip installs packages
- How long the build takes (note this for when you rebuild)

### Step 3: Run the Environment Check Script

```powershell
# Run the exploration script
docker run --rm ds-env:v1 python explore_env.py
```

You should see all installed libraries and their versions.

### Step 4: Start an Interactive Python Session

```powershell
docker run --rm -it ds-env:v1 python
```

Try inside Python:
```python
import pandas as pd
import numpy as np
import sklearn
print(pd.__version__, np.__version__, sklearn.__version__)
exit()
```

### Step 5: Mount Your Local Data Directory

The key to working with Docker in DS: mount your local data so the container can read it.

```powershell
# On Windows PowerShell, use ${PWD} for current directory
# Mount local data/ folder into /app/data in the container
docker run --rm -v ${PWD}/data:/app/data ds-env:v1 python -c "
import os
print('Files in /app/data:', os.listdir('/app/data'))
"
```

Create a `data/` folder and add a CSV file to test this.

### Step 6: Run a Script from Your Local Machine

```powershell
# Mount current directory and run a local script
docker run --rm -v ${PWD}:/app/workspace -w /app/workspace ds-env:v1 python my_analysis.py
```

This pattern lets you:
- Edit code on your host with your normal IDE
- Run code inside the container (consistent environment)
- Output files persist on your host (via the mount)

### Step 7: Rebuild After Changing Requirements

Add a new package to `requirements.txt` (e.g., `xgboost`), then rebuild:

```powershell
docker build -t ds-env:v2 .
```

Notice which layers are cached and which are rebuilt. Because `requirements.txt` is copied before source code, only the pip install layer and everything after it is invalidated.

---

## Exercises

### Exercise 1: Layer Caching

1. Build `ds-env:v1` (note the time)
2. Change only `explore_env.py`
3. Rebuild -- observe which layers are cached
4. Now change `requirements.txt`
5. Rebuild -- observe that pip install runs again

### Exercise 2: Image Size Comparison

Build with different base images and compare sizes:

```powershell
# Build with slim base (our default)
docker build -t ds-env:slim .

# Temporarily change Dockerfile to use full base:
# FROM python:3.12
docker build -t ds-env:full .

docker images | grep ds-env
```

### Exercise 3: Environment Variable Injection

```powershell
# Pass a config value at runtime
docker run --rm -e DATA_PATH=/app/data ds-env:v1 python -c "
import os
print('DATA_PATH:', os.environ.get('DATA_PATH', 'not set'))
"
```

### Exercise 4: Using an .env File

Create a file called `.env`:
```
DATA_PATH=/app/data
MODEL_NAME=my-model
```

Then run:
```powershell
docker run --rm --env-file .env ds-env:v1 python -c "
import os
print(os.environ.get('DATA_PATH'))
print(os.environ.get('MODEL_NAME'))
"
```

---

## Common Issues

| Problem | Cause | Fix |
|---------|-------|-----|
| `pip install` fails | Network issue during build | Use `--network=host` flag or check proxy |
| Container can't read mounted files | Windows path format | Use `${PWD}` not `%CD%` in PowerShell |
| `Permission denied` on mounted files | User mismatch | Run with `--user $(id -u):$(id -g)` on Linux |
| Image takes 5+ minutes to build | No build cache | Normal on first build; subsequent builds use cache |
| `ModuleNotFoundError` in container | Package not in requirements.txt | Add to requirements.txt, rebuild |

---

## Key Takeaways

- Pin ALL dependency versions in requirements.txt for reproducibility
- Order Dockerfile instructions from least-to-most-frequently-changed
- Use bind mounts (`-v`) to read/write data from your host
- NEVER put secrets (API keys) in a Dockerfile or requirements.txt
- Use `.dockerignore` to keep build context small and fast
