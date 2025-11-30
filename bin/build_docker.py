#!/usr/bin/env python3
"""
Build Docker images.
"""
import argparse


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
        "--detect-tags",
        action="store_true",
        help="Detect new tags for Docker images and print list.",
    )
    args = argparser.parse_args()
    # config_path = args.config
    # print(f"Using configuration file: {config_path}")

    if args.detect_tags:
        detect_tags()


def read_config():
    """
    Reads configuration for building Docker images.
    """
    pass

def detect_tags():
    """
    Detects new tags for Docker images.
    """
    print('images=["ghcr.io/petrows/github-linters:v3-test"]')


if __name__ == "__main__":
    main()
