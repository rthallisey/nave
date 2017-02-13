#!/bin/bash

cp bootstrap-args.sh /bootstrap
./vessel/mariadb_vessel/mariadb_vessel.py > /var/log/vessel/vessel.log
