#!/bin/bash

VERSION=$(cat VERSION)
echo "1. MyConnectome version to deploy is ${VERSION}"
CONTAINER="poldracklab/myconnectome-explore"
echo "2. Building ${CONTAINER}:latest"
docker build -t "${CONTAINER}" .
echo "3. Tagging with version"
docker tag "${CONTAINER}" "${CONTAINER}:${VERSION}"
echo "4. Pushing ${CONTAINER}"
docker push "${CONTAINER}"
