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

""" Kubernetes RESTapi class """
# Consider using https://github.com/kubernetes-incubator/client-python

import requests


class Kubernetes():

    def __init__(self):
        self.token = self.get_kube_token()
        self.header = { 'Authorization': 'Bearer %s' %self.token}

    def get_kube_token(self):
        """Kubernetes places a token in every pod that can securly contact the
           rest API
        """
        with open('/var/run/secrets/kubernetes.io/serviceaccount/token', 'r') as token_file:
            token = token_file.readlines()
        return token[0]

    def contact_kube_endpoint(self, url, headers=None, verify=False):
        if headers is None:
            headers = self.header
        return requests.get(url, headers=headers, verify=verify).json()
