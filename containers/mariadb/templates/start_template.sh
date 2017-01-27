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
    mysqladmin -uroot -p"{{db_password}}" shutdown
}

mkdir -p /var/lib/mysql
chown -R mysql: /var/lib/mysql

cp /etc/nave/mariadb.conf /etc/my.cnf

if [[ "${!BOOTSTRAP[@]}" ]]; then
    mysql_install_db
    chown -R mysql: /var/lib/mysql
    bootstrap
    exit 0
fi

tail -f /var/log/mariadb/mariadb.log &

#TODO: run this entire script as non root
runuser mysql -s "/bin/bash" -c "mysqld_safe" $BOOTSTRAP_ARGS
