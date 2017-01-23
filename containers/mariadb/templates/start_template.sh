#!/bin/bash

function boostrap {
    mysqld_safe --wsrep-new-cluster &

    mysql -u root --password="{{db_password}}" -e "GRANT ALL PRIVILEGES ON *.* TO 'root'@'localhost' IDENTIFIED BY '{{db_password}}' WITH GRANT OPTION;"
    mysql -u root --password="{{db_password}}" -e "GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' IDENTIFIED BY '{{db_password}}' WITH GRANT OPTION;"
    mysqladmin -uroot -p "{{db_password}}" shutdown
}

if [[ "${!BOOTSTRAP[@]}" ]]; then
    mysql_install_db
    bootstrap
    exit 0
fi

/usr/bin/mysqld_safe
