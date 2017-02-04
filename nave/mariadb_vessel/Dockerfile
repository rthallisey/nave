FROM ansibleapp/nave-centos-vessel-base:latest
MAINTAINER Ryan Hallisey

RUN mkdir /vessel/mariadb_vessel
COPY __init__.py mariadb_vessel.py /vessel/mariadb_vessel/

CMD ["sleep", "10000"]
#CMD ["controller.py", "mariadb"]
