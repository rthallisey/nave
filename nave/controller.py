#!/usr/bin/env python
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

import argparse
import json
import sys
import urllib2

from vessel import Vessel
from mariadb_vessel.mariadb_vessel import MariadbVessel


def parser():
    parser = argparse.ArgumentParser(description='Vessel Client.')

    parser.add_argument("vessel",
                        help='Input which vessel to spawn')
    return parser.parse_args()


def main():
    args = parser()
    service = args.vessel

    url = 'http://localhost:8080/apis/nave.vessel/v1/namespaces/default/'
    # TODO(rhallisey): error check the response
    # TODO(rhallisey): this can be customized to a different name as long as we
    # check against a list of valid vessels
    if service == 'mariadb':
        response = urllib2.urlopen(url + 'servicevessels/' + service +
                                   '-vessel')

    info = response.read()
    # TODO(rhallisey) JSON error checking
    user_data = json.loads(info)

    if user_data.get('kind') == 'Vessel':
        op = Vessel(user_data)
        op.deploy()

    if user_data.get('kind') == 'ServiceVessel':
        vessel_dict = {'mariadb': MariadbVessel(user_data)}
        service_ves = vessel_dict.get(service)
        service_ves.deploy()

if __name__ == '__main__':
    sys.exit(main())
