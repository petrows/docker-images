# Common image for GitHub linters
FROM ubuntu:24.04

LABEL org.opencontainers.image.source=https://github.com/petrows/docker-images

RUN apt-get update && apt-get install -qy --no-install-recommends \
    bash \
    git \
    curl \
    # Python packages
    python3 \
    python3-pip \
    python3-venv \
    # NodeJS
    nodejs \
    npm \
    && apt-get clean -q && rm -rf /var/lib/apt/lists/*

# Activate venv
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.* /opt/venv/

# Linters for Python
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r /opt/venv/requirements.txt

RUN pip freeze
