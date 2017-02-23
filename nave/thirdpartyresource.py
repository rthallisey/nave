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

"""ThirdPartyResource class"""

import json

from kubernetes import Kubernetes

class ThirdPartyResource(object):

    def __init__(self, url):
        self.kubernetes = Kubernetes()
        self._read_tpr_data(url)
        self.kind = self.tpr_data.get('kind')
        self.vessel_spec = self.tpr_data.get('vesselSpec')
        self.first_node = self.vessel_spec.get('first_node')
        self.name = self.tpr_data.get('metadata').get('name')
        self.timestamp = self.tpr_data.get('metadata').get('creationTimestamp')

    def _read_tpr_data(url):
        url = url + "?watch=true"
        self.tpr_data = self.kubernetes.contact_kube_endpoint(url)
