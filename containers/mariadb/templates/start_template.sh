#!/bin/bash

function boostrap {
    mysqld_safe --wsrep-new-cluster &

    mysql -u root --password="password" -e "GRANT ALL PRIVILEGES ON *.* TO 'root'@'localhost' IDENTIFIED BY 'password' WITH GRANT OPTION;"
    mysql -u root --password="password" -e "GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' IDENTIFIED BY 'password' WITH GRANT OPTION;"
    mysqladmin -uroot -p "password" shutdown
}

if [[ "${!BOOTSTRAP[@]}" ]]; then
    mysql_install_db
    bootstrap
    exit 0
fi

tail -f /var/log/mariadb/mariadb.log &
/usr/bin/mysqld_safe
