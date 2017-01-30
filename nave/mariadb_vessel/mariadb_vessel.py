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

import sys

from vessel import Vessel
from thirdpartyresource import ThirdPartyResource

class MariadbVessel(Vessel):

    def __init__(self):
        self.tpr_data = self._get_service_vessel('mariadb')
        ThirdPartyResource(self.tpr_data)
        self.lifecycle_actions = ['deploy', 'recovery']

        super(Vessel, self).__init__()

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
