---
title: "Initial Deployment Workflow: High-Level Overview"
menu:
  docs:
    parent: "PSM Enterprise Edition User Guide"
weight: 7
categories: [psm]
toc: true
---
## Initial Deployment Workflow: High-Level Overview
This is an outline of the steps necessary for initial deployment of a PSM cluster and its associated DSC-equipped hosts. Detailed steps are provided further below in this document; also refer to the *Enterprise PSM Best Practices* document for further guidance on configuration.

- <font size='2'>Install the PSM</font>
       - Install the PSM software on either an ESX-based or KVM-based 3-node cluster. 
       - Configure the PSM using the `bootstrap_PSM.py` utility.
       - Save a copy of the DSC security token.
       - Set the PSM user authentication policy, and create PSM users with appropriate roles.
- <font size='2'>Network Switch Port Configuration</font>
       - Configure the top-of-rack switch ports connecting to DSC uplinks.
- <font size='2'>Host Configuration</font><font size='2'></font>For each host:
       - Download and install DSC software appropriate for the host’s OS, which will include device drivers and a CLI management utility (`penctl` for Linux/Windows,` esx-pencli` for ESXi)
       - Associate each DSC to the PSM, either from its host or via DHCP.
       - Plan for one additional IP address allocated to each DSC as a management interface, configured either from its host or via DHCP.
       - Admit the DSC into its PSM cluster.  The PSM can be configured to do this automatically.
       - (optional) Create a “Host” object on the PSM corresponding to the admitted DSC.
- <font size='2'>Creat</font><font size='2'>ing</font><font size='2'> and Manage Network Policies</font>
       - Create “Workload” objects corresponding to each VM instance.
       - (optional) Create “App” objects, corresponding to network services.
       - Create and manage policies corresponding to various features such as flow export and firewall rules and permissions between Workloads and Apps.
  
Installation of the PSM cluster is a one-time activity; other procedures may be performed during initial installation, but will also be part of the standard operation of the PSM, performed as more hosts, users, and policies are added.
