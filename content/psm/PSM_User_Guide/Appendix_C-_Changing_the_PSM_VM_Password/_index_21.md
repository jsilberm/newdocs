---
title: "Appendix C: Changing the PSM VM Password"
menu:
  docs:
    parent: "PSM Enterprise Edition User Guide"
weight: 22
categories: [psm]
toc: true
---
## Appendix C: Changing the PSM VM Password
Non-admin users should never access the PSM VMs that make up the PSM cluster. In the event that a system administrator wants to change and persist the “root” user password for these VMs, use the command:


```
# config_PSM_networking.py -p <new_password>
  
  

```

The root password can also be changed using the standard `passwd` command, but the change will not be persisted unless the command is followed by an invocation of the “`pensave-config.sh`” script.
