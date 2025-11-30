ARG PWS_PODMAN_VERSION=5.7.0
FROM mgoltzsche/podman:$PWS_PODMAN_VERSION

LABEL org.opencontainers.image.source=https://github.com/petrows/docker-images
LABEL org.opencontainers.image.description="Podman static"

RUN apk add --update --no-cache \
    bash \
    git \
    python3 \
    py-pip

RUN ln -s /usr/local/bin/podman /usr/local/bin/docker
