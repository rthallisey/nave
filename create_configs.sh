# $1 Cluter size
# $2 source dir
# $3 destination dir
#!/bin/bash

function templates-to-configs {
  for i in $(seq 1 $1); do
    for j in $(ls "${BUILD_ROOT}/kubernetes/${SERVICE}/templates/" | xargs -n 1 basename); do
      f=$(echo $j | sed -e s,template,$i,)
      cp "${BUILD_ROOT}/kubernetes/${SERVICE}/templates"/$j "${BUILD_ROOT}/kubernetes/${SERVICE}"/$f
      sed -i "s,{{count}},$i,g" "${BUILD_ROOT}/kubernetes/${SERVICE}"/$f

      sed -i "s,{{container_name}},${CONTAINER_REG}-${SERVICE}:${TAG},g" "${BUILD_ROOT}/kubernetes/${SERVICE}"/$f

    done
  done
}
