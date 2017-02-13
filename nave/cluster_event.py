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

'''Class providing resources for triggering and tracking cluster events'''

class ClusterEvent(object):

    def cluster_event(self, event):
        """ Cluster event

        When a container that's managed by a vessel starts, it will use an
        init container to reach out to the vessel to see if it's ok to start.

        The vessel is aware of the cluster size.

        Any complex or stateful application will require each service to have its
        own service endpoint.  Therefore, the number of active services in the
        cluster equals the number of service endpoints.

        kube_url + "apis/v1/namespaces/default/endpoints/<service>"

        Otherwise, we can look at the # of pods and compare that to the number
        that should be running in the cluster.

        Two possible event triggers:
          1) Init container calls to Kubernetes to spawn a vessel
          2) User creates a vessel

        Track all events in '/state/application-state'
        """
        #TODO(rhallisey): proper error checking
        with open('/state/application-state', 'a') as f:
            f.write(event + '\n')


    def get_recent_event(self):
        try:
            with open('/state/application-state', 'r') as f:
                recent_item = f.readlines()[-1]
            return recent_item
        except IOError:
            print "No saved events"
            return None

    def failure_event(pod):
        pass
