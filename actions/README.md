## Workflow execution samples

### End-to-end Tests ###

```
st2 run --async st2ci.st2_pkg_e2e_test hostname=st2-pkg-staging-stable-u16 distro=UBUNTU16 pkg_env=staging release=stable version={{st2kv.system.st2_this_release}} chatops=true
st2 run --async st2ci.st2_pkg_e2e_test hostname=st2-pkg-staging-stable-u18 distro=UBUNTU18 pkg_env=staging release=stable version={{st2kv.system.st2_this_release}} chatops=true
st2 run --async st2ci.st2_pkg_e2e_test hostname=st2-pkg-staging-stable-u20 distro=UBUNTU20 pkg_env=staging release=stable version={{st2kv.system.st2_this_release}} chatops=true
st2 run --async st2ci.st2_pkg_e2e_test hostname=st2-pkg-staging-stable-el7 distro=RHEL7 pkg_env=staging release=stable version={{st2kv.system.st2_this_release}} chatops=true
st2 run --async st2ci.st2_pkg_e2e_test hostname=st2-pkg-staging-stable-el8 distro=RHEL8 pkg_env=staging release=stable version={{st2kv.system.st2_this_release}} chatops=true
```

### End-to-End Upgrade Tests ###

```
st2 run --async st2ci.st2_pkg_upgrade_e2e_test hostname=st2-pkg-upgrade-staging-stable-u20 distro=UBUNTU20 pkg_env=staging release=stable upgrade_from_version={{st2kv.system.st2_prev_release}} upgrade_to_version={{st2kv.system.st2_this_release}} chatops=true
st2 run --async st2ci.st2_pkg_upgrade_e2e_test hostname=st2-pkg-upgrade-staging-stable-u18 distro=UBUNTU18 pkg_env=staging release=stable upgrade_from_version={{st2kv.system.st2_prev_release}} upgrade_to_version={{st2kv.system.st2_this_release}} chatops=true
st2 run --async st2ci.st2_pkg_upgrade_e2e_test hostname=st2-pkg-upgrade-staging-stable-u16 distro=UBUNTU16 pkg_env=staging release=stable upgrade_from_version={{st2kv.system.st2_prev_release}} upgrade_to_version={{st2kv.system.st2_this_release}} chatops=true
st2 run --async st2ci.st2_pkg_upgrade_e2e_test hostname=st2-pkg-upgrade-staging-stable-el7 distro=RHEL7 pkg_env=staging release=stable upgrade_from_version={{st2kv.system.st2_prev_release}} upgrade_to_version={{st2kv.system.st2_this_release}} chatops=true
st2 run --async st2ci.st2_pkg_upgrade_e2e_test hostname=st2-pkg-upgrade-staging-stable-el8 distro=RHEL8 pkg_env=staging release=stable upgrade_from_version={{st2kv.system.st2_prev_release}} upgrade_to_version={{st2kv.system.st2_this_release}} chatops=true
```
