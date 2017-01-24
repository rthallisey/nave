#!/bin/bash

set -x
set -e

function bootstrap {
    mysqld_safe --wsrep-new-cluster &

    while [[ ! -f /var/lib/mysql/mariadb.pid ]]; do
        sleep 3
    done

    ./security_reset.exp
    mysql -u root --password="{{db_password}}" -e "GRANT ALL PRIVILEGES ON *.* TO 'root'@'localhost' IDENTIFIED BY '{{db_password}}' WITH GRANT OPTION;"
    mysql -u root --password="{{db_password}}" -e "GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' IDENTIFIED BY '{{db_password}}' WITH GRANT OPTION;"
    mysqladmin -uroot -p "{{db_password}}" shutdown
}

mkdir -p /var/lib/mysql
chown -R mysql: /var/lib/mysql

tail -f /var/log/mariadb/mariadb.log &

if [[ "${!BOOTSTRAP[@]}" ]]; then
    mysql_install_db
    chown -R mysql: /var/lib/mysql
    bootstrap
    exit 0
fi

/usr/bin/mysqld_safe
