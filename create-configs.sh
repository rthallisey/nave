#!/bin/bash

source "${BUILD_ROOT}/utils.sh"

function resolve-special-cases {
    # First mariadb node needs --wsrep-new-cluster"
    if [[ "${CONFIG_NAME}" == "mariadb-1" ]]; then
        kube-variable-replace "bootstrap_args" "--wsrep-new-cluster"
    else
        kube-variable-replace "bootstrap_args" "''"
    fi
}

function copy-bootstrap-template {
    KUBE_TEMPLATE="${BUILD_ROOT}/kubernetes/${SERVICE}/templates/${SERVICE}-bootstrap-template.yaml"
    KUBE_FILE="${BUILD_ROOT}/kubernetes/${SERVICE}/${SERVICE}-bootstrap.yaml"
    copy-kubernetes-template
    kube-variable-replace "container_name" "${PROJECT}\/${REGISTRY}-${SERVICE}:${TAG}"
}

function build-kube-resources {
  for template_file in $(ls "${BUILD_ROOT}/kubernetes/${SERVICE}/templates/" | grep -v bootstrap |xargs -n 1 basename); do
    local kube_file=$(echo $template_file | sed -e "s/template/${cluster_count}/")

    KUBE_TEMPLATE="${BUILD_ROOT}/kubernetes/${SERVICE}/templates/${template_file}"
    KUBE_FILE="${BUILD_ROOT}/kubernetes/${SERVICE}/${kube_file}"

    # Kubernetes templates
    copy-kubernetes-template
    resolve-special-cases
    kube-variable-replace "count" "${cluster_count}"
    kube-variable-replace "container_name" "${PROJECT}\/${REGISTRY}-${SERVICE}:${TAG}"
  done
}

function build-configs {
  for cluster_count in $(seq 1 $CLUSTER_SIZE); do
    if [[ "${CLUSTER_SIZE}" -eq 1 ]]; then
        CONFIG_NAME="${SERVICE}"
    else
        CONFIG_NAME="${SERVICE}-${cluster_count}"
    fi
    CONFIG_FILE="${CONFIG_ROOT}/${CONFIG_NAME}/${SERVICE}.conf"
    CONFIG_TEMPLATE="${CONTAINER_DIR}/${SERVICE}/templates/${SERVICE}_template.conf"

    # Create Kubernetes Resources
    build-kube-resources
    copy-bootstrap-template

    # Create $SERVICE.conf
    copy-config-template
    config-variable-replace "cluster_name" "${CLUSTER_NAME}"
    config-variable-replace "count" "${cluster_count}"
    config-variable-replace "cluster_addresses" "${CLUSTER_ADDRESSES}"
    config-variable-replace "db_password" "${DB_PASSWORD}"

    # Create Kubernetes configmaps
    if [[ -e "${ROOT}/.kube/config" ]]; then
        kubectl --kubeconfig="${HOME}/.kube/config" delete configmap "${CONFIG_NAME}"
        kubectl --kubeconfig="${HOME}/.kube/config" create configmap "${CONFIG_NAME}" --from-file="${CONFIG_FILE}"
    else
        kubectl delete configmap "${CONFIG_NAME}"
        kubectl create configmap "${CONFIG_NAME}" --from-file="${CONFIG_FILE}"
    fi

  done
}
