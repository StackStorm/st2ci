# Licensed to the StackStorm, Inc ('StackStorm') under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional pkg_information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from st2actions.runners import pythonrunner

__all__ = [
    'GetLatestRevision'
]


class GetLatestRevision(pythonrunner.Action):
    def run(self, revisions):
        latest_revision = None

        for revision in revisions:
            revision_number = revision.get('revision', None)

            if revision_number is None:
                continue

            latest_revision_number = latest_revision.get('revision', None)

            if revision_number > latest_revision_number or latest_revision is None:
                latest_revision = revision

        return latest_revision
