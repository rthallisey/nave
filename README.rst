====
Nave
====

Nave makes use of native Kubernetes resources and tools in order to take an
application that is not cloud native and make it function in a cloud native
environment.

Overview
========

- ``ThirdPartyResource`` - `The Kubernetes ThirdPartyResource <http://kubernet
  es.io/docs/user-guide/thirdpartyresources/>`__ is a custom resource tailored
  for an application.
- ``Vessel`` - a vessel is the object that will manage the lifecycle of a
  complex application. A vessel has three parts::
    Resource template
    Dockerfile
    Lifecycle code

Design
======

Nave uses the ThirdPartyResource as a method to store data in etcd.
The vessel is a running pod in the cluster, which will incorporate the etcd
data into how it manages the lifecycle of the complex application.
