# Dockerfile to build platformio
FROM ghcr.io/petrows/github-linters:v5

# Default env
ENV HOME=/github/home
RUN mkdir -p -m 777 $HOME

RUN pip install platformio==6.1.18

WORKDIR /app
