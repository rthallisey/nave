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
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

from kubernetes import Kubernetes

class Vessel(object):

    def __init__(self):
        # Kubernetes has these environment vars set in every container running
        # in the cluster
        self.kube_endpoint = os.getenv("KUBERNETES_SERVICE_HOST")
        self.kube_port = os.getenv("KUBERNETES_PORT_443_TCPORT")
        self.base_url = "https://%s:%s/" % (self.kube_endpoint, self.kube_port)

        self.kubernetes = Kubernetes()
        # Disable HTTPS warnings from request
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

    def _kube_client(self, *args):
        # https://github.com/kubernetes-incubator/client-python

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


    def _get_vessel_version(self):
        # Vessel version endpoint
        # https://<kube_ip_address>:<port>/apis/nave.vessel/

        url = self.base_url + "apis/nave.vessel"
        return self.kubernetes.contact_kube_endpoint(url, self.kubernetes.header)


    def _get_all_vessels(self):
        # All vessels endpoint
        # https://<kube_ip_address>:<port>/apis/nave.vessel/v1/servicevessels/

        url = self.base_url + "apis/nave.vessel/v1/servicevessels"
        return self.kubernetes.contact_kube_endpoint(url, self.kubernetes.header)


    def _service_vessel_tpr_data(self, service):
        # Specific vessel endpoint
        # https://<kube_ip_address>:<port>/apis/nave.vessel/v1/namespaces/default/servicevessels/mariadb-vessel
        url = self.base_url + "apis/nave.vessel/v1/namespaces/default/" \
              "servicevessels/%s-vessel" %service
        return self.kubernetes.contact_kube_endpoint(url, self.kubernetes.header)


    def _get_service_pods(self, service):
        url = self.base_url + "api/v1/namespaces/default/pods"
        print url
        print self.kubernetes.contact_kube_endpoint(url, self.kubernetes.header)
