## Workflow execution samples

1. Upgrade e2e test Workflow

```
 st2 run st2ci.st2_pkg_upgrade_e2e_test hostname=lk-pkg-upgrade-testing-el7-001 distro=RHEL7 upgrade_from_version=1.4.0 upgrade_to_version=1.5.0 role=cislave enterprise=true enterprise_key=<redacted> -a
```
