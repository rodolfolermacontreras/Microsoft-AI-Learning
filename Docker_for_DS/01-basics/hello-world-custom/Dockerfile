# Use a minimal Python base image
# python:3.12-slim is ~180MB (vs ~1GB for full python:3.12)
FROM python:3.12-slim

# Set working directory inside the container
# All subsequent COPY/RUN commands use this as the base path
WORKDIR /app

# Copy only what we need
COPY hello.py .

# CMD = default command when the container starts
# This can be overridden at runtime: docker run my-hello:v1 python -c "print('override')"
CMD ["python", "hello.py"]
