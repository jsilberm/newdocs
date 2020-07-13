---
title: "Appendix A: PSM Authentication Bootstrap"
menu:
  docs:
    parent: "PSM Enterprise Edition User Guide"
weight: 20
categories: [psm]
toc: true
---
## Appendix A: PSM Authentication Bootstrap
The PSM’s Authentication subsystem requires a bootstrapping, involving the following steps:

1. Create the “default” tenant.
1. Create the “AdminRoleBinding” object.
1. Create the “AuthenticationPolicy” object.
1. Create the default “admin” User object.
1. Post the “AuthBootstrapComplete” status to the Cluster object.
  
Validation can be achieved either by logging in to the GUI or via Postman as the “admin” user.
These steps are automated by the `bootstrap_PSM.py` utility, which should be used for this process. This appendix is included for informational purposes only.

