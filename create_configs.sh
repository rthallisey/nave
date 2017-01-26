# $1 Cluter size
# $2 source dir
# $3 destination dir
#!/bin/bash

function templates-to-configs {
  for i in $(seq 1 $1); do
    for j in $(ls "${BUILD_ROOT}/kubernetes/${SERVICE}/templates/" | xargs -n 1 basename); do
      f=$(echo $j | sed -e s,template,$i,)
      # Kubernetes templates
      cp "${BUILD_ROOT}/kubernetes/${SERVICE}/templates"/$j "${BUILD_ROOT}/kubernetes/${SERVICE}"/$f
      sed -i "s,{{count}},$i,g" "${BUILD_ROOT}/kubernetes/${SERVICE}"/$f
      sed -i "s,{{container_name}},${CONTAINER_REG}-${SERVICE}:${TAG},g" "${BUILD_ROOT}/kubernetes/${SERVICE}"/$f

      # SERVICE.conf
      sed "s/{{cluster_name}}/${CLUSTER_NAME}/g" "${CONTAINER_DIR}/${SERVICE}/templates/${SERVICE}_template.conf" > "/etc/nave/${SERVICE}/${SERVICE}-$i.conf"
      sed -i "s,{{count}},$i,g" "/etc/nave/${SERVICE}/${SERVICE}-$i.conf"
      sed -i "s/{{cluster_addresses}}/${CLUSTER_ADDRESSES}/g" "/etc/nave/${SERVICE}/${SERVICE}-$i.conf"
      sed -i "s/{{db_password}}/${DB_PASSWORD}/g" "/etc/nave/${SERVICE}/${SERVICE}-$i.conf"

    done
  done
}
