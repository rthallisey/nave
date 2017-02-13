FROM centos:latest
MAINTAINER Ryan Hallisey

RUN yum install -y python-requests
RUN mkdir -p vessel
COPY __init__.py cluster_event.py thirdpartyresource.py kubernetes.py controller.py vessel.py /vessel/
