# 04 - ML Pipeline: Train and Serve Containers

Two-container ML workflow:
1. **Training container** -- runs model training, saves artifacts
2. **Serving container** -- loads artifacts, exposes a prediction API

This pattern mirrors production ML systems where training and inference are separate, independently deployable units.

---

## What This Section Covers

- Separate Docker images for training and inference
- Passing model artifacts between containers via shared volumes
- A minimal Flask prediction API
- The container lifecycle for batch training + continuous serving

---

## Files in This Section

```
04-ml-pipeline/
|-- README.md
|-- train/
|   |-- Dockerfile        # Training container image
|   |-- train.py          # Training script (sklearn, saves model.pkl + metadata)
|   |-- requirements.txt
|-- serve/
|   |-- Dockerfile        # Serving container image
|   |-- serve.py          # Flask REST API for predictions
|   |-- requirements.txt
|-- models/               # Shared folder (created at runtime via volume mount)
|-- data/                 # Sample data (created at runtime)
```

---

## Architecture

```
[Training Container]                [Serving Container]
train.py                            serve.py
  |                                   |
  | saves model.pkl                   | loads model.pkl
  v                                   v
[models/ volume] <------ shared -----> [models/ volume]
  (on your host machine)
```

The `models/` folder is shared between containers via a bind mount. The training container writes `model.pkl` and `metadata.json`. The serving container reads them.

---

## Step-by-Step Instructions

### Step 1: Create Output Directories

```powershell
cd C:\Training\Microsoft\Copilot\Docker_for_DS\04-ml-pipeline

New-Item -ItemType Directory -Force -Path models
New-Item -ItemType Directory -Force -Path data
```

### Step 2: Build Both Images

```powershell
# Build training image
docker build -t ds-trainer:v1 -f train/Dockerfile train/

# Build serving image
docker build -t ds-server:v1 -f serve/Dockerfile serve/
```

### Step 3: Run Training

```powershell
# Run training container
# - Mounts models/ folder so saved artifacts appear on your host
# - Container exits when training is done
docker run --rm \
  -v ${PWD}/models:/app/models \
  ds-trainer:v1
```

After this completes, check:
```powershell
Get-ChildItem models/
# Should see: model.pkl, metadata.json, training_report.json
```

### Step 4: Start the Prediction Server

```powershell
# Start serving container in background
# - Mounts same models/ folder so it can read the trained model
# - Maps port 5000 for API access
docker run -d --name prediction-api \
  -p 5000:5000 \
  -v ${PWD}/models:/app/models \
  ds-server:v1

# Check it's running
docker ps
docker logs prediction-api
```

### Step 5: Test the API

```powershell
# Health check
Invoke-RestMethod -Uri http://localhost:5000/health

# Get feature info
Invoke-RestMethod -Uri http://localhost:5000/info

# Make a prediction (single instance)
$body = '{"features": [5.1, 3.5, 1.4, 0.2]}'
Invoke-RestMethod -Uri http://localhost:5000/predict `
  -Method POST `
  -ContentType "application/json" `
  -Body $body

# Or use curl if available
curl -X POST http://localhost:5000/predict `
  -H "Content-Type: application/json" `
  -d '{"features": [5.1, 3.5, 1.4, 0.2]}'
```

### Step 6: Retrain and Hot-Reload

```powershell
# Run training again (e.g., with different hyperparameters)
docker run --rm -v ${PWD}/models:/app/models ds-trainer:v1

# No need to restart the serving container -- it reloads the model on each request
# (see serve.py for lazy-loading pattern)

# Test again
Invoke-RestMethod -Uri http://localhost:5000/predict `
  -Method POST `
  -ContentType "application/json" `
  -Body '{"features": [6.7, 3.0, 5.2, 2.3]}'
```

### Step 7: Cleanup

```powershell
docker stop prediction-api
docker rm prediction-api
```

---

## Exercises

### Exercise 1: Change Hyperparameters

In `train/train.py`, change the training parameters (e.g., `n_estimators`, `max_depth`). Rebuild and retrain. Check the `metadata.json` to see if metrics improved.

### Exercise 2: Add a Batch Prediction Endpoint

In `serve/serve.py`, add a `/predict/batch` endpoint that accepts a list of feature vectors and returns a list of predictions.

### Exercise 3: Model Versioning

Modify `train.py` to save models with timestamped filenames (e.g., `model_20260304_143022.pkl`). Modify the server to load the latest model automatically.

### Exercise 4: Add Input Validation

In `serve.py`, add validation that returns a 400 error with a helpful message if the input has the wrong number of features.

---

## Key Takeaways

- Training and serving containers share state only through mounted volumes
- Train-once-serve-many pattern: rebuild server image only when code changes, not when model changes
- The serving container should be stateless -- all state comes from the mounted model files
- Always validate API inputs before passing to the model
