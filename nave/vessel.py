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

"""Base class for a Vessel

Common functions that will serve all Vessels
"""

import os
import subprocess
import urllib2

class Vessel(object):

    def __init__(self):
        self._get_kube_token()
        self.kube_endpoint = os.getenv("KUBERNETES_SERVICE_HOST")
        self.kube_port = os.getenv("KUBERNETES_PORT_443_TCPORT")

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

        p = subprocess.Popen(kubeargs, stdout=subprocess.PIPE)
        out, err = p.communicate()
        return out, err

    def _get_kube_token(self):
        """Kubernetes places a token in every pod that can securly contact the
           rest API
        """
        with open('/var/run/secrets/kubernetes.io/serviceaccount/token', 'r') as kube_token:
            self.kube_token = content_file.read()

    def _contact_kube_endpoint(self, addr):
        return requests.get(url, headers=headers, verify=False).json()

    def _get_vessel_version(self):
        # Vessel version endpoint
        # https://<kube_ip_address>:6443/apis/nave.vessel/

        url = "https://%s:%s/apis/nave.vessel" % (self.kube_endpoint, self.kube_port)
        self.vessel_version = self.contact_kube_endpoint(url)

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
