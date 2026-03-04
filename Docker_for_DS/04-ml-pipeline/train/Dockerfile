FROM python:3.12-slim

# System dependencies for scikit-learn
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

# Create models directory (will be overridden by volume mount at runtime)
RUN mkdir -p /app/models

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV MODELS_DIR=/app/models

# Training is a batch job -- run and exit
CMD ["python", "train.py"]
