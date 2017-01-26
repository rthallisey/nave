# $1 Cluter size
# $2 source dir
# $3 destination dir
#!/bin/bash

function templates-to-configs {
  for num in $(seq 1 $1); do
    for temp_file in $(ls "${BUILD_ROOT}/kubernetes/${SERVICE}/templates/" | xargs -n 1 basename); do
      local new_file=$(echo $temp_file | sed -e "s/template/$num/")

      # Kubernetes templates
      cp "${BUILD_ROOT}/kubernetes/${SERVICE}/templates"/$temp_file "${BUILD_ROOT}/kubernetes/${SERVICE}"/$new_file
      sed -i "s/{{count}}/$num/g" "${BUILD_ROOT}/kubernetes/${SERVICE}"/$new_file
      sed -i "s/{{container_name}}/${PROJECT}\/${REGISTRY}-${SERVICE}:${TAG}/g" "${BUILD_ROOT}/kubernetes/${SERVICE}"/$new_file

      # SERVICE.conf
      sed "s/{{cluster_name}}/${CLUSTER_NAME}/g" "${CONTAINER_DIR}/${SERVICE}/templates/${SERVICE}_template.conf" > "/etc/nave/${SERVICE}/${SERVICE}-$num.conf"
      sed -i "s/{{count}}/$num/g" "/etc/nave/${SERVICE}/${SERVICE}-$num.conf"
      sed -i "s/{{cluster_addresses}}/${CLUSTER_ADDRESSES}/g" "/etc/nave/${SERVICE}/${SERVICE}-$num.conf"
      sed -i "s/{{db_password}}/${DB_PASSWORD}/g" "/etc/nave/${SERVICE}/${SERVICE}-$num.conf"
    done
  done
}
