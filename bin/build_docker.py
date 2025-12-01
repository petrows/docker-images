#!/usr/bin/env python3
"""
Build Docker images.
"""
import argparse
from datetime import datetime, timezone
import fcntl
import logging
import os
import subprocess
import sys
import requests
import yaml



config = {}
logging.basicConfig(
  level=logging.INFO,
  format="%(levelname)s: %(message)s"
)

def main():
    """
    Entry point function.
    """

    argparser = argparse.ArgumentParser(description="Build Docker images.")
    argparser.add_argument(
        "--config",
        type=str,
        default="docker.yml",
        help="Path to the Docker build configuration file.",
    )
    argparser.add_argument(
        "--detect-images",
        action="store_true",
        help="Detect new images for Docker images and print list.",
    )
    argparser.add_argument(
        "--build",
        type=str,
        default="",
        help="Detect new images for Docker images and print list.",
    )
    argparser.add_argument(
        "--deploy",
        type=str,
        default="",
        help="Deploy new images for Docker images and print list.",
    )
    argparser.add_argument(
      "-l",
      "--log-level",
      type=str,
      choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
      default="INFO",
      help="Set the logging level.",
    )
    args = argparser.parse_args()

    logging.getLogger().setLevel(args.log_level.upper())

    read_config()

    if args.detect_images:
        detect_images()

    if args.build:
        get_build_sh(args.build, push=False)

    if args.deploy:
        get_build_sh(args.deploy, push=True)


def exec(command: list[str]) -> bool:
    command_base = os.path.basename(command[0])
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    fl = fcntl.fcntl(p.stdout, fcntl.F_GETFL)
    fcntl.fcntl(p.stdout, fcntl.F_SETFL, fl | os.O_NONBLOCK)

    fl = fcntl.fcntl(p.stderr, fcntl.F_GETFL)
    fcntl.fcntl(p.stderr, fcntl.F_SETFL, fl | os.O_NONBLOCK)

    while p.poll() is None:
        try:
            line = p.stdout.readline()
            if line:
                logging.debug(f"{command_base}: {line.decode('utf-8').strip()}")
        except OSError:
            pass

        try:
            line = p.stderr.readline()
            if line:
                logging.debug(f"{command_base}! {line.decode('utf-8').strip()}")
        except OSError:
            pass

    p.wait()
    if p.returncode != 0:
        logging.debug(f"Command '{' '.join(command)}' return code {p.returncode}")

    return p.returncode == 0


def read_config():
    """
    Reads configuration for building Docker images.
    """
    global config
    with open("docker.yml", "r") as f:
        logging.debug("Reading configuration from docker.yml")
        config = yaml.safe_load(f)


def image_full_name(image: str, tag: str) -> str:
    """
    Returns full image name with prefix.
    """
    global config
    prefix = config['repo']['prefix']
    return f"{prefix}/{image}:{tag}"


def detect_images_tags(name: str):
    """
    Detects new image tags for build.
    """
    global config

    tags_detected = []

    for image in config.get("images", []):
        if name == image['name']:
            tags = ghcr_image_tags(f"{config['repo']['owner']}", name)
            logging.debug(f"Existing tags for image {name}: {tags}")
            for tag in image.get("tags", []):
                if tag not in tags:
                    logging.debug(f"New image detected: {name}:{tag}")
                    tags_detected.append(tag)

    return tags_detected


def detect_images():
    """
    Detects new images for build.
    """
    global config

    images_detected = []

    for image in config.get("images", []):
        name = image.get("name", "")
        tags = detect_images_tags(name)
        if tags:
            images_detected.append(name)

    # if not images_detected:
    #     print("::error::No new images detected for build.")
    #     sys.exit(1)

    print(f'images={images_detected}')


def get_build_sh(name: str, push=False) -> str:
    """
    Returns build.sh path for image.
    """
    global config

    out = []
    out.append("#!/usr/bin/env bash")
    out.append("")

    image = next((img for img in config.get("images", []) if img.get("name") == name), None)
    if not image:
        logging.error(f"Image '{name}' not found in configuration.")
        sys.exit(1)

    tags = detect_images_tags(name)
    if not tags:
        logging.info(f"No new tags detected for image '{name}'.")
        sys.exit(1)

    out.append(f'echo "::group::{name}"')
    if push:
        for tag in tags:
            full_name = image_full_name(name, tag)
            out.append(f'echo "Deploying image: {full_name}"')
            out.append(f'docker push {full_name}')
    else:
        out.append(f'echo "Building image: {name}"')
        out.append('(')
        out.append(f'cd {name}')
        build_args = []
        build_args.append(['--progress', 'plain'])
        build_args.append(['--network', 'host'])
        build_args.append(['--cache-from', config['repo']['cache']])
        build_args.append(['--cache-to', config['repo']['cache']])
        build_args.append(['--label', f'org.opencontainers.image.source="https://github.com/{config["repo"]["owner"]}"'])
        build_args.append(['--label', f'org.opencontainers.image.description="{image.get("description", "")}"'])
        iso_time = datetime.now(timezone.utc).isoformat()
        build_args.append(['--label', f'org.opencontainers.image.created="{iso_time}"'])
        for tag in tags:
            full_name = image_full_name(name, tag)
            build_args.append(['-t', full_name])
        build_args.append(['-f', f'{name}.dockerfile'])
        out.append(f'docker build {" ".join([item for sublist in build_args for item in sublist])} .')
        out.append(')')
    out.append('echo "::endgroup::"')

    print("\n".join(out))


def ghcr_image_tags(owner: str, image: str) -> bool:
    """
    Check if a GHCR image:tag exists, supporting public and private repos.

    Args:
        owner_repo: "owner/repo" format, e.g., "petrows/github-linters"
        tag: image tag, e.g., "v3"

    Returns:
        True if tag exists, False otherwise.
    """
    github_token = os.environ.get("GITHUB_TOKEN")  # read token from env

    headers = {
        "Accept": "application/vnd.docker.distribution.manifest.v2+json"
    }

    # Token flow for public and private images
    token_headers = {}
    token_url = f"https://ghcr.io/token?scope=repository:{owner}/{image}:pull&service=ghcr.io"
    token_resp = requests.get(token_url, auth=(owner, github_token), headers=token_headers)
    token_resp.raise_for_status()
    token = token_resp.json()["token"]
    headers["Authorization"] = f"Bearer {token}"

    manifest_url = f"https://ghcr.io/v2/{owner}/{image}/tags/list"
    resp = requests.get(manifest_url, headers=headers)

    if resp.status_code == 200:
        return resp.json().get("tags", [])
    elif resp.status_code == 404:
        return []
    else:
        resp.raise_for_status()


if __name__ == "__main__":
    main()
