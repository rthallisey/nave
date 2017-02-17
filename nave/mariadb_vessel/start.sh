#!/bin/bash

cp bootstrap-args.sh /bootstrap
kubectl get pods -n vessels |  tail -n +2 | grep -v Terminating | cut -d ' ' -f 1 > hack-pods
./vessel/mariadb_vessel/mariadb_vessel.py &> /var/log/vessel/vessel.log
