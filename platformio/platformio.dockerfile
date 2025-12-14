# Dockerfile to build platformio
FROM ghcr.io/petrows/github-linters:v6

# Default env
ENV HOME=/github/home
RUN mkdir -p -m 777 $HOME

RUN pipx install --global platformio==6.1.18

WORKDIR /app
