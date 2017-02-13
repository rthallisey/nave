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

"""Controller class for Vessels

Common functions that will gather information about the cluster
"""

import os

import subprocess
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

from kubernetes import Kubernetes

class Controller():

    def __init__(self):
        # Kubernetes has these environment vars set in every container running
        # in the cluster
        self.kube_endpoint = os.getenv("KUBERNETES_SERVICE_HOST")
        self.kube_port = os.getenv("KUBERNETES_PORT_443_TCP_PORT")
        self.base_url = "https://%s:%s/" % (self.kube_endpoint, self.kube_port)

        self.kubernetes = Kubernetes()
        # Disable HTTPS warnings from request
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

    def _kube_client(self, *args):
        # Consider using the kubernetes python client
        # https://github.com/kubernetes-incubator/client-python
        pass


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
        # https://<kube_ip_address>:<port>/apis/nave.vessel/v1/namespaces/vessels/servicevessels/mariadb-vessel
        url = self.base_url + "apis/nave.vessel/v1/namespaces/vessels/" \
              "servicevessels/%s-vessel" %service
        return self.kubernetes.contact_kube_endpoint(url, self.kubernetes.header)


    def service_list(self, service):
        url = self.base_url + "api/v1/namespaces/vessels/endpoints"
        k = self.kubernetes.contact_kube_endpoint(url, self.kubernetes.header)['items']
        if k is None:
            return []
        m = filter(lambda u : (service in u and 'vessel' not in u),
                   map(lambda v :  v['metadata']['name'], k))
        print "%s Services: %s" %(len(m), m)
        self.services = m
        return m


    def pod_list(self, service):
        url = self.base_url + "api/v1/namespaces/vessels/pods"
        k = self.kubernetes.contact_kube_endpoint(url, self.kubernetes.header)['items']
        if k is None:
            return []
        m = filter(lambda u : (service in u and 'bootstrap' not in u
                               and 'vessel' not in u),
                   map(lambda v :  v['metadata']['name'], k))
        print "%s Pods: %s" %(len(m), m)
        return m


    def name_list(self, service):
        url = self.base_url + "api/v1/namespaces/vessels/pods"
        k = self.kubernetes.contact_kube_endpoint(url, self.kubernetes.header)['items']
        if k is None:
            return []

        m = []
        for item in k:
            # The bootstrap resource is a job. It does node have the field 'ownerReferences'
            try:
                m.append((item['metadata']['ownerReferences'][0]['name'], item['metadata']['name']))
            except:
                pass

        print "Names: %s" % m
        return m


    def is_running(self, pod):
        '''Check if a pod is running'''
        url = self.base_url + "api/v1/namespaces/vessels/pods/" + pod
        k = self.kubernetes.contact_kube_endpoint(url, self.kubernetes.header)
        if k is None:
            return None
        return k['status']['phase']
