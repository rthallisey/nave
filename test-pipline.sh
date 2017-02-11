#!/bin/bash

ROOT=$(readlink -f $0)
BUILD_ROOT=`dirname $ROOT`
KUBE_ROOT="${BUILD_ROOT}/kubernetes"

source "${BUILD_ROOT}/default-config.sh"

function create {
    kubectl create -f $@
}

function corrupt-database {
    echo "Corrupting database"
}

function destroy-galera-cluster {
    echo "Destroying Galera cluster"
    pods=$(kubectl get pods -o name -n vessels | grep -v bootstrap | cut -d '/' -f 2)
    for pod in ${pods[@]}; do
        kubectl --kubeconfig="${HOME}/.kube/config" delete pods $pod -n vessels
    done
}

function recover-galera-cluster {
    # Replaced by init containers calling the vessel
    echo "Recovering Galera cluster"

    # Vessel will find newest DB
    kubectl --kubeconfig="${HOME}/.kube/config" create -f "${BUILD_ROOT}/vessels/mariadb/mariadb-vessel.yaml"

    sleep 20
    vessel=$(kubectl get pods -o name -n vessels | grep "vessel" | cut -d '/' -f 2)
    echo $vessel
    kubectl --kubeconfig="${HOME}/.kube/config" logs $vessel -n vessels

    (cd "${HOME}/halcyon-vagrant-kubernetes"
        vagrant ssh-config > /tmp/vagrant-ssh
        awk -v RS= '{print > ("/tmp/kube-" NR)}' /tmp/vagrant-ssh

        i=$(ssh -F /tmp/kube-2 vagrant@kube2 "cat /var/lib/nave/vessel-data/newest-db")
        echo $i
    ) &>/tmp/test
    newest=`cat /tmp/test`

    kubectl --kubeconfig="${HOME}/.kube/config" delete rc mariadb-vessel -n vessels
    service_num=$(echo $newest | cut -f 2 -d '-')
    echo "Setting safe_to_bootstrap in grastate.dat for mariadb-${service_num}"
    (cd "${HOME}/halcyon-vagrant-kubernetes"
        ssh -F /tmp/kube-2 vagrant@kube2 "sudo sed -i 's/safe_to_bootstrap: 0/safe_to_bootstrap: 1/' /var/lib/nave/mariadb-${service_num}/grastate.dat"
    )

    echo "Bootstrapping cluster with pod ${newest}"
    kubectl --kubeconfig="${HOME}/.kube/config" delete pods "${newest}" -n vessels
    sleep 20

    pods=$(kubectl get pods -o name -n vessels | grep -v bootstrap | grep -v vessel | grep -v mariadb-"${service_num}" | cut -d '/' -f 2)
    echo "Rejoining the rest of the pods to the cluster"
    for pod in "${pods[@]}"; do
        kubectl --kubeconfig="${HOME}/.kube/config" delete pods $pod -n vessels
    done
    echo "----------------------"
    echo "  Cluster recovered!  "
    echo "----------------------"
}

function bootstrap-mariadb {
    echo "Bootstrapping up Galera cluster"
    kubectl --kubeconfig="${HOME}/.kube/config" create -f "${KUBE_ROOT}/mariadb/mariadb-service-1.yaml"
    kubectl --kubeconfig="${HOME}/.kube/config" create -f "${KUBE_ROOT}/mariadb/mariadb-pv-1.yaml"
    kubectl --kubeconfig="${HOME}/.kube/config" create -f "${KUBE_ROOT}/mariadb/mariadb-pvc-1.yaml"
    kubectl --kubeconfig="${HOME}/.kube/config" create -f "${KUBE_ROOT}/mariadb/mariadb-bootstrap.yaml"
}

function setup-mariadb {
    echo "Setting up Galera cluster"

    kubectl --kubeconfig="${HOME}/.kube/config" create -f "${KUBE_ROOT}/mariadb/mariadb-pod-1.yaml"
    for cluster_count in $(seq 2 $CLUSTER_SIZE); do
        kubectl --kubeconfig="${HOME}/.kube/config" create -f "${KUBE_ROOT}/mariadb/mariadb-service-${cluster_count}.yaml"
        kubectl --kubeconfig="${HOME}/.kube/config" create -f "${KUBE_ROOT}/mariadb/mariadb-pv-${cluster_count}.yaml"
        kubectl --kubeconfig="${HOME}/.kube/config" create -f "${KUBE_ROOT}/mariadb/mariadb-pvc-${cluster_count}.yaml"
        kubectl --kubeconfig="${HOME}/.kube/config" create -f "${KUBE_ROOT}/mariadb/mariadb-pod-${cluster_count}.yaml"
    done
}

function clean {
    kubectl --kubeconfig="${HOME}/.kube/config" delete job mariadb-bootstrap -n vessels
    for cluster_count in $(seq 1 $CLUSTER_SIZE); do
        kubectl --kubeconfig="${HOME}/.kube/config" delete service "mariadb-${cluster_count}" -n vessels
        kubectl --kubeconfig="${HOME}/.kube/config" delete pv "mariadb-${cluster_count}" -n vessels
        kubectl --kubeconfig="${HOME}/.kube/config" delete pvc "mariadb-${cluster_count}" -n vessels
	kubectl --kubeconfig="${HOME}/.kube/config" delete rc "mariadb-${cluster_count}" -n vessels
    done

    (cd "${HOME}/halcyon-vagrant-kubernetes"
        vagrant ssh-config > /tmp/vagrant-ssh
        awk -v RS= '{print > ("/tmp/kube-" NR)}' /tmp/vagrant-ssh
        ssh -F /tmp/kube-2 vagrant@kube2 "sudo rm -rf /var/lib/nave/*"
    )
}

case "$1" in
    'setup' )
        setup-mariadb
        ;;
    'destroy' )
        destroy-galera-cluster
        ;;
    'recover' )
        recover-galera-cluster
        ;;
    'bootstrap' )
        bootstrap-mariadb
        ;;
    'clean' )
        clean
        ;;
    '-h' )
        echo "test-pipeline.sh"
        echo "This script is designed to test vessels by simulating cluster events."
        echo ""
        echo "          bootstrap   - Bootstrap MariaDB cluster"
        echo "          setup       - Setup a MariaDB Galera cluster"
        echo "          destroy     - Destroy the cluster sending into a damaged state."
        echo "          recover     - Recover from a damaged cluster"
        echo "          clean       - Delete everything from a running cluster"
        echo "          -h          - Help menu"
        ;;
esac
