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

"""Mariadb Vessel class

A service_vessel class will describe how a service should run. The class
will cover the follow critera:
    Input:
      - Events
      - Thirdpartyresource data
    Class Definition:
      - Event handeling
          Interprets whether and event should trigger a workflow.
      - Workflows
          Holds service specifc workflows.
"""

import subprocess
import sys

from vessel import Vessel
from thirdpartyresource import ThirdPartyResource

class MariadbVessel(Vessel):

    def __init__(self):
        super(MariadbVessel, self).__init__()
        self.lifecycle_actions = ['deploy', 'recovery']
        self.load_tpr_data()


    def _mariadb_recovery(self, pods):
        """Workflow for recovering mariadb"""

        # need to have one template/pod for each galera node with their
        # own pv/pvc of /var/lib/mysql/grastate.dat

        print pods
        seqno = -1000
        newest_pod = None
        for pod in pods:
            print pod
            # read all volumes that hold /var/lib/mysql/grastate.dat
            p = subprocess.Popen(["kubectl", "exec", pod, "cat",
                                  "/var/lib/mysql/grastate.dat"],
                                 stdout=subprocess.PIPE)

            output = p.stdout.readlines()
            for item in output:
                if "seqno" in item:
                    output = item
                    print output

            output = int(output.split(":")[1])
            # look for the highest positive value
            if (output >= seqno):
                seqno = output
                newest_pod = pod

        # run mysql start --wsrep-new-cluster on the highest seqno
        print "Newest pod and seqno number"
        print "newest database: %s" %newest_pod
        print "seqno: %i" %seqno
        with open('/latest-db/newest-db', 'w') as f:
            f.write(newest_pod+"\n")


    def load_tpr_data(self):
        self.tpr_data = self._service_vessel_tpr_data('mariadb')
        self.tpr = ThirdPartyResource(self.tpr_data)


    def get_tpr_spec(self):
        return self.tpr.vessel_spec


    def get_timestamp(self):
        self.load_tpr_data()
        return self.tpr.timestamp


    def trigger_cluster_event(self, event, pods):
        print event

        # Hack the event handling together.
        # The new design is going to change this around with new class structure.
        if event == "missing pod":
            self._mariadb_recovery(pods)
