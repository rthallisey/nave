#!/bin/bash

ROOT=$(readlink -f $0)
BUILD_ROOT=`dirname $ROOT`
KUBE_ROOT="${BUILD_ROOT}/kubernetes"
CMD_FILE="${BUILD_ROOT}/kubernetes/mariadb/run-cmd.sh"
BOOTSTRAP_FILE="${BUILD_ROOT}/kubernetes/mariadb/bootstrap-args.sh"

source "${BUILD_ROOT}/default-config.sh"

set -x

function create {
    kubectl create -f $@
}

function replace_cmd {
    sed -i 's/^runuser.*$/sleep 10/' "${CMD_FILE}"
}

function replace_sleep {
    sed -i 's/^sleep.*$/runuser mysql -s "/bin/bash" -c "mysqld_safe ${BOOTSTRAP_ARGS}"' "${CMD_FILE}"
}

function bootstrap-replace {
#    local args="$1"
    sed -i 's/^BOOTSTRAP_ARGS.*$/BOOTSTRAP_ARGS="$1"' "${BOOTSTRAP_FILE}"
}

function corrupt-database {
    echo "Corrupting database"
}

function destroy-galera-cluster {
    echo "Destroying Galera cluster"
    replace_cmd
    kubectl --kubeconfig="${HOME}/.kube/config" delete configmap "run-cmd" -n vessels
    kubectl --kubeconfig="${HOME}/.kube/config" create configmap "run-cmd" --from-file="${CMD_FILE}" -n vessels

    pods=$(kubectl get pods -o name -n vessels | grep -v bootstrap | grep -v vessel | cut -d '/' -f 2)
    for cluster_count in $(seq 1 $CLUSTER_SIZE); do
        pod=$(echo $pods | cut -d ' ' -f "${cluster_count}")
        kubectl --kubeconfig="${HOME}/.kube/config" delete pods $pod -n vessels
    done
}

function recover-galera-cluster {
    echo "Recovering Galera cluster"
    bootstrap-replace '   '
    kubectl --kubeconfig="${HOME}/.kube/config" delete configmap "bootstrap-args"
    kubectl --kubeconfig="${HOME}/.kube/config" create configmap "bootstrap-args" --from-file="${BOOTSTRAP_FILE}" -n vessels

    pods=$(kubectl get pods -o name -n vessels | grep -v bootstrap | grep -v vessel | cut -d '/' -f 2)
    for cluster_count in $(seq 1 $CLUSTER_SIZE); do
        pod=$(echo $pods | cut -d ' ' -f "${cluster_count}")
        kubectl --kubeconfig="${HOME}/.kube/config" delete pods $pod -n vessels
    done
}

function setup-mariadb {
    echo "Setting up Galera cluster"
    replace_sleep
    kubectl --kubeconfig="${HOME}/.kube/config" delete configmap "run-cmd" -n vessels
    kubectl --kubeconfig="${HOME}/.kube/config" create configmap "run-cmd" --from-file="${CMD_FILE}" -n vessels

    bootstrap-replace "--wsrep-new-cluster"
    kubectl --kubeconfig="${HOME}/.kube/config" delete configmap "bootstrap-args" -n vessels
    kubectl --kubeconfig="${HOME}/.kube/config" create configmap "bootstrap-args" --from-file="${BOOTSTRAP_FILE}" -n vessels
    for cluster_count in $(seq 1 $CLUSTER_SIZE); do
        kubectl --kubeconfig="${HOME}/.kube/config" create -f "${KUBE_ROOT}/mariadb/mariadb-service-${cluster_count}.yaml"
        kubectl --kubeconfig="${HOME}/.kube/config" create -f "${KUBE_ROOT}/mariadb/mariadb-pv-${cluster_count}.yaml"
        kubectl --kubeconfig="${HOME}/.kube/config" create -f "${KUBE_ROOT}/mariadb/mariadb-pvc-${cluster_count}.yaml"
        kubectl --kubeconfig="${HOME}/.kube/config" create -f "${KUBE_ROOT}/mariadb/mariadb-pod-${cluster_count}.yaml"
        if [[ $cluster_count -eq 1 ]]; then
            echo "Waiting for Mariadb-1 to start..."
            sleep 10
            bootstrap-replace ""
            kubectl --kubeconfig="${HOME}/.kube/config" delete configmap "bootstrap-args" -n vessels
            kubectl --kubeconfig="${HOME}/.kube/config" create configmap "bootstrap-args" --from-file="${BOOTSTRAP_FILE}" -n vessels
        fi
    done
}

case "$1" in
    'all' )
        setup-mariadb
        destroy-galera-cluster
        recover-galera-cluster
        ;;
    'recover' )
        destroy-galera-cluster
        recover-galera-cluster
        ;;
esac
