---
title: "PSM Object Model"
menu:
  docs:
    parent: "PSM Enterprise Edition User Guide"
weight: 8
categories: [psm]
toc: true
---
<style>
   .p-table th {
       align: center;
       border: 1px solid #ccc;
       text-align: center;
       background: #44546A;
       border-color: white;
       font-weight: bold;
       color: white;
   }

   .p-table table {
       margin-left:auto;
       margin-right:auto;
   }

   .p-table td {
       border: 1px solid #ccc;
       text-align: left;
       border-left: none;
       border-right: none;
   }
</style>
## PSM Object Model
The PSM’s intent-based paradigm relies on the PSM object model described in this section. Each object can be associated with one or more *labels* that can be used to refer to a group of objects, which is a very effective way to enable “administration at scale”. 
***NOTE:*** *Labels that begin with "io.pensando." are reserved for system use, and cannot be created or modified by the user. if the user attempts to create or modify an object's labels with a system label, the label will be silently removed from the user configuration.* 
### Host Objects
The primary compute objects are illustrated in Figure 4. A physical server is represented by a *Host* object.
A Host can have one or more *DistributedServicesCard* objects, each representing a DSC card. 
Each VM on a host is represented by a *Workload* object.
  
![image alt text](/images/PSM/PSM_User_Guide/PSM_Object_Model/1c6c34327374713a704288a570cbe7b3a476dc7e.png)<div style="text-align:center">
<font size='2'>*Figure 4. PSM primary compute objects*
</font>

</div>Once a DSC card has been admitted into a PSM cluster, it must be associated with a Host object representing the host it is installed in. In general, Host objects cannot be changed or updated.[^kix.1vrgibiaznp5]
### Firewall Objects
The primary firewall objects are illustrated in Figure 5. The *NSPRule* (Network Security Policy Rule) specifies the firewall behavior, but is not a managed object itself.  Instead, the *NetworkSecurityPolicy*[^kix.fxq3mgc0p6ri] is the managed object that contains an array of NSPRule specifications.
  
![image alt text](/images/PSM/PSM_User_Guide/PSM_Object_Model/74b8466cec2e4faa05fbe4c3bb3505579cf53546.png)<div style="text-align:center">
<font size='2'>*Figure 5. PSM primary firewall objects:*
</font> 
<font size='2'>*NetworkSecurityPolicy, NSPRule, and App*
</font>

</div>
### Workloads, Apps, and Network Policy
In PSM terminology, a *Workload* corresponds to an OS-provisioned VM, bare-metal server, or container.  A Workload is defined by its *host-name* and by one or more *interfaces* defined by:

- mac-address
- ip-addresses
- micro-seg-vlan
- external-vlan
  
When applied to an ESXi environment, the *micro-segmentation VLAN* of a Workload corresponds to a *port-VLAN* within the vSphere Distributed Switch (vDS) that is unique and associated to the VM network interface.
In PSM terminology, an *App* is a service defined either by a protocol/port pair, or by an application level gateway (ALG).
In PSM terminology, a *Network Security Policy* is a collection of firewall rules, governing App connectivity between Workloads.
### Key PSM Objects
The following table contains sample key PSM objects. For a complete list please refer to the REST API online help available through the PSM GUI.
<div class="p-table center"><div></div>

| <div style="text-align:center">**Object** | **Description** |
| --- | --- || </div>Distributed<br>ServiceCard | DSC Object, one per DSC, identified by the hostname assigned by the  penctl or esx-pencli CLI tool.  If no name was assigned, the card’s MAC address is used.<br><br>- A DistributedServiceCard object is subsequently associated to a Host object |
|   <br>Host | One Host object for every ESXi (or bare-metal) host<br><br>- Associated to one or more DistributedServiceCard objects based on their MAC addresses<br>- Allows the PSM to correlate one or more DSC cards to a Host<br>- A Host object is subsequently referred to by a Workload object |

</div>
  
<div style="text-align:center">*Table 2. PSM objects (part 1/3)*
</div>

<div class="p-table center"><div></div>

| <div style="text-align:center">**Object** | **Description** |
| --- | --- || </div>Workload | One Workload object for each VM, container or bare-metal server<br><br>- Refers to a Host object<br>- Allows PSM to correlate a Workload with Host and DSC<br>- Workload object is subsequently referred to by a NetworkSecurityPolicy <br>  <br><br>***Note:*** *A Workload object belongs to the “default” tenant unless specified. Please see the REST API Guide. A NetworkSecurityPolicy rule is typically deployed tenant-wide. ("attach-tenant": true in NetworkSecurityPolicy object)* |
| Network | A Network object represents a VLAN to which a workload is connected<br><br>- Identified by a name<br>- Contains the VLAN number and the Orchestrator(s) in which such VLAN exists and is associated to Workloads |
|   <br>App | Describes the networking specification of an application, service or traffic<br><br>- An App object is subsequently referred to by a NetworkSecurityPolicy object<br>  <br><br>***Note:*** *The App object belongs to the “default” tenant unless specified. Please see the REST API guide for a detailed description of the Tenant object.*  <br><br>*A NetworkSecurityPolicy rule is typically deployed tenant-wide. ("attach-tenant": true in NetworkSecurityPolicy object)* |
| Flow<br>Export | One object created for each flow export rule<br><br>- Contains the information necessary to identify flows whose information should be exported (i.e., a 5-tuple)<br>- Specifies the export format (IPFIX in this release)<br>- Identifies the collector(s) that should receive the traffic |

</div>
  
<div style="text-align:center"><font size='2'>*Table 2. PSM objects (part 2/3)*
</font>
