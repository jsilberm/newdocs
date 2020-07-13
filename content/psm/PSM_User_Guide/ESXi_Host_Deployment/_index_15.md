---
title: "ESXi Host Deployment"
menu:
  docs:
    parent: "PSM Enterprise Edition User Guide"
weight: 16
categories: [psm]
toc: true
---
## ESXi Host Deployment
This section details the steps required to configure DSC services on ESXi hosts to operate on traffic among VMs running on the same host. Please refer to the “ESXi Driver” section of the Pensando *DSC-25 Distributed Services Card User Guide* for detailed instructions on installing the driver.
### VMware vCenter Integration
The PSM can use the vCenter API to perform necessary network configurations on ESXi hosts and retrieve information on the host itself and the workloads running on it. Integrating an ESXi host in the Pensando platform requires operations on both the PSM (usually performed by the network administrator), and vCenter (usually performed by the compute administrator), according to the workflow presented below.
#### Underlying Principles
Pensando uses the port group's VLAN assignment (termed as micro-segmentation VLAN) to ensure inter-VM traffic goes through the DSC before it is forwarded to its destination, when the DSC is assigned to a profile that is associated with the Virtualized Deployment Target. The destination can be a VM on the same or remote host. 
In order to achieve this, a different micro-segmentation VLAN is assigned to each vNIC attached to a vDS switch, as shown in Figure 32; this ensures that the Pensando vDS switch does not allow direct VM to VM communication. This configuration is needed to ensure that all VM-to-VM communications are subject to micro-segmentation policy enforcement by the DSC. Figure 32 shows various possible traffic patterns between VMs.
  
![image alt text](/images/PSM/PSM_User_Guide/ESXi_Host_Deployment/55271b6961fad59d828b8c073ef7b82ca65a8649.png)
<div style="text-align:center"><font size='2'>*Figure 32. DSC access to*
</font> 
<font size='2'>*VM-to-VM traffic*
</font> 

</div>
The following steps are necessary to achieve the required configuration:

- Unique micro-segmentation (or Micro-seg) VLAN is allocated for each vNIC
- Allocation of VLANs, (Micro-seg and external) is centrally managed by PSM, and pushed to DSC nodes via REST API
- DSC translates micro-segmentation VLAN to external port group on the uplink
- Micro-segmentation policy is by whitelist: no communication within or between host VMs is allowed unless expressly permitted by policy on the DSC
  
#### Configuration Workflow
PSM and ESXi configuration requires the steps as listed below and graphically depicted in Figure 33; some of these steps require action by the network administrator or virtual infrastructure administrator, while others are automatically carried out by the PSM, leveraging the vCenter API.
  
![image alt text](/images/PSM/PSM_User_Guide/ESXi_Host_Deployment/eb24a47c00aaa63213c2a13987b2ea82561c6294.png)

<div style="text-align:center"><font size='2'>*Figure 33. vCenter integration workflow*
</font>

</div>

1. From the PSM, Step 1 blue: navigate to the Orchestrator menu and select the “vCenter” function to register to a vCenter server, which requires providing the IP address (URI) and login credentials (“username/password”) of the vCenter server, as shown in Figure 34, or a certificate to be used for authentication.
  
![image alt text](/images/PSM/PSM_User_Guide/ESXi_Host_Deployment/aad06ff393b2c3579b930b2ba7826355700b31f3.png)  
<div style="text-align:center">
<font size='2'>*Figure 34. Registering a vCenter server*
</font>

</div>

       1. Step 1 red: A vDS is automatically created by the PSM within vCenter with the form #Pen-vDS-<suffix> (where <suffix> is the DC name) using the vCenter API.
1. From the PSM, Step 2 blue: create networks (VLANs) that are associated to the vCenter Server and to a Data Center, using the screen shown in Figure 35.
  
![image alt text](/images/PSM/PSM_User_Guide/ESXi_Host_Deployment/a1473198046abf52a0dab20caa08e9fd89ae4eb7.png)  
<div style="text-align:center">
<font size='2'>*Figure 35. Creating Network objects, with corresponding VLANs*
</font>

</div>

       1. Step 2 red: The networks will become port groups of the vDS and will be visible within vCenter.
       1. In the PSM, each Network will become an “external” VLAN that will be used for packets traveling between the DSC and the ToR switch.
1. From vCenter, Step 3 blue: the virtual server admin adds ESXi host to Pensando vDS and associated DSC ports as uplinks to vDS
       1. Step 3 red: once that is done, the PSM auto-creates a Host object based upon the ESXi hostname and associates it to the DSC, as shown in Figure 36. This automatic action is triggered by the Pensando vDS configuration in vCenter.
  

  
![image alt text](/images/PSM/PSM_User_Guide/ESXi_Host_Deployment/51f5823ba495937f68ddba493de518b2dd21058d.png)
<div style="text-align:center"><font size='2'>*Figure 36. Host Overview with auto-created Host object*
</font>

</div>

1. From vCenter, Step 4 blue: the virtual  server admin creates a VM and associates its network interface to a PG created in the Pensando vDS.
       1. Step 4 red: as a result of this configuration change in vCenter, the PSM automatically creates a Workload object:
           1. MAC address, IP address, external VLANs are devised from vCenter and stored in the Workload object, as shown in Figure 37.
           1. All tags associated with the VM are attached to the Workload object as labels.
1. From the PSM, Step 5 red: Assigns a unique micro-segmentation VLAN as a VLAN override to each connected vDS port (i.e each VNIC interface).
  
<div style="text-align:center">
  
![image alt text](/images/PSM/PSM_User_Guide/ESXi_Host_Deployment/58875314cc928735f83603b05e059dafbf125c08.png)
<font size='2'>*Figure 37. Workload object automatically populated with information from vCenter*
</font>

</div>
