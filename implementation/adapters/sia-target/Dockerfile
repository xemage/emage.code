# SIA Target Agent Harness Adapter
# This Dockerfile builds a container that runs a SIA target agent
# with configurable model base URLs for trajectory capture via CWSO proxy.
#
# Security Requirements:
# - Launcher MUST use: docker run --rm --read-only --tmpfs /tmp --tmpfs /run
# - /workspace mount point is the only writable location
# - No API keys are baked into the image
#

FROM python:3.12-slim-bookworm

# Build arguments for reproducible builds
ARG SIA_GIT_REF=refs/tags/v0.2.1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements.txt for pip install
COPY requirements.txt /tmp/requirements.txt

# Install Python dependencies with pinned versions for reproducibility
RUN pip install --no-cache-dir -r /tmp/requirements.txt && \
    rm /tmp/requirements.txt

# Clone SIA at the exact pinned version tag — build fails if the tag does not exist
# (no silent fallback to main). This is required for reproducible, auditable builds.
RUN git clone --depth 1 --branch "${SIA_GIT_REF}" \
    https://github.com/hexo-ai/sia.git /sia && \
    pip install --no-cache-dir -e /sia && \
    rm -rf /sia/.git

# Copy harness entrypoint script
COPY harness-entrypoint.py /app/harness-entrypoint.py
RUN chmod +x /app/harness-entrypoint.py

# Create required directories for security model
# /tmp and /run will be mounted as tmpfs by launcher (--tmpfs flags)
# /workspace will be mounted by launcher as RW mount
RUN mkdir -p /workspace && \
    mkdir -p /tmp && \
    mkdir -p /run

# Set Python to unbuffered mode for real-time logging
ENV PYTHONUNBUFFERED=1

# Default environment values (can be overridden by launcher)
ENV SIA_BACKEND=claude
ENV SIA_MODEL=haiku
ENV SIA_MAX_TURNS=10

# Entrypoint: run the harness script
ENTRYPOINT ["/usr/local/bin/python", "/app/harness-entrypoint.py"]
