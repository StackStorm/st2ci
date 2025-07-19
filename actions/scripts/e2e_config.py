#!/usr/bin/env python

import json

from st2actions.runners.pythonrunner import Action

from st2client.client import Client
from st2client.models import KeyValuePair

# The end to end tests and package promotion workflows rely on information
# which express the following concepts:
#
#  - the current development and release branches.
#  - the stackstorm tests git branch to use for testing.
#  - the git branch to use when installing the  st2boostrap script to run to install st2 on an AWS instance.
#  - the supported linux distributions for a given version of stackstorm.
#  - the distrbution path used by packagecloud repository. (e.g. rocky8 uses el/8)
#  - the amazon image to use and instance type when testing packages.
#
# All this information was scattered across rules, action default parameters and workflow variables.
#
# This action acts as a central authority on configuration for all these services so that maintenance
# is easier to reason about across workflows, it avoids repeating data and ensures consistency.
#
# The "environment" is the primary key to lookup up related configuration data in the keystore:
#      - stable             The current StackStorm release available for general use.
#      - staging-stable     StackStorm version available during the release phase use to test before being promoted to "release" status.
#      - unstable           Development packages that have passed e2e testing and have been promoted to "unstable".
#      - staging-unstable   Development packages built from "master".

e2ecfg = {
    "github": {
        "organisation": "StackStorm",
        "repository": "st2",
        "context": "st2/e2e/<% ctx().distro.toLower() %>",
        "url": "https://buildstatus.stackstorm.org/execution/<% ctx().st2.action_execution_id %>",  # this dns entry doesn't exist any more. delete/fix?
    },
    "environment": {
        "stable": {"st2": "v3.8", "packagecloud": "stable"},
        "staging-stable": {"st2": "v3.8", "packagecloud": "staging-stable"},
        "unstable": {
            "st2": "v3.9",
            "packagecloud": "unstable",
        },
        "staging-unstable": {"st2": "v3.9", "packagecloud": "staging-unstable"},
    },
    "st2": {
        "v3.9": {
            "st2test": {
                "branch": "master",
            },
            "st2bootstrap": {
                "branch": "master",
            },
            "package_version": "3.9dev",
            "distributions": {
                "linux": ["ubuntu22", "ubuntu20", "rocky9", "rocky8"],
                "windows": ["windows2016"],
            },
        },
        "v3.8": {
            "st2test": {
                "branch": "v3.8",
            },
            "st2bootstrap": {
                "branch": "v3.8",
            },
            "package_version": "3.8.1",
            "distributions": {
                "linux": ["ubuntu20", "ubuntu18", "centos8", "centos7"],
                "windows": ["windows2016"],
            },
        },
    },
    "packagecloud": {
        # Logic was already built on package cloud but mapping maintained to avoid
        # corner case logic in denormalisation code.
        "repo": {
            "stable": "stable",
            "staging-stable": "staging-stable",
            "unstable": "unstable",
            "staging-unstable": "staging-unstable",
        },
        "distro": {
            "ubuntu24": {"package_path": "ubuntu/noble"},
            "ubuntu22": {"package_path": "ubuntu/jammy"},
            "ubuntu20": {"package_path": "ubuntu/focal"},
            "ubuntu18": {"package_path": "ubuntu/bionic"},
            "ubuntu16": {"package_path": "ubuntu/xenial"},
            "ubuntu14": {"package_path": "ubuntu/trusty"},
            "rocky9": {"package_path": "el/9"},
            "rocky8": {"package_path": "el/8"},
            "rhel8": {"package_path": "el/8"},
            "rhel7": {"package_path": "el/7"},
            "rhel6": {"package_path": "el/6"},
            "centos8": {"package_path": "el/8"},
            "centos7": {"package_path": "el/7"},
            "centos6": {"package_path": "el/6"},
        },
    },
    "aws": {
        "region": "us-west-2",
        "distro": {
            "windows2016": {"default": {"id": "ami-061967ec99026bdc1", "type": "t2.small"}},
            "ubuntu24": {"default": {"id": "ami-0a4435b54107f9c9f", "type": "c5.large"}},
            "ubuntu22": {"default": {"id": "ami-07ceaccc0c1916f5f", "type": "c5.large"}},
            "ubuntu20": {"default": {"id": "ami-07182692443fccde1", "type": "c5.large"}},
            "ubuntu18": {"default": {"id": "ami-0bbe6b35405ecebdb", "type": "t2.small"}},
            "ubuntu16": {"default": {"id": "ami-8803e0f0", "type": "t2.small"}},
            "ubuntu14": {"default": {"id": "ami-038a82c53a4545bb5", "type": "t2.small"}},
            "rocky9": {"default": {"id": "ami-08f2642bb132b988c", "type": "c5.large"}},
            "rocky8": {"default": {"id": "ami-0f74cc83310468775", "type": "c5.large"}},
            "rhel8": {"default": {"id": "ami-087c2c50437d0b80d", "type": "c5.large"}},
            "rhel7": {"default": {"id": "ami-9fa343e7", "type": "c4.large"}},
            "rhel6": {"default": {"id": "ami-0b4704d80e01f7948", "type": "c4.large"}},
            "centos8": {"default": {"id": "ami-0155c31ea13d4abd2", "type": "c5.large"}},
            "centos7": {"default": {"id": "ami-3ecc8f46", "type": "c4.large"}},
            "centos6": {"default": {"id": "ami-e9503589", "type": "c4.large"}},
        },
        "subnet": {
            "staging": "subnet-b7b7aec0",
            "sandbox": "subnet-0e4e9179",
            # Use "public" if you want node to be available on public internet. Set up Elastic IP manually.
            "public": "subnet-4d73bc3a",
            "production": "subnet-4e73bc39",
        },
    },
}


def denormalise_config(client, environment):
    """
    Denormalised data to be easily queried from workflows.
    """
    # Fetch keys from keystore
    env = client.keys.get_by_name(name="environment")
    st2 = client.keys.get_by_name(name="st2")
    github = client.keys.get_by_name(name="github")
    packagecloud = client.keys.get_by_name(name="packagecloud")
    aws = client.keys.get_by_name(name="aws")

    st2_version = env[environment]["st2"]
    packagecloud_repo = env[environmanet]["packagecloud"]
    profile = {
        "env": environment,
        "st2": st2[st2_version],
    }
    profile["st2"]["version"] = st2_version
    # resolve package cloud and aws information per distribution
    for distro in profile["st2"]["distributions"]["linux"]:
        linux_distro = {
            "name": distro,
            "packagecloud": packagecloud["distro"][distro],
            "aws": aws["distro"][distro],
        }

    return profile


class e2eConfigAction(Action):
    def run(self, environment=None, kv_update=False):
        """
        Manage StackStorm ci/cd configuration in the K/V datastore.
        environment: Return normalised configuration for a given envrionment to simplify writing workflows.
        kv_update: Update the k/v with the scripts internal data.
        """
        client = Client()

        if kv_update:
            for k, v in e2ecfg.items():
                client.keys.update(KeyValuePair(name=k, value=json.dumps(v)))

        if environment:
            # Normalised configuration read from the kv/store
            return (True, denormalise_config(client, environment))

        return True
