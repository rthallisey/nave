#!/bin/bash

ROOT=$(readlink -f $0)
BUILD_ROOT=`dirname $ROOT`
CONTAINER_DIR="${BUILD_ROOT}/containers"

source "${BUILD_ROOT}/default-config.sh"

CONTAINER_REG="nave/centos"
TAG="${TAG:-latest}"

function docker-build-cmd {
    echo "Building container for ${SERVICE}"
    local tag="${CONTAINER_REG}-${SERVICE}:${TAG}"

    docker build -t tag $@
}

function build-templates {
    echo "Building templates for ${SERVICE}"
    sed "s/{{cluster_name}}/${CLUSTER_NAME}/g" "${CONTAINER_DIR}/${SERVICE}/templates/${SERVICE}_template.conf" > "${BUILD_ROOT}/containers/${SERVICE}/${SERVICE}.conf"

    sed -i "s/{{cluster_addresses}}/${CLUSTER_ADDRESSES}/g" "${CONTAINER_DIR}/${SERVICE}/${SERVICE}.conf"

    sed "s/{{db_password}}/${DB_PASSWORD}/g" "${CONTAINER_DIR}/${SERVICE}/templates/start_template.sh" > "${BUILD_ROOT}/containers/${SERVICE}/start.sh"
}

for SERVICE in "$@"; do
    build-templates
    docker-build-cmd "${CONTAINER_DIR}/${SERVICE}"
done
