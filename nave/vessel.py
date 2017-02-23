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

"""Vessel base class"""

import argparse
import json
import os
import subprocess
import sys

from controller import Controller
from kubernetes import Kubernetes
from thirdpartyresource import ThirdPartyResource


class Vessel(object):
    def __init__(self, service):
        self.state = "None"
        self.identity = "user"
        self.controller = Controller()

        self.load_tpr_data(service)
        self.get_identity()
        self.get_cluster_state()


    def get_identity(self):
        ''' Determine the identity of the vessel creator

        If HOSTNAME is not set, a user is creating the vessel.
        '''
        try:
            self.identity = os.environ['HOSTNAME']
        except KeyError:
            self.identity = "user"


    def get_cluster_state(self):
        '''Get the state of the cluster

        CLUSTER_STATE should only be used when the user creates a vessel.
        Application triggered events should not care about state.

        If CLUSTER_STATE is not set, look at the cluster and determine the
        state.
        '''
        try:
            self.state = os.environ['CLUSTER_STATE']
        except KeyError:
            self.state = "None"


    def load_tpr_data(self, service):
        url = self.controller.base_url + "apis/nave.vessel/v1/namespaces/vessels/" \
              "servicevessels/%s-vessel" %service
        self.tpr = ThirdPartyResource(url)
        self.tpr_data = self.tpr.get_data()


    def get_tpr_spec(self):
        return self.tpr.vessel_spec


    def get_tpr_timestamp(self):
        return self.tpr.timestamp


    def allowed_workflows(self):
        '''Find the current allowed workflows by the user'''
        pass


    def workflow_type(self):
        '''Find the workflow type the use wants executed
        For example, the thirdpartyresource could say execute Ansible workflows
        '''
        pass
