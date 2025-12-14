# Common image for GitHub linters
FROM docker.io/library/ubuntu:24.04

LABEL org.opencontainers.image.source=https://github.com/petrows/docker-images
LABEL org.opencontainers.image.description="Set of generic linters for common GitHub tasks"

RUN apt-get update && apt-get install -qy --no-install-recommends \
    bash \
    ssh \
    git \
    curl \
    # Python packages
    python3 \
    python3-pip \
    python3-venv \
    # NodeJS
    nodejs \
    npm \
    zstd \
    && apt-get clean -q && rm -rf /var/lib/apt/lists/*

ENV HOME=/github/home
RUN mkdir -p -m 777 $HOME

# Activate venv
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:/opt/bin:$PATH"

# Copy working requirements reciepes
COPY requirements.* /opt/venv/

# Linters for Python and other software
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r /opt/venv/requirements.txt

# Display current installed packages
RUN pip freeze

# Copy our scripts
COPY bin /opt/bin
RUN chmod +x /opt/bin/*
