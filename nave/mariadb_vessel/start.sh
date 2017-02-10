#!/bin/bash

cp bootstrap-args.sh /bootstrap
./vessel/controller.py mariadb > /var/log/vessel/vessel.log
