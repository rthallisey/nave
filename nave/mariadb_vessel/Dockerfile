FROM ansibleapp/nave-centos-vessel-base:latest
MAINTAINER Ryan Hallisey

RUN mkdir /vessel/mariadb_vessel
COPY __init__.py mariadb_vessel.py /vessel/mariadb_vessel/
COPY init.sh bootstrap-args.sh /

RUN curl -LO https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl

RUN chmod +x ./kubectl
RUN mv ./kubectl /usr/local/bin/kubectl

RUN mkdir -p /var/log/vessel

# Until vessel_v2 init.sh
CMD ["./init.sh"]
#CMD ["/vessel/controller.py", "mariadb"]
