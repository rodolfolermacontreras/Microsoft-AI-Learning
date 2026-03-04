# ============================================================
# Python Data Science Environment
# ============================================================
# Base image: python:3.12-slim
#   - Official Python image with Debian Linux
#   - "slim" variant: no unnecessary packages, ~180MB vs ~1GB
#   - Always pin the minor version for reproducibility
FROM python:3.12-slim

# ============================================================
# LAYER 1: System dependencies
# ============================================================
# Install system-level packages needed to compile Python libs.
# - gcc, g++: C/C++ compilers (required by some pip packages)
# - libgomp1: OpenMP support for parallelism (e.g., LightGBM, XGBoost)
# - curl: for health checks, downloading resources
# Combine into a single RUN to minimize layers.
# Clean up apt cache in the same layer to keep image size down.
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libgomp1 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ============================================================
# LAYER 2: Python dependencies
# ============================================================
# Set working directory. Docker creates it if it doesn't exist.
WORKDIR /app

# Copy requirements BEFORE source code.
# Reason: pip install is slow and expensive. If only source code
# changes (but requirements.txt is unchanged), Docker reuses the
# cached pip layer. This is the most important optimization.
COPY requirements.txt .

# Upgrade pip and install packages.
# --no-cache-dir: don't cache downloaded packages (saves image space)
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ============================================================
# LAYER 3: Application files
# ============================================================
# Copy source code last (changes most frequently).
COPY . .

# ============================================================
# Security: Non-root user
# ============================================================
# Containers run as root by default. Best practice: run as a
# non-privileged user to reduce risk.
RUN useradd --create-home --shell /bin/bash dsuser
USER dsuser

# ============================================================
# Runtime configuration
# ============================================================
# PYTHONUNBUFFERED=1: Forces stdout/stderr to be unbuffered.
# Without this, print() output may not appear in docker logs.
ENV PYTHONUNBUFFERED=1

# PYTHONDONTWRITEBYTECODE=1: Don't write .pyc files.
# Keeps the container filesystem cleaner.
ENV PYTHONDONTWRITEBYTECODE=1

# Default command: drop into Python shell.
# Override at runtime: docker run ds-env:v1 python train.py
CMD ["python"]
