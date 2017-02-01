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
from datetime import datetime
import json
import sys
import time


from vessel import Vessel
from mariadb_vessel.mariadb_vessel import MariadbVessel


def parser():
    parser = argparse.ArgumentParser(description='Vessel Client.')

    parser.add_argument("vessel",
                        help='Input which vessel to spawn')
    return parser.parse_args()


def cluster_event(service_vessel):
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
    """
    print "cluster event"

def compare_timestamp(t1, t2):
    t1 = datetime.strptime(t1, "%Y-%m-%dT%H:%M:%SZ")
    t2 = datetime.strptime(t2, "%Y-%m-%dT%H:%M:%SZ")

    return t1 < t2


def main():
    args = parser()
    service = args.vessel

    vessel_dict = {'mariadb': MariadbVessel()}
    service_vessel = vessel_dict.get(service)
    service_vessel.print_tpr_spec()
    ts_old = service_vessel.get_timestamp()

    while(True):
        # check for newer timestamp (new tpr resource)
        ts_new = service_vessel.get_timestamp()
        if compare_timestamp(ts_new, ts_old):
            print "ThirdPartyResource has been updated. " \
                   "Reloading it's data..."
            service_vessel.load_tpr_data()

        # check if an event occured in the cluster
        event = cluster_event(service)
        if event is not None:
            service_vessel.trigger_cluster_event(event)

        time.sleep(1)
        exit(0)

if __name__ == '__main__':
    sys.exit(main())
