# $1 Cluter size
# $2 source dir
# $3 destination dir
#!/bin/bash

function build-kube-resources {
  for temp_file in $(ls "${BUILD_ROOT}/kubernetes/${SERVICE}/templates/" | xargs -n 1 basename); do
    local new_file=$(echo $temp_file | sed -e "s/template/$num/")

    # Kubernetes templates
    cp "${BUILD_ROOT}/kubernetes/${SERVICE}/templates"/$temp_file "${BUILD_ROOT}/kubernetes/${SERVICE}"/$new_file
    sed -i "s/{{count}}/$num/g" "${BUILD_ROOT}/kubernetes/${SERVICE}"/$new_file
    sed -i "s/{{container_name}}/${PROJECT}\/${REGISTRY}-${SERVICE}:${TAG}/g" "${BUILD_ROOT}/kubernetes/${SERVICE}"/$new_file
  done
}

function build-configs {
  for num in $(seq 1 $CLUSTER_SIZE); do

    # Create Kubernetes Resources
    build-kube-resources

    # Create $SERVICE.conf
    local config_file="${CONFIG_ROOT}/${SERVICE}-${num}/${SERVICE}.conf"

    mkdir -p "${CONFIG_ROOT}/${SERVICE}-${num}"
    sed "s/{{cluster_name}}/${CLUSTER_NAME}/g" "${CONTAINER_DIR}/${SERVICE}/templates/${SERVICE}_template.conf" > $config_file
    sed -i "s/{{count}}/${num}/g" $config_file
    sed -i "s/{{cluster_addresses}}/${CLUSTER_ADDRESSES}/g" $config_file
    sed -i "s/{{db_password}}/${DB_PASSWORD}/g" $config_file

    # Create Kubernetes configmaps
    kubectl --kubeconfig="${HOME}/.kube/config" create configmap "${SERVICE}-${num}" --from-file=$config_file
  done
}
