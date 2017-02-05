#!/bin/bash

ROOT=$(readlink -f $0)
BUILD_ROOT=`dirname $ROOT`
CONTAINER_DIR="${BUILD_ROOT}/containers"
NAVE_DIR="${BUILD_ROOT}/nave"
CONFIG_ROOT="${CONFIG_ROOT:-/etc/nave}"

source "${BUILD_ROOT}/default-config.sh"
source "${BUILD_ROOT}/create-configs.sh"

CONTAINER_REG="${PROJECT}/${REGISTRY}"
TAG="${TAG:-latest}"

function docker-build-cmd {
    echo "Building container for ${SERVICE}"
    local service="${2:-$SERVICE}"
    local registry="${CONTAINER_REG}-${service}:${TAG}"

    echo $registry
    docker build -t $registry $1
    docker --config="${HOME}/.docker" push $registry
}

function build-templates {
    echo "Building templates for ${SERVICE}"
    CONTAINER_TEMPLATE="${CONTAINER_DIR}/${SERVICE}/templates/start_template.sh"
    CONTAINER_START_SCRIPT="${CONTAINER_DIR}/${SERVICE}/start.sh"
    copy-container-template
    container-variable-replace "db_password" "${DB_PASSWORD}"
    build-configs
}

docker-build-cmd "${NAVE_DIR}" "vessel-base"
for SERVICE in "$@"; do
    build-templates

    chmod +x "${CONTAINER_DIR}/${SERVICE}/start.sh"
    docker-build-cmd "${CONTAINER_DIR}/${SERVICE}"
    docker-build-cmd "${NAVE_DIR}/${SERVICE}_vessel" "mariadb-vessel"
done
