# ============================================================
# Custom Jupyter Lab Image for Data Science
# ============================================================
# Base: jupyter/datascience-notebook (from Jupyter Docker Stacks)
# This already includes: Python, R, pandas, numpy, scipy, matplotlib,
# scikit-learn, and Jupyter Lab.
# See: https://jupyter-docker-stacks.readthedocs.io/en/latest/

# Pin the image tag to a specific digest for full reproducibility.
# Check the latest at: https://hub.docker.com/r/jupyter/datascience-notebook/tags
FROM jupyter/datascience-notebook:python-3.11

# ============================================================
# Install additional Python packages
# ============================================================
# Note: We run as the default jovyan user (UID 1000).
# pip install works without sudo in this base image.
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# ============================================================
# Jupyter configuration
# ============================================================
# Set default working directory to the persistent work folder
WORKDIR /home/jovyan/work

# The base image's ENTRYPOINT and CMD handle Jupyter Lab startup.
# We don't need to override them.
