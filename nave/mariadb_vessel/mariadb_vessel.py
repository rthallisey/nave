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
        self.empty_bootstrap_cmd = 'BOOTSTRAP_ARGS=""'
        self.new_cluster_cmd = 'BOOTSTRAP_ARGS="--wsrep-new-cluster"'
        self.event = ClusterEvent()
        self.local_owner = self.controller.get_owner(self.identity)
        self.owner_list = self.controller.owner_list('mariadb')


    def _mariadb_lights_out_recovery(self):
        """Workflow for recovering mariadb"""
        seqno = -1000
        newest_owner = None
        newest_pod = None

        print "Sharing local grastate.dat with the cluster"
        # Share local grastate.dat with the cluster
        with open('/var/lib/mysql/grastate.dat', 'r') as t:
            grastate = t.read()
        with open('/vessel-shared/grastate-%s' %self.local_owner, 'w') as f:
            f.write(grastate)

        for owner, pod in self.owner_list:
            print pod

            try:
                # Read stored files in vessel-shared to see different states of the cluster
                with open('/vessel-shared/grastate-' + owner, 'r') as f:
                    info = f.readlines()
            except IOError:
                return True

            for item in info:
                if "seqno" in item:
                    output = item
                    print output

                    output = int(output.split(":")[1])
                    # Look for the highest positive value
                    if (output >= seqno):
                        seqno = output
                        newest_owner = owner
                        newest_pod = pod

        # Run mysql start --wsrep-new-cluster on the highest seqno
        print "Newest owner and seqno number"
        print "newest database: %s" %newest_owner
        print "seqno: %i" %seqno

        if self.local_owner is newest_owner:
            print "Starting '%s' first" % self.local_owner
            with open('/var/lib/mysql/grastate.dat', 'r') as f:
                info = f.readlines()

            # Replace safe_to_bootstrap
            with open('/var/lib/mysql/grastate.dat', 'w') as t:
                t.write(info.replace('safe_to_bootstrap: 0', 'safe_to_bootstrap: 1'))
            return False
        elif self.controller.is_running(newest_pod):
            print "The newest database is running in pod '%s'. Starting '%s'" %(newest_pod, self.local_owner)
            return False
        else:
            print "The newest database in pod '%s' hasn't started yet. Restarting." % newest_pod
            return False


    def _mariadb_deploy(self):
        """Workflow for deploying mariadb"""
        first_node = self.tpr.first_node
        first_pod = None

        print "Looking for '%s' to start first" % first_node

        for n in self.owner_list:
            if n[0] == first_node:
                first_pod = n[1]
                print "The first service '%s' has the pod name: '%s'" %(first_node, first_pod)

        if first_pod == self.identity:
            self.replace_bootstrap_cmd(self.empty_bootstrap_cmd, self.new_cluster_cmd)
            print "Starting '%s'" % self.identity
            return False
        elif self.controller.is_running(first_pod) == 'Running':
            self.replace_bootstrap_cmd(self.new_cluster_cmd, self.empty_bootstrap_cmd)
            print "'%s' is running. Starting '%s'" %(first_node, self.identity)
            return False
        else:
            return True

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
            #TODO: Make error handling more obvious
            # if something returns true, that doesn't usually mean it failed..
            if self._mariadb_deploy():
                return True
            self.event.cluster_event('deploy')
            return False
        elif running_pods == 0:
            print "Mariadb Lights Out Recovery"
            if self._mariadb_lights_out_recovery():
                return True
            self.event.cluster_event('lights-out-recovery')
            return False
        elif cluster_size < pod_list:
            print "Scaling MariaDB cluster"
            if self._mariadb_deploy():
                return True
            self.event.cluster_event('scale')


def main():

    # print "Using ThirdPartyResource with spec: %s" %self.get_tpr_spec()
    # print "Using ThirdPartyResource from: %s" % self.get_timestamp()
    # self.load_tpr_data()

    vessel = MariadbVessel()
    failure = vessel.cluster_status()
    if failure:
        sys.exit(1)

if __name__ == '__main__':
    sys.exit(main())
