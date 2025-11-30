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
    config_path = args.config
    print(f"Using configuration file: {config_path}")


def read_config():
    """
    Reads configuration for building Docker images.
    """
    pass


if __name__ == "__main__":
    main()
