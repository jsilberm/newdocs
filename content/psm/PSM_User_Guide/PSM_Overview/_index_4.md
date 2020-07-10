---
title: "PSM Overview"
menu:
  docs:
    parent: "PSM Enterprise Edition User Guide"
weight: 5
categories: [psm]
toc: true
---
## PSM Overview
The Pensando PSM platform is a policy and services manager: a programmable, secure, highly available, comprehensive single point for managing infrastructure policy and functionality for:

- Distributed firewall security
- Telemetry and analytics
- Troubleshooting
- Distributed Service Card (DSC) lifecycle management
- Operations and maintenance: events, alerts, technical support
- Authentication, authorization, and accounting (AAA)
  
The PSM platform is designed to establish and manage consistent policies for thousands of DSCs (refer to the *Pensando Platform Release Notes* for current support limits).
The PSM platform operates as a 3-node quorum-based cluster running on VMs hosted on multiple servers for fault tolerance. A PSM cluster can tolerate the loss of one controller node and continue to maintain full service. The PSM cluster is not involved in datapath operations; if it becomes unreachable, data traffic will continue working seamlessly on disconnected DSC hosts.
Figure 1 is a diagram of the interconnection between the PSM and the DSCs it manages; interactions take place through an IP network.
  
![image alt text](/images/PSM/PSM_User_Guide/PSM_Overview/34b70664441784b72e0fee48767ebc073dcb62b3.png)<div style="text-align:center">
<font size='2'>*Figure 1. PSM/DSC interconnection*
</font>

</div>The PSM employs an *intent-based* configuration management structure, similar to Kubernetes. Any configuration changes are continuously monitored within the PSM until it has been confirmed that the changes have been propagated to all DSCs.
Each DSC is configured with an IP address that is used for communication with its associated PSM over any IP network. This is referred to as its *management address*.
Each DSC runs an agent which constantly watches for incoming configuration changes upon which it must take action. This agent runs within the DSC and is completely transparent to and independent of the host and its operating system.
The PSM resends configuration requests until the desired state is reported back from each DSC, as shown in Figure 2:
  
![image alt text](/images/PSM/PSM_User_Guide/PSM_Overview/831255ab9fbf09ba8313d91957a3ec892e497ca5.png)<div style="text-align:center"><font size='1'>
</font>

<font size='2'>*Figure 2. Working principles of intent-based configuration*
</font>

</div>Intent is expressed in terms of *policies*; the PSM uses an object model to describe the various entities involved in the policies. Objects include *Host objects*, *Workload objects*, and *App objects*. More information can be found in the <ins>PSM Object Model</ins> section.
Figure 3 is a sample topology of two ESXi hosts deploying DSCs connecting to two Top-of-Rack switches.
Notes:

- Management traffic for both the ESXi host and the DSC is untagged and, as such, gets associated by the switch to the native VLAN; such traffic is not subject to policy evaluation. The PSM supports untagged workload uplink traffic. All workload traffic, even if untagged, will be subject to policy enforcement.
- *Micro-segmentation VLANs*  are used on a given ESXi host to enforce traffic isolation and are facilitated by ESXi port groups: each VM is associated to a port group (PG) with its own unique micro-segmentation VLAN (e.g., 10, 20, 30 in figure 3).
- VMs on different hosts can communicate with each other if they share the same external VLAN (or Workload VLAN) that was specified and associated with the Workloads. 
  
![image alt text](/images/PSM/PSM_User_Guide/PSM_Overview/07d540bbfc2386a51cc09d64b2921a7887297aac.png)  
<div style="text-align:center">
<font size='2'>*Figure 3. ESXi host physical interconnection and virtual networking configuration*
</font>
