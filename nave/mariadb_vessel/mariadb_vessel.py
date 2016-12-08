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

"""Mariadb Vessel class."""


from service_vessel import ServiceVessel


class MariadbVessel(ServiceVessel):

    def __init__(self, data):
        self.lifecycle_actions = ['deploy', 'recovery']
        super(MariadbVessel, self).__init__(data)

    def _mariadb_recovery(self):
        """Workflow for recovering mariadb"""

        # need to have one template/pod for each galera node with their
        # own pv/pvc of /var/lib/mysql/grastate.dat

        # read all volumes that hold /var/lib/mysql/grastate.dat
        output, error = self._kube_client("kubectl exec mariadb cat "
                                          "/var/lib/mysql/grastate.dat")
        seqno = output
        # look for the highest positive value
        # run /etc/init.d/mysql start --wsrep-new-cluster on the highest seqno

        pass

    def _deploy(self):
        self._run_helm_package()

    def do_action(self):
        if self.action in self.lifecycle_actions:
            if self.action == 'deploy':
                self._deploy()
            elif self.action == 'recovery':
                self._mariadb_recovery()
        else:
            print("%s is not a valid lifecycle action. "
                  "Pick from the list of valid action: %s"
                  % self.action, self.lifecycle_actions)
