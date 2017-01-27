#!/bin/bash

function copy-files {
    local source=$1
    local dest=$2
    cp $source $dest
}

function copy-kubernetes-template {
    copy-files $KUBE_TEMPLATE $KUBE_FILE
}

function copy-config-template {
    mkdir -p "${CONFIG_ROOT}/${SERVICE}-${cluster_count}"
    copy-files $CONFIG_TEMPLATE $CONFIG_FILE
}

function copy-container-template {
    copy-files $CONTAINER_TEMPLATE $CONTAINER_START_SCRIPT
}

function variable-replace {
    sed -i "s/{{$1}}/$2/g" $3
}

function config-variable-replace {
    variable-replace $1 $2 $CONFIG_FILE
}

function kube-variable-replace {
    variable-replace $1 $2 $KUBE_FILE
}

function container-variable-replace {
    variable-replace $1 $2 $CONTAINER_START_SCRIPT
}
