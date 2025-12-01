ARG PWS_PODMAN_VERSION=5.7.0
FROM mgoltzsche/podman:$PWS_PODMAN_VERSION

LABEL org.opencontainers.image.source=https://github.com/petrows/docker-images
LABEL org.opencontainers.image.description="Podman static"

RUN apk add --update --no-cache \
    bash \
    git \
    python3 \
    py3-pip \
    py3-pyaml

RUN ln -s /usr/local/bin/podman /usr/local/bin/docker

# Activate venv
RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:/opt/bin:$PATH"

# Copy working requirements reciepes
COPY requirements.* /opt/venv/

# Linters for Python and other software
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r /opt/venv/requirements.txt
