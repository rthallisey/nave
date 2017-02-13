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

"""Mariadb Vessel class

A service_vessel class will describe how a service should run. The class
will cover the follow critera:
    Input:
      - Cluster Data
      - Thirdpartyresource data
    Class Definition:
      - Event handling
          Interprets whether and event should trigger a workflow.
      - Workflows
          Holds service specifc workflows.
"""

import os
import subprocess
import sys

sys.path.insert(1, os.path.join(sys.path[0], '..'))

from cluster_event import ClusterEvent
from vessel import Vessel


class MariadbVessel(Vessel):

    def __init__(self):
        super(MariadbVessel, self).__init__('mariadb')
        self.lifecycle_actions = ['deploy', 'recovery']
        self.failure = False
        self.empty_bootstrap_cmd = 'BOOTSTRAP_ARGS=""'
        self.new_cluster_cmd = 'BOOTSTRAP_ARGS="--wsrep-new-cluster"'
        self.event = ClusterEvent()


    def _mariadb_lights_out_recovery(self):
        """Workflow for recovering mariadb"""

        pods = self.controller.pod_list('mariadb')
        print 'Active MariaDB pods in the cluster: %s' % pods

        seqno = -1000
        newest_pod = None
        for pod in pods:
            print pod

            # Read all volumes that hold /var/lib/mysql/grastate.dat
            p = subprocess.Popen(["kubectl", "exec", pod, "cat",
                                      "/var/lib/mysql/grastate.dat"],
                                      stdout=subprocess.PIPE,
                                      stderr=subprocess.PIPE)
            err = p.stderr.readlines()
            if len(err) != 0:
                print err
                self.failure = True

            output = p.stdout.readlines()
            if len(output) == 0:
                self.failure = True
            else:
                for item in output:
                    if "seqno" in item:
                        output = item
                        print output

                output = int(output.split(":")[1])
                # Look for the highest positive value
                if (output >= seqno):
                    seqno = output
                    newest_pod = pod

        # Run mysql start --wsrep-new-cluster on the highest seqno
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
        # Returns ['name', 'pod_name']
        name_list = self.controller.name_list('mariadb')
        first_node = self.tpr.first_node
        first_pod = None

        print "Name_list %s" % name_list
        print "Looking for '%s' to start first" % first_node

        for n in name_list:
            if n[0] == first_node:
                first_pod = n[1]
                print "The first service '%s' has the pod name: '%s'" %(first_node, first_pod)

        if first_pod == self.identity:
            print "Starting '%s'" % self.identity
            self.replace_bootstrap_cmd(self.empty_bootstrap_cmd, self.new_cluster_cmd)
            self.failure = False
        elif self.controller.is_running(first_pod) == 'Running':
            print "'%s' is running. Starting '%s'" %(first_node, self.identity)
            self.replace_bootstrap_cmd(self.new_cluster_cmd, self.empty_bootstrap_cmd)
            self.failure = False
        else:
            self.failure = True


    def replace_bootstrap_cmd(self, old_cmd, new_cmd):
        print "Replacing bootstrap_cmd %s with %s" %(old_cmd, new_cmd)
        with open('/bootstrap/bootstrap-args.sh', 'r') as f:
            output = f.read()

        with open('/bootstrap/bootstrap-args.sh', 'w') as f:
            new_cmd = output.replace(old_cmd, new_cmd)
            f.write(new_cmd)


    def cluster_status(self):
        print "Checking cluster size..."
        cluster_size = len(self.controller.service_list('mariadb'))

        print "Checking number of pods in the cluster..."
        pod_list = self.controller.pod_list('mariadb')

        running_pods = 0
        for p in pod_list:
            if self.controller.is_running(p) == 'Running':
                running_pods += 1

        event = self.event.get_recent_event()
        if event is None:
            print "Deploying Mariadb"
            self._mariadb_deploy()
            self.event.cluster_event('deploy')
        elif running_pods == 0:
            print "Mariadb Lights Out Recovery"
            self._mariadb_lights_out_recovery()
            self.event.cluster_event('lights out recovery')
        elif cluster_size < pod_list:
            print "Scaling MariaDB cluster"
            self._mariadb_deploy()
            self.event.cluster_event('scale')


def main():

    # print "Using ThirdPartyResource with spec: %s" %self.get_tpr_spec()
    # print "Using ThirdPartyResource from: %s" % self.get_timestamp()
    # self.load_tpr_data()

    vessel = MariadbVessel()
    vessel.cluster_status()


if __name__ == '__main__':
    sys.exit(main())
