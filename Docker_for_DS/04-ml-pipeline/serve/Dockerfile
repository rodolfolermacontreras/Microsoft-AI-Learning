FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

# Create models directory (overridden by volume mount at runtime)
RUN mkdir -p /app/models

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV MODELS_DIR=/app/models
ENV PORT=5000

# Document which port this container listens on
EXPOSE 5000

# Serving is a long-running process
CMD ["python", "serve.py"]
