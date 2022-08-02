#!/bin/bash
echo "DOCKER_GID=$(getent group docker | cut -d: -f3)"
