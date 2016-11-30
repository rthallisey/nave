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

"""Base class for a Vessel."""

import subprocess


class Vessel(object):

    def __init__(self, data):
        self.data = data

        self.template = self.data.get('vesselSpec')
        self.dependencies = self.template.get('dependencies')
        self.name = self.template.get('serviceName')

        self.lifecycle_actions = ['deploy']
        self.action = self.template.get('action')
        super(Vessel, self).__init__()

    def _kube_client(self, *args):
        kubeargs = ''
        if isinstance(args, list):
            for arg in args:
                kubeargs += arg
        else:
            kubeargs = ''.join(args)
            kubeargs = kubeargs.split(' ')
        subprocess.Popen(kubeargs)

    def _user_action(self, *args, **kwargs):
        """Perform a user directed action.

        Gather and Execute how the user wants to run Kubernetes Vessels.
        """

        pass

    def _spawn_vessels(self, service):
        """Spawn a Vessel"""

        self._kube_client("kubectl create -f"
                          "/etc/nave/%s/%s-vessel.yaml"
                          % service, service)

    def _dependency_chain(self, service):
        """Determine the dependencies of a service"""

        pass

    def _workflow(self):
        """Perform an Lifecycle action for a complex application"""

        if self.action in self.lifecycle_actions:
            self._user_action()
            for service in self.services:
                self._spawn_vessels(service)
        # TODO(rhallisey): Exception & Error handling
        else:
            print("This is not a valid lifecycle action. "
                  "Pick from the list of valid action: %s"
                  % self.lifecycle_actions)

    def get_services(self):
        return self.services

    def deploy(self):
        self._workflow()
