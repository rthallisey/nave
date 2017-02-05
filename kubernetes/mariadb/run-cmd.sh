#!/bin/bash

runuser mysql -s "/bin/bash" -c "mysqld_safe ${BOOTSTRAP_ARGS}"
