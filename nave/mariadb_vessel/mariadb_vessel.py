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

import os
import subprocess
import sys

from vessel import Vessel
from thirdpartyresource import ThirdPartyResource

class MariadbVessel(Vessel):

    def __init__(self):
        super(MariadbVessel, self).__init__()
        self.lifecycle_actions = ['deploy', 'recovery']
        self.load_tpr_data()
        self.get_identity()
        self.get_cluster_state()
        self.status = 0

        self.empty_bootstrap_cmd = 'BOOTSTRAP_ARGS=""'
        self.new_cluster_cmd = 'BOOTSTRAP_ARGS="--wsrep-new-cluster"'


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
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE)
            err = p.stderr.readlines()
            if len(err) != 0:
                print err
                self.status = 1

            output = p.stdout.readlines()
            if len(output) == 0:
                self.status = 1
            else:
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
        try:
            with open('/latest-db/newest-db', 'w') as f:
                f.write(newest_pod+"\n")
        except:
            pass


    def _mariadb_deploy(self):
        """Workflow for deploying mariadb"""

        print "Deploying Mariadb"
        # Returns ['name', 'pod_name']
        name_list = self.name_list('mariadb')
        first_node = self.tpr.first_node

        print "Name_list %s" % name_list
        print "Looking for '%s' to start first" % first_node

        first_pod = None
        for n in name_list:
            if n[0] == first_node:
                first_pod = n[1]
                print "The first service '%s' has pod '%s'" %(first_node, first_pod)

        if first_pod == self.pod:
            self.replace_bootstrap_cmd(self.empty_bootstrap_cmd, self.new_cluster_cmd)
            print "Starting '%s'" % self.pod
            self.status = 0
        elif self.is_running(first_pod) == 'Running':
            self.replace_bootstrap_cmd(self.new_cluster_cmd, self.emtpy_bootstrap_cmd)
            print "'%s' is running. Starting '%s'" %(first_node, self.pod)
            self.status = 0
        else:
            self.status = 1


    def get_identity(self):
        ''' Determine the identity of the vessel creator

        If HOSTNAME is not set, a user is creating the vessel.
        '''
        try:
            self.pod = os.environ['HOSTNAME']
        except KeyError:
            self.pod = "user"

    def get_cluster_state(self):
        '''Get the state of the cluster

        CLUSTER_STATE should only be used when the user creates a vessel.
        Application triggered events should not care about state.

        If CLUSTER_STATE is not set, look at the cluster and determine the
        state.
        '''
        try:
            self.state = os.environ['CLUSTER_STATE']
        except KeyError:
            self.state = "None"


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
        if event == "deploy":
            self._mariadb_deploy()

        return self.status, self.pod


    def replace_bootstrap_cmd(self, old_cmd, new_cmd):
        with open('/bootstrap/bootstrap-args.sh', 'r') as f:
            output = f.read()

        with open('/bootstrap/bootstrap-args.sh', 'w') as f:
            new_cmd = output.replace(old_cmd, new_cmd)
            f.write(new_cmd)
