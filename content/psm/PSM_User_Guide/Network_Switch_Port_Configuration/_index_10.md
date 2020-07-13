---
title: "Network Switch Port Configuration"
menu:
  docs:
    parent: "PSM Enterprise Edition User Guide"
weight: 11
categories: [psm]
toc: true
---
## Network Switch Port Configuration
This section details the configuration required on Top-of-Rack (ToR) switches to which DSCs are connected.
Since each DSC card can send and receive traffic over multiple VLANs, DSCs *must* connect to switch ports configured as trunk ports under certain conditions:

- If the Workloads on a host are configured to use an IEEE 802.1q External VLAN, then the corresponding switch port *must* be configured as a trunk port.
- If all the Workloads on a host are sending untagged traffic (External VLAN 0), then the switch port associated with DSC can be configured as an access port.
  
All management traffic (towards an ESXi host or DSC) is expected to be untagged. Any management traffic must be configured with the native VLAN of the network switch. Most network switches use "VLAN 1" as the native VLAN on a trunk port, when not explicitly configured with a native VLAN.  If the management traffic is not using VLAN 1, then adjust the "trunk native vlan" switch port configuration to match the VLAN ID used by management traffic to ensure that it will be transmitted untagged on the links to DSCs.
