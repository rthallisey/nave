FROM centos:latest
MAINTAINER Vessel Maintainers

COPY MariaDB.repo /etc/yum.repos.d/

RUN yum install -y http://mirror.centos.org/centos-7/7/extras/x86_64/Packages/epel-release-7-6.noarch.rpm
RUN rpm --import http://yum.mariadb.org/RPM-GPG-KEY-MariaDB \
    && rpm --import /etc/pki/rpm-gpg/RPM-GPG-KEY-EPEL-7

RUN yum install -y MariaDB-Galera-server \
                   MariaDB-client \
                   rsync \
                   galera \
                   socat \
                   hostname \
                   expect \
                   percona-xtrabackup \
                   which \
                   socat \
                   tar

RUN mkdir -p /var/log/mariadb \
    && touch /var/log/mariadb/mariadb.log \
    && chown -R mysql: /var/log/mariadb \
    && rm -rf /var/lib/mysql/* \
    && chmod 755 /var/log/mariadb/mariadb.log

COPY mariadb.conf /etc/my.cnf
COPY start.sh security_reset.exp ./

CMD ["./start.sh"]
