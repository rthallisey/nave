#!/usr/bin/env python
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Controller

This script will interact with the Vessel and transfer events to the Vessel as
they happen.  It will be run when the container starts and serves as a daemon.
"""

import argparse
import json
import sys


from kubernetes import Kubernetes
from vessel import Vessel
from mariadb_vessel.mariadb_vessel import MariadbVessel


def parser():
    parser = argparse.ArgumentParser(description='Vessel Client.')

    parser.add_argument("vessel",
                        help='Input which vessel to spawn')
    return parser.parse_args()


def cluster_event(vessel, service):
    """ Cluster event

    When a container that's managed by a vessel starts, it will use an
    init container to reach out to the vessel to see if it's ok to start.

    The vessel is aware of the cluster size.

    Any complex or stateful application will require each service to have its
    own service endpoint.  Therefore, the number of active services in the
    cluster equals the number of service endpoints.

       kube_url + "apis/v1/namespaces/default/endpoints/<service>"

    Otherwise, we can look at the # of pods and compare that to the number
    that should be running in the cluster

    Two possible event triggers:
       1) Init container calls to Kubernetes to spawn a vessel
       2) User creates a vessel
    """
    print "Checking cluster size..."
    cluster_size = len(vessel.service_list(service))

    print "Checking number of pods in the cluster..."
    pod_count = len(vessel.pod_list(service))-1

    if cluster_size > pod_count:
        return 'missing pod'

def main():
    args = parser()
    service = args.vessel

    vessel = Vessel()
    kubernetes = Kubernetes()
    token = kubernetes.token
    vessel_dict = {'mariadb': MariadbVessel()}
    service_vessel = vessel_dict.get(service)

    print "Using ThirdPartyResource with spec: %s" %service_vessel.get_tpr_spec()
    print "Using ThirdPartyResource from: %s" % service_vessel.get_timestamp()

    service_vessel.load_tpr_data()

    # check if an event occured in the cluster
    event = cluster_event(vessel, service)
    if event is not None:
        service_vessel.trigger_cluster_event(event)

if __name__ == '__main__':
    sys.exit(main())
