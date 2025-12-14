# Dockerfile to build platformio
FROM ghcr.io/petrows/github-linters:v6

# Default env
ENV HOME=/github/home
RUN mkdir -p -m 777 $HOME

RUN apt-get update && apt-get install -qy --no-install-recommends \
    texlive-xetex \
    texlive-latex-recommended \
    texlive-latex-extra \
    texlive-fonts-recommended \
    texlive-fonts-extra \
    texlive-lang-english \
    texlive-lang-german \
    texlive-lang-cyrillic \
    texlive-plain-generic \
    biber \
    && apt-get clean -q && rm -rf /var/lib/apt/lists/*

WORKDIR /app
