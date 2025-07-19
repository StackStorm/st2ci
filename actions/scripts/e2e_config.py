#!/usr/bin/env python

import json

from st2actions.runners.pythonrunner import Action

# The end to end tests and package promotion workflows rely on information
# which define various parts of the process:
#
#  - what the current development and release branches.
#  - the stackstorm tests git branch to use for testing.
#  - the st2boostrap script git branch to install st2 on an AWS instance.
#  - which linux distributions are supported for the stackstorm version being tested.
#  - the distrbution path used by packagecloud repository. (e.g. rocky8 uses el/8)
#  - the amazon image and instance type to use for testing packages.
#
# All this information was scattered across numerous packs in rules, action default parameters
# which made it hard to understand what was being done and how workflow variables were being used.
#
# This action acts as a central authority on configuration for all these services so that maintenance
# is easier to reason about across workflows, it avoids repeating data and ensure consistency.
#
# The notion of a "profile" has been defined that will return all information related to the environment:
#      - release                The current StackStorm release available for general use.
#      - release-candidate      StackStorm version available during the release phase use to test before being promoted to "release" status.
#      - development-tested     Development packages that have passed e2e testing and have been promoted to "development-test".
#      - development            Development packages built from "master".
e2ecfg = {
    "secrets": {
        "aws_secret_key": "{{ st2kv.system.aws_secret_key }}",
        "aws_access_key": "{{ st2kv.system.aws_access_key }}",
    },
    "github": {
        "organisation": "StackStorm",
        "repository": "st2",
        "context": "st2/e2e/<% ctx().distro.toLower() %>",
        "url": "https://buildstatus.stackstorm.org/execution/<% ctx().st2.action_execution_id %>",
    },
    "st2": {
        "environment": {
            "release": "v3.8",
            "release-candidate": "v3.8",
            "development-tested": "v3.9",
            "development": "v3.9",
        },
        "version": {
            "v3.9": {
                "st2test_branch": "master",
                "st2bootstrap_branch": "master",
                "package_environment": "development",
                "package_version": "3.9dev",
                "distributions": {
                    "linux": ["ubuntu22", "ubuntu20", "rocky9", "rocky8"],
                    "windows": ["windows2016"],
                },
            },
            "v3.8": {
                "st2test_branch": "v3.8",
                "st2bootstrap_branch": "v3.8",
                "package_environment": "release",
                "package_version": "3.8.1",
                "distributions": {
                    "linux": ["ubuntu20", "ubuntu18", "centos8", "centos7"],
                    "windows": ["windows2016"],
                },
            },
        },
    },
    "packagecloud": {
        "environment": {
            "release": "stable",
            "release-candidate": "staging-stable",
            "development-tested": "unstable",
            "development": "staging-unstable",
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
    },
}


def denormalise_config(cfg):
    """
    Denormalised data to be easily queried from workflows.
    """
    profile = {}
    for profile_name, st2_version in cfg["st2"]["environment"].items():
        profile[profile_name] = {
            "secret": cfg["secrets"],
            "github": cfg["github"],
            "st2": {"version": st2_version},
            "packagecloud": {
                "repo_name": cfg["packagecloud"]["environment"][profile_name],
                "distributions": {},
            },
            "aws": {"region": cfg["aws"]["region"], "distributions": {}},
        }
        profile[profile_name]["st2"].update(cfg["st2"]["version"][st2_version])
        for distro in profile[profile_name]["st2"]["distributions"]["linux"]:
            profile[profile_name]["aws"]["distributions"].update(
                {distro: cfg["aws"]["distro"][distro]}
            )
            profile[profile_name]["packagecloud"]["distributions"].update(
                {distro: cfg["packagecloud"]["distro"][distro]}
            )

    return profile


class e2eConfigAction(Action):
    def run(self, profile=None):
        """
        Returns the configuration for the profile or all profiles
        if no profile name is provided.
        """
        cfg = denormalise_config(e2ecfg)

        if profile:
            cfg = cfg[profile]

        return (True, json.dumps(cfg, indent=4))
