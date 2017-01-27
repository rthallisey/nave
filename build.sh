#!/bin/bash

ROOT=$(readlink -f $0)
BUILD_ROOT=`dirname $ROOT`
CONTAINER_DIR="${BUILD_ROOT}/containers"
CONFIG_ROOT="{CONFIG_ROOT:-/etc/nave}"

source "${BUILD_ROOT}/default-config.sh"
source "${BUILD_ROOT}/create_configs.sh"

CONTAINER_REG="${PROJECT}/${REGISTRY}"
TAG="${TAG:-latest}"

function docker-build-cmd {
    echo "Building container for ${SERVICE}"
    local registry="${CONTAINER_REG}-${SERVICE}:${TAG}"

    docker build -t $registry $@
    docker --config="${HOME}/.docker" push $registry
}

function build-templates {
    echo "Building templates for ${SERVICE}"

    sed "s/{{db_password}}/${DB_PASSWORD}/g" "${CONTAINER_DIR}/${SERVICE}/templates/start_template.sh" > "${BUILD_ROOT}/containers/${SERVICE}/start.sh"

    build-configs
}

for SERVICE in "$@"; do
    build-templates

    chmod +x "${CONTAINER_DIR}/${SERVICE}/start.sh"
    docker-build-cmd "${CONTAINER_DIR}/${SERVICE}"
done
