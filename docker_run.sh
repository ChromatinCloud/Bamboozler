#!/usr/bin/env bash

# docker_run.sh
# A convenience script to build and run the BamBoozler Docker container.

# Stop on error
set -e

# Name of the Docker image you want to create/use
IMAGE_NAME="bamboozler"

echo "[INFO] Building Docker image '${IMAGE_NAME}'..."
docker build -t "${IMAGE_NAME}" .

echo "[INFO] Running interactive Docker container..."
docker run -it "${IMAGE_NAME}"

