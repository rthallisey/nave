FROM vessel-base:latest
MAINTAINER Ryan Hallisey

RUN mkdir /mariadb_vessel
COPY __init__.py mariadb_vessel.py /opt/vessel/bin

CMD ["controller.py mariadb"]
