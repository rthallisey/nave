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

"""Service Vessel class"""

from vessel import Vessel


class ServiceVessel(Vessel):

    def __init__(self):
        super(ServiceVessel, self).__init__()

    def _helm_client(self, *args):
        helm_args = ''
        if isinstance(args, list):
            for arg in args:
                helm_args += arg
        else:
            helm_args = ''.join(args)
            helm_args = helm_args.split(' ')
        subprocess.Popen(helm_args)

    def _database_action(self):
        """Register a service's user and password in the database"""

        pass

    def _run_helm_package(self):
        """Execute a Helm package for a service"""

        self._helm_client("helm install --name %s %s" % self.name, service)

    def _get_all_vessels(self):
        # All vessels endpoint
        # https://<kube_ip_address>:6443/apis/nave.vessel/v1/servicevessels/

        url = "https://%s:%s/apis/nave.vessel/v1/servicevessels" % (self.kube_endpoint, self.kube_port)
        return self.contact_kube_endpoint(url)

    def _get_service_vessel(self, service):
        # Specific vessel endpoint
        # https://<kube_ip_address>:6443/apis/nave.vessel/v1/namespaces/default/servicevessels/mariadb-vessel

        url = "https://%s:%s/apis/nave.vessel/v1/namespaces/default/" \
              "servicevessels/%s-vessel" % (self.kube_endpoint,
                                            self.kube_port,service)
        return self.contact_kube_endpoint(url)
