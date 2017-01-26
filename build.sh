#!/bin/bash

ROOT=$(readlink -f $0)
BUILD_ROOT=`dirname $ROOT`
CONTAINER_DIR="${BUILD_ROOT}/containers"

source "${BUILD_ROOT}/default-config.sh"
source "${BUILD_ROOT}/create_configs.sh"

CONTAINER_REG="ansibleapp/nave-centos"
TAG="${TAG:-latest}"

function docker-build-cmd {
    echo "Building container for ${SERVICE}"
    local tag="${CONTAINER_REG}-${SERVICE}:${TAG}"

    docker build -t $tag $@
}

function build-templates {
    echo "Building templates for ${SERVICE}"

    sed "s/{{db_password}}/${DB_PASSWORD}/g" "${CONTAINER_DIR}/${SERVICE}/templates/start_template.sh" > "${BUILD_ROOT}/containers/${SERVICE}/start.sh"

    templates-to-configs $CLUSTER_SIZE
}

for SERVICE in "$@"; do
    build-templates

    chmod +x "${CONTAINER_DIR}/${SERVICE}/start.sh"
    docker-build-cmd "${CONTAINER_DIR}/${SERVICE}"
done
