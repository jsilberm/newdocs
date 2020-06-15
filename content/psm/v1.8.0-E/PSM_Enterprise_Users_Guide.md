---
title: PSM Enterprise User Guide
menu:
  main:
weight: -10
categories: [psm]
toc: true
---

<font size='2'>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
</font>

  
![image alt text](/images/psmtest/test/70ea179e4b3f7c0b85929961df88e9ae40cb2d38.png)  
#   
#   
#   
#   
# PSM Enterprise User Guide  
#   
Date:&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
*May 15*
, 2020  
  
  
<font size='2'>
Contents
</font>

##   
## Introduction  
This guide describes how to install and operate the Pensando Policy and Service Manager (PSM) and deploy the Distributed Services Card (DSC). Please refer to the *Pensando Distributed Services Card (DSC) User Guide* for DSC installation and setup instructions.  
  
A Distributed Services Card (DSC) is installed in a PCIe slot and provides network and storage services to the host, allowing fully programmable control of all services including security and visibility features.  
  
The Policy and Services Manager (PSM) allows for configuration and delivery of network, security, and telemetry policies to Pensando DSCs at scale.  
  
The PSM is accessible through either a secure RESTful API or a browser-based GUI, both described in this document.  The full Pensando API Reference Guide for PSM is available online as part of PSM at `https://IPaddr/docs`
, where `IPaddr`
 corresponds to the PSM cluster address, and is also available in the release as `PSM_apidoc.pdf`
. The API can be used by posting REST calls in JSON format to the same URI. The GUI is a browser-based interface, accessible at the PSM cluster IP through the URI `https://IPaddr`
.   
  
Parts of this document assume that readers have VMware ESXi or KVM system administration experience.  
  
Users of PSM and this guide are assumed to be familiar with REST APIs and JSON-based payloads. The term “endpoint”, used in the context of REST API calls and `curl`
 commands, refers to the URI with respect to the PSM instance `https://IPaddr`
 .  
Developers and operators are strongly recommended to use tools such as Postman and swagger-generated client libraries for API-based development whenever possible. The PSM distribution includes a working Postman collection with sample calls and payloads for multiple common use cases.  
  
This document corresponds to the PSM 1.X.Y release.  Differences will exist with respect to certain PSM managed objects in earlier PSM releases. See the *Pensando Release Notes, Version 1.X.Y* document for details and further information about supported third party switches, cables, known issues, and fixed bugs.  
  
## Glossary  
| <font size='2'><br>**Name**<br></font> | <font size='2'><br>**Description**<br></font> |
| --- | --- |
| PSM | Pensando Policy and Services Manager |
| DSC | Pensando Distributed Services Card |
| ionic&#95;en | DSC Ethernet device driver |
| NetworkSecurity  <br>Policy | PSM name for Network Security Policy object |
| Vmware Installation Bundle (VIB) | vSphere Installation Bundle, VMware’s device driver package format |
| AAA | Authentication, Authorization, Accounting |
| Host | A system that includes a managed DSC |
  
## PSM Overview  
The Pensando PSM platform is a policy and services manager based on a programmable, secure, highly available, comprehensive single point for managing infrastructure policy management and functions for:  
  
- Distributed firewall security
- Telemetry and analytics
- Troubleshooting
- Distributed Service Card (DSC) lifecycle management
- Operations and maintenance: events, alerts, technical support
- Authentication, authorization, and accounting (AAA)
  
  
The PSM platform is designed to provide consistent policies for thousands of DSCs (refer to *Pensando Release Notes* for current support limits). The PSM platform operates as a 3-node quorum-based cluster running on VMs hosted on multiple servers for fault tolerance. The PSM can tolerate the loss of one controller node in the cluster and continue to maintain full service. The PSM controller is not involved in datapath operations; if it becomes unreachable, data traffic will continue working seamlessly on disconnected DSC hosts. Figure 1 is a diagram of the interconnection between the PSM and the DSCs it manages; interactions take place through an IP network.  
![image alt text](/images/psmtest/test/e7ab16fb3b625fa9fc35381e58e5d078c372ac2f.png)  
<font size='2'>
*Figure 1. PSM/DSC interconnection*
</font>

 <font size='1'>

</font>

PSM employs an *intent-based* configuration management structure, similar to Kubernetes. Any configuration changes are continuously monitored within the PSM until it has been confirmed that the changes have been propagated to DSCs.  
  
Each DSC is configured with an IP address that is used for communication with its associated PSM over any IP network. This is commonly referred to as its *management address*.  
  
Each DSC runs an agent which constantly watches for incoming configuration changes upon which it must take action. This agent runs within the DSC and is completely transparent to and independent of the host and its operating system.  
  
The PSM resends configuration requests until the desired state is reported back from each DSC, as shown in Figure 2:  
![image alt text](/images/psmtest/test/e66f9ecea52ae5b1bbff1048bce3c2c34a9e886d.png)<font size='1'>

</font>

<font size='2'>
*Figure 2. Working principles of intent-based configuration*
</font>

  
Intent is expressed in terms of *policies*; the PSM uses an object model to describe the various entities involved in the policies. Objects include *Host Objects*, *Workload Objects*, and *App Objects*. More information can be found in the <ins>PSM Object Model</ins> section.<font size='1'>

</font>

  
Figure 3 is a sample topology of two ESXi hosts deploying DSCs connecting to two Top-of-Rack switches.  
Note:  

- Management traffic for both the ESXi host and the DSC is untagged and, as such, gets associated by the switch to the native VLAN; such traffic is not subject to policy evaluation. The PSM supports untagged workload uplink traffic. All workload traffic, even if untagged, will be subject to policy enforcement.
- “microsegmentation VLANs”  are used on a given ESXi host to enforce traffic isolation and are facilitated by ESXi port groups: each VM is associated to a port group (PG) with its own VLAN (e.g., 10, 20, 30) in the figure below.
- VMs on different hosts can communicate with each other if they share the same external VLAN (or Workload VLAN) that was specified and associated with the Workloads. For further details, please see the section <ins>First Time Workload Configuration</ins>.
![image alt text](/images/psmtest/test/fc707a0a5a46cfcdda5c45af0627b9ed67f03057.png)  
  
<font size='2'>
*Figure 3. ESXi host physical interconnection and virtual networking configuration*
</font>
<font size='2'>

</font>

## Initial Deployment Workflow: High-Level Overview  
This is an outline of the steps necessary for initial deployment of a PSM cluster and its associated DSC-equipped hosts. Detailed steps are provided further below in this document; also refer to the *Enterprise PSM Best Practices* document for further guidance on configuration.  

<font size='2'>

- Installing the PSM
</font>
- Install the PSM as eith2r an ESX-based or KVM-based 3-node cluster. 
- Configure the PSM using the `bootstrap_PSM.py` utility.
- Save a copy of the DSC security token.
- Set the PSM user authentication policy, and create PSM users with appropriate roles.
<font size='2'>
- Network Switch Port Configuration
</font><font size='2'>
-
</font> 
- Configure the top-of-rack switch ports connecting to DSC uplinks.
<font size='2'>
- Host Configuration
</font> 
- Download and install DSC device drivers on each host.
- Associate each DSC to the PSM either from its host or via DHCP.
- Plan for one additional IP address allocated to each DSC as a management interface, configured either from its host or via DHCP.
- Admit the DSC into its PSM cluster.  The PSM can be configured to allow this to happen automatically.
- (optional) Create a “Host” object corresponding to the admitted DSC.
<font size='2'>
- Create and Manage Network Policies
</font><font size='2'>
-
</font> 
- Create “Workload” objects corresponding to each VM instance.
- (optional) Create “App” objects, corresponding to network services.
- Create and manage policies corresponding to various features such as flow export and firewall rules and permissions between Workloads and Apps.
  
  
Installation of the PSM cluster is a one-time activity; other procedures may be performed during initial installation, but will also be part of the standard operation of the PSM, performed for each addition of hosts, users, and policies.  
## PSM Object Model  
The PSM implements an intent-based paradigm that relies on an object model described in this section. Each object can be associated with one or more labels that can be used to refer to a group of objects, which is a very effective way to enable “administration at scale”.  
NOTE: Labels that begin with "io.pensando." are reserved for system use, and cannot be created or modified by the user. If the user includes such a system label in an operation (e.g., association of labels to an object, identification of objects by label), the label will be silently removed from the operation.  
  
### Host Objects  
The primary compute objects are illustrated in Figure 4. A physical server is represented by a *Host* object. A Host can have one or more *DistributedServicesCard* objects, each representing a DSC card. Each VM is represented by a *Workload* object.  
![image alt text](/images/psmtest/test/68a3c0810830b22c0578c2167db29c33e7c8c764.png)  
<font size='2'>
*Figure 4. PSM primary compute objects*
</font>

Once a DSC card has been admitted into a PSM, it needs to be associated with a Host object representing the host it is mounted on. In general, Host objects cannot be changed or updated.   
### Firewall Objects  
The primary firewall objects are illustrated in Figure 5. The *NSPRule* (Network Security Policy Rule) specifies the firewall behavior, but is not a managed object itself.  Instead, the *NetworkSecurityPolicy* is the managed object that contains an array of NSPRule specifications.  
![image alt text](/images/psmtest/test/74b8466cec2e4faa05fbe4c3bb3505579cf53546.png)  
<font size='2'>
*Figure 5. PSM primary firewall objects:*
</font> 
<font size='2'>
*NetworkSecurityPolicy, NSPRule, and App*
</font>
<font size='2'>

</font>

### Workloads, Apps, and Network Policy  
In PSM terminology, a *Workload* corresponds to an OS-provisioned VM, bare-metal server, or container.  A Workload is defined by its “`host-name`
” and by one or more “`interfaces`
” defined by:  

- mac-address
- ip-addresses
- micro-seg-vlan
- external-vlan
  
  
When applied to an ESXi environment, the “micro-segment VLAN” of a Workload corresponds to a “port-VLAN” within the DVS that is unique and associated to the VM network interface.  
  
In PSM terminology, an *App* is a service defined either by a “protocol, port” pair, or by an application level gateway (i.e. “ALG”)  
  
In PSM terminology, a *Network Security Policy* is a collection of firewall rules, governing App connectivity between Workloads.  
### Key PSM Objects  
The following table contains sample key PSM objects. For a complete list please refer to the REST API online help available through the PSM GUI.  
  
| <font size='2'><br>**Object**<br></font> | <font size='2'><br>**Description**<br></font> |
| --- | --- |
| Distributed  <br>ServiceCard | • DSC Object, one per DSC, identified by the hostname assigned by the  `penctl`<br> or `esx-pencli`<br> CLI tool.  If no name was assigned, the card’s MAC address is used.  <br>• A DistributedServiceCard object is subsequently associated to a Host object |
| Host | • One Host object for every ESXi (or bare-metal) host  <br>• Associated to one or more DistributedServiceCard objects based on their MAC addresses  <br>• Allows the PSM to correlate one or more DSC cards to a Host  <br>• A Host object is subsequently referred to by a Workload object |
| Workload | • One Workload object for each VM, container or bare metal server  <br>• Refers to a Host object  <br>• Allows PSM to correlate a Workload with Host and DSC  <br>• Workload object is subsequently referred to by a NetworkSecurityPolicy  <br>  <br>***Note:*** *A Workload object belongs to the “default” tenant unless specified. Please see the REST API guide A NetworkSecurityPolicy rule is typically deployed tenant-wide. ("attach-tenant": true in NetworkSecurityPolicy object)* |
| Network | • A Network object represents a VLAN to which a workload is connected  <br>•It is identified by a name  <br>•It contains the VLAN number and the Orchestrator(s) in which such VLAN exists and is associated to Workloads |
## <font size='2'>

</font>

| <font size='2'><br>**Object**<br></font> | <font size='2'><br>**Description**<br></font> |
| --- | --- |
| App | • Describes the networking specification of an application, service or traffic  <br>• An App object is subsequently referred to by a NetworkSecurityPolicy object  <br>  <br>***Note:*** *The App object belongs to the “default” tenant unless specified. Please see the REST API guide for a detailed description of the Tenant object.*  <br>  <br>*A NetworkSecurityPolicy rule is typically deployed tenant-wide. ("attach-tenant": true in NetworkSecurityPolicy object)* |
| Flow  <br>Export | • One object is created for each flow export rule  <br>• It contains the information necessary to identify flows whose information should be exported (i.e., a 5-tuple).  <br>• It specifies the export format (IPFIX in this release)  <br>• It identifies the collector(s) that should receive the traffic |
| Mirror  <br>Sessions | • One object is created for each bidirectional traffic mirroring rule  <br>• It contains the information necessary to identify flows whose packets should be captured and exported (i.e., a 5-tuple).  <br>• It defines a schedule for the mirroring to start  <br>• It specifies a protocol (currently ERSPAN is supported) and an address for the collector  <br>• It indicates the size to which packets should be truncated. |
| Network  <br>Security  <br>Policy | • Contains traffic rules (embedded objects) and/or references to App objects  <br>  <br>***Note:*** *The NetworkSecurityPolicy object belongs to the “default” tenant unless specified. Please see the REST API guide for detailed description on object ‘Tenant’.*  <br>*NetworkSecurityPolicy defined rules are deployed tenant wide. ("attach-tenant": true in NetworkSecurityPolicy object)* |
##   
<font size='1'>

</font>

## Installing the PSM  
**NOTE**:  Before installation, refer to the Release Notes for the minimum resource requirements needed to operate the PSM.    
### Install and Configure the PSM (ESXi Cluster)  
The PSM installs as a virtual appliance (OVA format file), deployed through VMware Virtual Center (vCenter). The PSM deployment depends on vApp and requires vCenter for installation. *While it is recommended that vCenter or OVFtool is used to deploy the PSM OVA, more savvy users can use native ESXi tools.*  
See the *PSM for Enterprise Solution Design Best Practices* document for details on hardware and software requirements for PSM installation. Please plan for 60 minutes as an upper-bound limit to install a 3-node PSM cluster.  
  
A PSM instance is deployed as a high-availability quorum-based cluster. To ensure the highest availability, the PSM should be installed on 3 VMs, each on separate host that are part of a VMware HA cluster.   
  
- Log in to vCenter. Locate the ESXi host you want to install a PSM node on and select “Deploy OVF Template” from the Action button.   
- Specify the URI or Local File name of the PSM OVA file `psm.ova`.
- Specify the PSM VM name.
- Under the storage section, select Thick Provision. 
- Specify the OVA properties: hostname, IP address, etc.
- If using DHCP, leave the IPaddress blank, and configure a static MAC address-to-IP binding (reservation) for this host in the DHCP server. 
- Note that changing PSM cluster node IP addresses after bootstrapping is not supported. 
- It is strongly suggested that static IP is used. 
- Under Password, specify the SSH/console password.
- Review details. Click “Next” to accept the advanced configuration warning and lack of Publisher certificate. 
- Start the VM in vCenter once the OVA deployment status shows “Completed”. The boot process will untar and install the PSM distribution from a read-only partition.
- When the VM comes up, validate that the hostname has changed to what was specified in the OVA properties above and is not “localhost”. If “localhost” appears, then contact Pensando Support, as this indicates that the initialization did not complete successfully.
- Login to the PSM as user `root`, with the password specified in the OVA properties above (if one was not defined in the OVA properties, the default password is `centos`). If a non-default root password is configured, it may take 1-2 mins for the password to take effect after the login prompt becomes available. If this is a concern, make sure network access to the VM is disabled until the password has been reset.
- Initialize the cluster, as described in the section <ins>Bootstrap the PSM Cluster</ins>.
  
  
NOTE: Deploying a 3-node cluster involves importing the `psm.ova`
 file once for each VM instance. The number of imports can be reduced by cloning the first VM as a template, and then deploying subsequent VMs from the template. If taking this approach, follow these steps:  

- Create the first VM from the `psm.ova` file
- In vCenter, choose “Clone as Template to Library” to save the VM as a Template (.vmtx) file.  Be sure to give the VM a unique name.
- Select the new VM in vCenter. Select the “Configure” Menu item. Expand “Settings” and select “vApp Options”. Scroll down to “Properties”. Click the radio button for “hostname” and the “Set Value” action to change the hostname to a unique value (typically corresponding to the VM unique name).
- If applicable, apply any network-specific settings that may have been used in deploying the original VM from the `psm.ova` file. 
- Start the new VM and verify that the VM name and network setting are as intended before bootstrapping the cluster as described in the below section <ins>Bootstrap The PSM Cluster</ins>.
  
### Install and Configure the PSM (KVM Cluster)  
The PSM is supported on KVM as well as ESXIi; this section provides a short summary of the steps required to set up a KVM-based PSM appliance.  For a detailed guide, see <ins>Appendix M</ins>.  
  
- Create three KVM hosts. Server requirements are specified in the document *Enterprise PSM Design Best Practices*. (Pensando recommends that the three PSM cluster nodes should be distributed across multiple servers). 
- Configure the needed network bridges for access to the CentOS server and for the PSM.
- Make sure the VLAN module is loaded for each server.
- Create a bridge interface named br0 that links interface eno5, which is an active interface on the server.
- Restart the network and verify that the CentOS system server1 is accessible.
- Verify the network interfaces.
- Create the interfaces that will be used for the PSM.
- Create the interface that is linked to the physical interface.
- Restart the network service.
- Repeat the above steps to deploy the second server (server2) in the environment (a third one you might have in your setup).
- Install the PSM software:
- Deploy each PSM node using the `psm.qcow2` image
- Set networking for the nodes
- Bootstrap the cluster, as described in the next section.
  
### Bootstrap The PSM Cluster  
Before the PSM cluster can be administered, it must be initialized via the `bootstrap_PSM.py`
 utility.  Below are some usage examples. The command `bootstrap_PSM.py -h`
 will show all parameters that can be specified.  
Determine the IP address assigned to each PSM VM that has been deployed. In ESXi deployments this can be obtained from vCenter, or from within a CentOS VM with `ip addr`
. This address is required when launching the `bootstrap_PSM.py`
 utility and is provided through the `-v`
 option.  
  
NOTE: a PSM VM should have a single L3 interface that it uses to communicate to other PSM VMs as well as its DSCs. The IP address of this interface should be used in bootstrapping the cluster. The default IP route should point to this interface.  
<font size='2'>
**Example:**
</font>
<font size='2'>
 If you have only one PSM VM (for testing only):
</font>



```
# bootstrap_PSM.py -v 192.168.68.49


2019-09-26 11:48:05.405149: * start PSM bootstrapping process
2019-09-26 11:48:05.405195: * - list of PSM ips: ['192.168.68.49']
2019-09-26 11:48:05.405214: * - list of ntp servers: ['0.us.pool.ntp.org', '1.us.pool.ntp.org']
2019-09-26 11:48:05.405228: * - using domain name: pensando.io
2019-09-26 11:48:05.405240: * - auto-admit dsc: True
2019-09-26 11:48:05.405252: * checking for reachability
2019-09-26 11:48:09.415351: * connectivity check to 192.168.68.49 passed
2019-09-26 11:48:09.415436: * creating PSM cluster
2019-09-26 11:48:09.416110: * sending: POST http://localhost:9001/api/v1/cluster
2019-09-26 11:48:09.416144: {"api-version": "v1", "kind": "Cluster", "meta

(..snip..)

```
<font size='2'>

</font>

<font size='2'>

</font>

<font size='2'>
**Example:**
</font> 
<font size='2'>
To bootstrap a 3-node PSM cluster for production, specify all three IP addresses. Before executing this command, make sure that all three PSM VMs are already running. The PSM VMs can be deployed using the same OVA, but must have unique IP addresses. The bootstrap script only needs to be executed on one of the nodes.
</font>

<font size='2'>

</font>



```
# bootstrap_PSM.py -v 192.168.68.49 192.168.68.50 192.168.68.51

```
<font size='2'>

</font>

<font size='2'>
If everything completes successfully, the message below can be seen in the log:
</font>

<font size='2'>

</font>



```
(..snip..)

2019-09-26 18:52:13.693626: * PSM cluster created successfully


2019-09-26 18:52:13.693656: * you may access PSM at https://192.168.68.49

```
  
  
The PSM browser GUI and REST API should now be available at any of the PSM addresses. Note that there is no virtual IP address for the 3 node cluster. A load balancer should be installed in front of the cluster to enable such functionality.  
<font size='2'>

</font>

If a password is not specified when bootstrapping the PSM cluster, the default is `Pensando0$`
.   
  
The `bootstrap_PSM.py`
 utility can be used to provide configuration information to the PSM. The following example provides a cluster name, a domain name, and the address of an NTP server, and activates automatic DSC admission:  
<font size='2'>

</font>



```
# bootstrap_PSM.py -clustername Pod02 -domain training.local -ntpservers 10.29.5.5 -autoadmit True 10.29.12.11 10.29.12.12 10.29.12.13

```
<font size='2'>

</font>

To change the PSM cluster root password once the cluster is operational, see <ins>Appendix H</ins>.  
  
**Note**: Please make sure to save the DSC Security Token and store it in a safe place. This may be needed for advanced troubleshooting through the penctl tool, in situations where the PSM and a DSC cannot communicate.  
See: <ins>Appendix B -</ins> <ins>Save the PSM Security Token</ins>.  
## Network Switch Port Configuration  
This section details the configuration required on Top-of-Rack (ToR) switches to which DSCs are connected.  
Since each DSC card can send and receive traffic over multiple VLANs, DSCs *must* connect to switch ports configured as trunk ports under certain conditions:  

- If the Workloads on a host are configured to use an IEEE 802.1q External VLAN, then the corresponding switch port **<ins>must</ins>** be configured as a trunk port.
- If all the Workloads on a host are sending untagged traffic (External VLAN 0), then the switch port associated with DSC can be configured as an access port.
  
  
All management traffic (towards an ESXi host or DSC) is expected to be untagged. Any management traffic must be configured with the native VLAN of the network switch. Most network switches use "VLAN 1" as the native VLAN on a trunk port, when not explicitly configured with a native VLAN.  If the management traffic is not using VLAN 1, then adjust the "trunk native vlan" switch port configuration to match the VLAN ID used by management traffic to ensure that it will be transmitted untagged on the links to DSCs.  
  
## PSM Graphical User Interface  
The PSM Graphical User Interface (GUI) is accessible via a web browser at `https://IPaddr`
, where `IPaddr`
 corresponds to the IP address of any of the PSM cluster nodes. Figure 6 shows a configurable dashboard that offers an overview of the status of the Pensando Distributed Services Platform, while the main menu on the left hand side provides access to the configuration of all supported features.  
  
![image alt text](/images/psmtest/test/f0da5c86680b4e0e810bf5d815aa41f6c59d70bf.png)  
<font size='2'>
*Figure 6. Pensando PSM dashboard*
</font>

### Online Help  
Detailed and comprehensive online help is offered in a context-sensitive manner for each page in the PSM GUI, accessible through the help icon in the upper right-hand corner:  
![image alt text](/images/psmtest/test/56fc814d489af1d51dd3689eb840e0e77cc4b292.png)  
The help icon is context sensitive, showing information related to the currently displayed GUI elements. For example, clicking the help icon while in the Workload overview will display descriptive help and examples on how to create a Workload object, as shown in Figure 7.  Similarly, clicking the help icon while in the Monitoring -> Alerts and Events view will show help on configuring Alert Policies.  
  
![image alt text](/images/psmtest/test/4e0d953262ec943c6d48ed5104a9f9d693f9cbbb.png)  
<font size='2'>
*Figure 7. Example of PSM help*
</font> 

  
Online Help windows can be easily undocked, redocked, resized, or closed.  
  
Online Help has its own presentation context, so it does not need to be closed prior to subsequent operations; selecting different items from the left-hand-side Navigation pane will automatically display the corresponding Online Help information.  
### Searching  
The easy-to-use search facility is accessed from the search bar at the top of the screen.  
  
  
![image alt text](/images/psmtest/test/0c817f466d532b910771389c3daab4701faf2935.png)  
<font size='2'>
*Figure 8. PSM search facility*
</font>

  
In the example in Figure 8 above, doing a free form text search for the string “ae-s7”, shows a summary of the various objects where that string appears, along with a count of the number of occurrences for each object type.  
  
![image alt text](/images/psmtest/test/0c0c898bff294494f89bb75d83a7a4de1e186e6a.png)  
*Figure 9.* *Accessing Advanced Search*  
  
Clicking on the downward arrow on the right hand side of the text box (shown in Figure 9 above) gives access to the Advanced Search capability shown in Figure 10, where users can search based on object Category, Kind or Tag (arbitrary labels associated to objects):  
### ![image alt text](/images/psmtest/test/f9219711a5b9ed3999f20bc1c2be667d0ffe4297.png)  
<font size='2'>
*Figure 10. Advanced Search*
</font>

  
All the keywords used in Advanced Search can also be typed directly into the search bar to avoid having to bring up the Advanced Search tab.  
  
### Global Icons  
The GUI makes use of common/global icons for many actions, regardless of context, such as “Edit” or “Delete”, as shown in Figure 11 :  
![image alt text](/images/psmtest/test/712d177b09f9d571ea25d0235cff49d2cfb1a961.png)<font size='2'>

</font>

![image alt text](/images/psmtest/test/03017ea8c278ee0b6210812d41a947509f1f0d03.png)<font size='2'>

</font>

<font size='2'>
*Figure 11. Edit and Delete icons*
</font>

<font size='2'>

</font>

Many of the tables displayed in the GUI can be exported as CSV or JSON text files, as shown in Figure 12:  
![image alt text](/images/psmtest/test/4310a830292dba3f8182bac18de8517dbccdd6a5.png)  
### ![image alt text](/images/psmtest/test/6012cea6be19bedcdb5639ee8bfae97d284661e1.png)  
<font size='2'>
*Figure 12: Example of how a table can be exported in CSV or JSON format*
</font>

#### Server Certificate  
By default, a self-signed certificate is created by the PSM during installation, and is used to authenticate connections to the browser-based GUI or REST clients. Users may instead provide a custom key and certificate to the PSM to be used instead of the default self-signed one. If the root Certification Authority (CA) of the signer of such certificate is included in either the browser or the client hosts’ trusted root CA certificate list, warning messages related to the certificate validity will no longer be shown when accessing the PSM cluster login page.  
  
The two supported encoded key formats are RSA and ECDSA. To change the PSM certificate, click "Admin" --> "Server Certificate". On the top right hand side, click  "UPDATE". Enter the key and certificate in PEM format and then click "Upload" to apply the change, as shown in Figure 13. **Note:** this action will not disrupt existing connections, even if they were established with the previous certificate.  
  
![image alt text](/images/psmtest/test/3c02459f0645874e12653e673ecdd8fd63544a6c.png)<font size='2'>
*Figure 13.*
</font> 
<font size='2'>
*Changing the PSM server certificate*
</font>

#### API Capture  
The PSM GUI can display the REST API calls sent from the GUI to the PSM as it implements the configurations created by the user. When the API Capture menu item is selected, a view as shown in the figure below appears. Use this screen to browse sample API calls (in the API Capture tab) or a live capture of APIs generated while navigating the GUI (in the Live API Capture tab).  This can be a valuable tool to explore how the PSM API can be used for external integrations. The live capture tool is per GUI session; large responses are trimmed down to two records to present the look and feel of the response, rather than the entire response.  
  
![image alt text](/images/psmtest/test/0ac9eaa10bc3effebb068e275429b7ece815e39a.png)  
<font size='2'>
*Figure 14. Examples of captured REST API calls*
</font>

### Online Documentation  
The PSM Reference guide is provided in online format, and included within the PSM itself. The online documentation can be accessed at `https://IPaddr/docs`
 , where `IPaddr`
 corresponds to the PSM cluster address.  
## Create PSM Authentication Policy and Users  
Each PSM will have one or more users defined. Users are assigned roles granting them privileges depending on the tasks they need to perform; during the installation process, a default user, named `admin`
  with the password `Pensando0$`
 , is created with full administrator privileges. A different name for the default user as well as its password can be provided as parameters to the  `bootstrap_PSM.py`
 utility used to initialize the cluster as described in the section “<ins>Bootstrap The PSM Cluster</ins>”.   
### Authentication Policy  
The PSM supports Local (i.e., username and password), LDAP and RADIUS Authenticators, as shown in Figure 15. Creation of authenticators should be done early in the system setup process. Once two or more authenticators are created, they can be re-ordered dynamically to specify the priority with which they should be applied.  
![image alt text](/images/psmtest/test/f8649f2c69ce468879651515f6c12c2e185cb2d3.png)  
<font size='2'>
*Figure 15. Setting user authentication policy*
</font>

  
To create an LDAP Authenticator, click the “CREATE LDAP AUTHENTICATOR” button. Active Directory (AD) and OpenLDAP providers are supported.  
  
Configure *Credentials*, *Scope* (which controls user and group entry search) and *Attribute* mapping (which contains the name of the attributes that should be extracted from the LDAP entry of the user, such as full name and email address) as appropriate, ensuring all required (*) fields are properly filled, as in Figure 16:  
  
![image alt text](/images/psmtest/test/4ca518d0f15390010394d327785b3d3969652c11.png)  
<font size='2'>
*Figure 16. LDAP configuration*
</font>

  
Once saved, the values should be visible, as shown in Figure 17. The order of the various authenticators can be changed (using the small arrows on the right hand side).  
  
![image alt text](/images/psmtest/test/28655fdd0bf6ae298d317221d05c74361ad9d669.png)  
<font size='2'>
*Figure 17. Changing authentication order*
</font>

  
### Role Based Access Control (RBAC)  
The User Management menu gives access to the RBAC Management screen, shown in Figure 18, which allows management of either users or roles, or the association of users to roles (“rolebinding”) based on the selection made with the drop-down menu on the top right corner of the view. The recommended User Management sequence consists of first creating one or more Roles, followed by one or more Users, and then creating the corresponding associations (rolebinding).  
  
![image alt text](/images/psmtest/test/8ae2fe77052e06139f8b7f6476b0983de4b40f7f.png)  
<font size='2'>
*Figure 18.*
</font> 
<font size='2'>
*RBAC management*
</font>

  
####   
#### Roles  
Roles are created to control access to classes of features by sets of users. Roles can have scope over various objects, which are grouped by the PSM in the categories:   
  
- Auth
- Cluster
- Diagnostics
- Monitoring
- Network
- Objstore
- Rollout
- Security
- Staging
- Workload
  
  
![image alt text](/images/psmtest/test/5ba28d057de4b4b76d3172883e2945553f33347f.png)  
<font size='2'>
*Figure 19. RBAC roles*
</font>

  
As shown in Figure 19 above, for a given Group, various kinds of management aspects are available. Once one is selected, access to actions can be added or removed, as shown in Figure 20:  
  
- Create
- Delete
- Read
- Update
  
  
![image alt text](/images/psmtest/test/36ba0ba1cf4376939ab4016a90995337c95bd60c.png)  
<font size='2'>
*Figure 20. Assigning actions to a group*
</font>

#### Role Binding  
Once a Role is created, a corresponding rolebinding is automatically created. Rolebindings allow Users to be flexibly mapped to various sets of roles. Figure 21 shows the view to modify a “rolebinding” that allows to associate any of the users defined in the system (in the left list titled Available) with the Role specified in the form. Users successfully associated with the Role appear in the right list titled Selected.  
The rolebinding can be also specified using the “Group” attribute value configured in the LDAP authenticator “Attribute Mapping” section and retrieved from the LDAP user entry. This is the distinguished name of the LDAP group entry a user belongs to.  
  
![image alt text](/images/psmtest/test/1eb943a427507f388f3a96fc72c547681e6065ff.png)  
<font size='2'>
*Figure 21.*
</font> 
<font size='2'>
*Rolebinding*
</font>
<font size='2'>

</font>

## Bringing a DSC under PSM Management  
In order to have a DSC managed by the PSM it is necessary to first have the DSC discovered by the PSM, and then the PSM admin authorizing the DSC to join the cluster and be subsequently managed.  
### Associating a DSC with a PSM  
Each DSC requires its own IP address to communicate with the PSM. As the DSC obtains its address, it also gets the IP addresses of its assigned PSM. There are several options involved in associating a DSC with a PSM:  
  
- In-band versus out-of-band (OOB) access for management traffic
- Static versus DHCP address assignment
  
  
If the communication between the PSM and a DSC is OOB, then the dedicated physical DSC 1G Ethernet port will be used for management, and it should be connected to a network through which the PSM is accessible. If the communication is in-band, then management traffic will go through the main uplink ports and the PSM must be configured to use the in-band management network.  
  
Independently of whether OOB or in-band communication is deployed, the DSC management IP address can be set either statically or via DHCP. The same applies to the PSM address.  
  
Associating a DSC to a PSM requires properly setting the following parameters with the appropriate CLI tool (e.g. `penctl`
 for Linux and Windows, `esx-pencli`
 for ESXi):  
  
| **Parameter Name** | **Possible Values/Format** | **Default Values** | **Notes** |
| --- | --- | --- | --- |
| ID | N/A | N/A | DSC “name”. Typically same as “hostname” |
| ip-address | X.X.X.X/NN | N/A | DSC mgmt IP address and subnet mask if Static.  If DHCP, then “” |
| network-mode | INBAND or OOB | OOB | Use INBAND for single-wire management |
| Controllers | [ X.X.X.X, Y.Y.Y.Y, Z.Z.Z.Z ] | N/A | Array of IP addresses for PSM VMs |
  
  
The following command is used to statically assign a management address to a DSC for in-band management and provide the address(es) of the PSM:  
<font size='2'>

</font>



```
# penctl update dsc -i <DSC hostname> -o network -k inband -m <IP Address/netmask> -g <ip gateway> -c <cluster IP  addresses separated by ,>

```
  
If an IP address and default gateway are not specified, as in the following example where the 1Gb/s management port of the DSC is used for out-of-band management, the DSC will use DHCP to obtain them:  
  
<font size='2'>

</font>



```
# penctl update dsc -i DSC-A -o network -k oob -c 10.1.1.1,10.1.1.2,10.1.1.3

```
  
If no information is statically configured, the DSC tries to receive a full configuration (management IP address as well as PSM IP address) through DHCP.  
  
For more information on configuring a DCHP server to provide PSM information, please refer to <ins>Appendix I: ISC DHCP Server Example</ins>.  
For information on upgrading a DSC firmware and associating it to a PSM in ESXi environments, please see <ins>Appendix K: ESXi Sequence for Upgrading the DSC Firmware and Associating it to a PSM</ins>.  
For more information on initial installation/configuration of the DSC, please refer to the **DSC User Guide**.  
### Admit DSCs Into the PSM Cluster  
DSCs that are associated with a PSM are listed in the Distributed Services Cards Overview, shown in Figure 22. The view also displays a few statistics and metrics for admitted cards.  
![image alt text](/images/psmtest/test/8303ba5ff6ff2af734dd374c6534fa1e880f90b6.png)  
<font size='2'>
*Figure 22. Distributed Services Cards Overview screen*
</font>

The PSM admission policy `auto-admit-dscs`
 controls whether DSCs are admitted automatically or not. It is a cluster-wide attribute that determines whether or not new DSCs are automatically admitted into the PSM cluster once they are connected. The `bootstrap_PSM.py`
 utility can be used to set the value of `auto-admit-dscs`
 at cluster creation time.  
If set to `true`
 (the default value), the admission process happens automatically.  If set to `false`
, then each DSC must be explicitly admitted into the cluster (via GUI or automated via API). DSCs can be admitted via the PSM GUI by hovering and clicking the right-hand side icon shown in Figure 23.  
  
![image alt text](/images/psmtest/test/589c8f9b728c16466ed143ecad65da1102801f28.png)  
<font size='2'>
*Figure 23. Admitting a DSC*
</font>

Admitted DSCs can be decommissioned by hovering and clicking the right-hand side icon, as shown in Figure 24.  
  
![image alt text](/images/psmtest/test/b39d3c7e1bcc9d4d6be17fe30f21213dd535daf2.png)  
<font size='2'>
*Figure 24. Decommissioning a DSC*
</font>
<font size='2'>

</font>

  
Once a card is decommissioned, it is so indicated, as shown in Figure 25.  
![image alt text](/images/psmtest/test/e3e2849330478af2f93c395ceb9ca5631f1912a5.png)  
<font size='2'>
*Figure 25. DSC is listed as Decommissioned*
</font>

#### Host Management  
Host objects are created in one of two ways:  

- Hosts and corresponding DSCs are created implicitly when a PSM is configured to interoperate with vCenter.
- Hosts are created explicitly and associated to their DSC(s) in the PSM. 
  
  
A Host can be added by specifying a logical ID or the mac-address of a corresponding DSC, as shown in Figure 26. Note that the mac-address format is “xxxx.yyyy.zzzz”.  
  
![image alt text](/images/psmtest/test/feb06b5ccaea328518d46c01a1431876e4b7546b.png)  
<font size='2'>
*Figure 26. Select name type for this Host object*
</font>

  
The PSM will associate the Host object to the appropriate DSC object. As shown in Figure 27, if Workload objects have been created and associated to Hosts, they appear in the Hosts Overview.  
![image alt text](/images/psmtest/test/c012fd827f9bad937d26a9f329ad536c889a7cfe.png)  
<font size='2'>
*Figure 27. Hosts Overview*
</font>

Hosts can be deleted by checking one or more corresponding Hosts and clicking the delete icon, as shown above in Figure 27. Hosts cannot be deleted if they have any associated workloads. When a PSM is configured to interoperate with vCenter, then PSM hosts will be automatically deleted if any ESXi hosts are deleted, as vCenter configuration is reconciled with the PSM.  
#### DSC Features and Profiles  
The PSM allows users to turn on features incrementally on one or more hosts at a time. Users can define feature profiles using an object called *DSC Profiles*, and associate them with DSCs.  
  
Each DSC Profile has two settings: *DSC Profile Name* and *Feature Set*; together they determine the set of features supported by all DSCs assigned with that profile. A DSC can only be assigned to a single profile at any given time.  
  
Figure 28 shows the overview of DSC profiles provided by the PSM GUI.  
  
![image alt text](/images/psmtest/test/8e9249dcda0471f2a448984385864f856392810e.png)  
<font size='2'>
*Figure 28. DSC Profiles Overview*
</font>

  
If a profile’s settings are changed, all DSCs associated with that profile will automatically inherit support of the new set of features. Similarly, if a DSC is associated with a different profile the DSC will inherit support for the new set of features.  
##### Deployment Targets  
Two options are currently available as Deployment Targets: Host and Virtualized.    
###### Host  
The services implemented by the DSC are applied to the traffic entering and exiting the host. As shown in Figure 29, when the Host Deployment Target is selected, two Feature Sets are available for the user to select between: SmartNIC,  Flow Aware, and Flow Aware with Firewall, (see <ins>Feature Sets</ins> below for an explanation of the features available).  
![image alt text](/images/psmtest/test/01830cab7dccd912f978e89d5e54a12ff4b207b7.png)  
<font size='2'>
*Figure 29. Deployment Target selection*
</font>

  
###### Virtualized  
When the Virtualized Deployment Target is selected, the services implemented by the DSC installed on an ESXi host are applied to the traffic generated and received by each single VM. As shown in Figure 30, when this Deployment Target is selected, only the Flow Aware with Firewall Feature Set is available (see <ins>Flow Aware with Firewall</ins> below for an explanation of the features available in this Feature Set).  
  
![image alt text](/images/psmtest/test/cbbf1e943a0d74cba4e0f12135f19fe040b2ecda.png)  
<font size='2'>
*Figure 30. Feature Set selection for Virtualized Deployment Target*
</font>

##### Feature Sets  
<font size='2'>

</font>

Three Feature Sets are currently supported by the Pensando platform and are described below.  
###### SmartNIC  
The SmartNIC Feature Set, currently available with the Host Deployment Target, includes telemetry and visibility functions, such as a rich set of metrics and bi-directional traffic mirroring with ERSPAN. Although other Feature Sets include a wider range of services, the SmartNIC Feature Set does not have any limits in terms of connections per second that can be established through the card and it is therefore recommended when other services are not needed and the traffic is expected to have a large number of new flows per second is needed, such as in HPC (high performance computing) clusters or when conducting host performance testing.  
###### Flow Aware  
The Flow Aware Feature Set, currently available with the Host Deployment Target, includes features that require a DSC to keep track of individual flows. Examples include flow-based bi-directional ERSPAN, flow statistics, NetFlow/IPFIX. These features are key in gaining visibility on the network and possibly learn communication patterns within the enterprise data center, which can be used as a basis to create appropriate firewall policies.  
###### Flow Aware with Firewall  
The Flow Aware with Firewall Feature Set, currently available with the Virtualized Deployment Target, includes, in addition to all the features listed <ins>above</ins> for the Flow Aware Feature Set, also the capability of enforcing security policies, where a security policy specifies flows whose packets shall be forwarded or dropped by DSCs. This Feature Set selected with the Virtualized Deployment Target operates on traffic among single workloads (e.g, VMs) even if they execute on the same host. Hence, it can be used to provide visibility and enforcement with that level of granularity. A typical use case is an East-West stateful firewall, providing micro-segmentation within a data center.  
##### Default DSC Profile  
When the PSM is installed it has a pre-defined DSC Profile named Default that is associated with the Host Deployment Target and the SmartNIC Feature Set. By default when a DSC is admitted to the PSM it is assigned to the Default profile. Consequently, by default DSCs activate the SmartNIC feature set when they are admitted to the PSM.  
<font size='2'>

</font>

The PSM user can create additional profiles associated with other Feature Sets and assign DSCs to them so that they support different features.  
<font size='2'>

</font>

If the user wants DSCs to activate a different feature set when admitted to the PSM, change the Default profile so it is associated with the desired feature set.  
  
## ESXi Host Deployment  
This section details configuration steps required on ESXi hosts on which DSCs are deployed and their services should operate also on traffic among VMs running on the same host. Please refer to the  “ESXi Driver” section of the Pensando *DSC-25 Distributed Services Card User Guide* for detailed instructions on installing the driver.  
### vCenter Integration  
The PSM can use the vCenter API to perform necessary network configurations on ESXi hosts and retrieve information on the host itself and the workloads running on it. Integrating an ESXi host in the Pensando platform requires some operations on both the PSM (usually used by the network administrator), and vCenter (usually by the compute administrator), according to the workflow presented below.  
#### Underlying Principles  
Pensando uses the port group's VLAN assignment (termed as micro-segmentation VLAN) to ensure inter-VM traffic through the DSC before it is forwarded to its destination, when the DSC is assigned to a profile that is associated with the Virtualized Deployment Target. The destination can be a VM on the same or remote host.  
In order to achieve this, a different micro-segmentation VLAN is assigned to each vNIC attached to a DVS switch, as shown in the figure below; this ensures that the DVS proxy switch does not allow direct VM to VM communication. This configuration is needed to ensure that all VM to VM communications are subject to micro-segmentation policy enforcement by the DSC. Figure 31 shows various possible traffic patterns between VMs.  
![image alt text](/images/psmtest/test/55271b6961fad59d828b8c073ef7b82ca65a8649.png)  
<font size='2'>
*Figure 31. DSC access to*
</font> 
<font size='2'>
*VM-to-VM traffic*
</font> 
<font size='2'>

</font>

  
The following steps are necessary to achieve the required configuration:  
  
- Unique micro-segmentation (or uSeg) VLAN is allocated for each VM / vNIC
- Allocation of VLANs, (useg & external) is centrally managed by PSM, and pushed to DSCnodes via REST API
- DSC translates Micro-segmentation VLAN to external port-group on the uplink
- Micro-segmentation policy leverages the white list model, such that no communication within or between host VM’s is allowed unless policy expressly permits on DSC
  
####   
#### Configuration Workflow  
  
The actual PSM and ESXi configuration must follow the steps as listed below and graphically depicted in Figure 32; some of these steps require the intervention of the network administrator or compute administrator, while others are automatically carried out by the PSM leveraging the vCenter API. <font size='1'>

</font>

![image alt text](/images/psmtest/test/3c5b461a0e105d355dfbc2e450ff42759c455085.png)<font size='1'>

</font>

  
<font size='2'>
*Figure 32. vCenter integration workflow*
</font>

  
- From the PSM, Step 1 blue: navigate to the Orchestrator menu and select the vCenter function to register to a vCenter server, which requires configuring IP Address (URI) of the vCenter server and providing login credentials, as shown in Figure 33. Besides username and password, Token and certificates are supported as other authentication methods. 
![image alt text](/images/psmtest/test/4e8de5d79618c2c9347ef6e4fc2e587d111e1758.png)  
  
<font size='2'>
*Figure 33. Registering a vCenter server*
</font>

  
- Step 1 red: A Pensando DVS is automatically created by the PSM within vCenter using the vCenter API.
- From the PSM, Step 2 blue: create networks (VLANs) that are associated to the vCenter Server and to a Data Center, using the screen shown in Figure 34.
![image alt text](/images/psmtest/test/a1473198046abf52a0dab20caa08e9fd89ae4eb7.png)  
  
*Figure 34. Creating Network objects, with corresponding VLANs*  
  
- Step 2 red: The networks will become port groups of the DVS and will be visible within vCenter
- In the PSM each Network will become an “external” VLAN that will be used for packets traveling between DSC and ToR switch.
- From vCenter, Step 3 blue: the server admin associates ESXi server DSC ports to Pensando DVS
- Step 3 red: once that is done, the PSM auto-creates a Host object based upon the ESXi hostname and associates it to the DSC, as shown in Figure 35. This automatic action is triggered by the Pensando DVS configuration in vCenter.
![image alt text](/images/psmtest/test/d2d2924fdbd4954a53e6f8068f5898d6b54e7cc2.png)  
  
  
<font size='2'>
*Figure 35. Host Overview with auto-created Host object*
</font>

  
- From vCenter, Step 4 blue: the server admin creates a VM and associates the network to a PG in the Pensando DVS
- Step 4 red: as a result of this configuration change in vCenter, the PSM automatically creates a Workload object:
- MAC address, IP address, external and micro-seg VLANs are devised from vCenter and stored in the Workload object, as shown in Figure 36.
- All tags associated with the VM are attached to the Workload object as labels
![image alt text](/images/psmtest/test/cf6d860bea8301edc3a032cb2c1ba01886d792e5.png)  
  
<font size='2'>
*Figure 36. Workload object automatically populated with information from vCenter*
</font>

## Distributed Services  
All of the distributed services offered by the Pensando platform can be managed through the PSM, as presented in this section.  
### Security  
#### Network Security Policy Management  
Network Security Policies consist of one or more Security Rules within a Security Policy. A Security Rule consists of a 5-tuple: protocol type, source IP address, source port number, destination IP address, and destination port number, along with an Action (Permit, Deny, Reject). The source and destination IP address in the 5-tuple can also include a subnet (e.g “ipaddress/mask”), a comma separated list, or a range of IP addresses allowing user to aggregate policies.  The difference between “deny” and “reject” is that "deny” will drop the traffic without any response, while the "reject" option will block the traffic and report back to the client to either notify that the destination is unreachable, or close the connection.  
  
The behavior of the "reject" action depends on the type of traffic:  
1. For ICMP traffic, no flows are created in the flow-table and no “ICMP unreachable” response is sent back to the source.  
2. For UDP traffic, no flows are created in the flow-table and an “ICMP unreachable” response is sent back to source.  
3. For TCP traffic, no flows are created in the flow-table and a TCP RST segment is sent back to source, which closes the TCP connection.  
  
![image alt text](/images/psmtest/test/388c46d2ef201700c981b527dc967cf7fd17c2cf.png)  
<font size='2'>
*Figure 37. Defining a Security Rule*
</font>

  
To edit, re-order or update any Rules within a Policy, select the Rule and click the Edit icon.  
![image alt text](/images/psmtest/test/4ba544d7f623d002349f744fb654980bf0835ae8.png)  
<font size='2'>
*Figure 38. Editing a Rule*
</font>

  
**NOTE:** when deploying security policies in dual DSCs deployments (please refer to Section “Dual DSC-25 Deployment Scenarios” in the “Pensando DSC-25 Distributed Services Card User’s Guide For Enterprise Solution” for more information dual DSC deployment) flows should be pinned to a specific DSC to avoid that packets of the same flow may be handled by both cards, which would problematic when enforcing stateful rules.   
#### App Management  
An App object allows a user to define commonly-deployed applications’ protocol/ports, allowing the app’s name to be used in policies instead of repeatedly entering the protocol/port information, as shown Figure 39.  
  
  
![image alt text](/images/psmtest/test/a7442b7c0e9ada1b81438f6b1f28e2a1cea9b8d4.png)  
  
![image alt text](/images/psmtest/test/d57e6fbbebaa85b1009fde71a478a5440f246d5d.png)  
*Figure 39. App objects*  
  
App objects also allow specifying Application Layer Gateway (ALG) configurations that define application-specific firewall behavior. Supported Apps or ALGs include ICMP, DNS, FTP, SUNRPC, and MSRPC. App objects can be defined based on ALGs only, protocols and ports only, or both, as shown in Figure 40.  
  
![image alt text](/images/psmtest/test/14bf9d11df207b0526c33c12247de78a932f01ee.png)*Figure 40. App object definition types*  
  
#### Firewall Profile Management  
The PSM user can configure the operating parameters of the distributed stateful firewall implemented across the various DSCs. Figure 41 shows the screen used for this purpose.  
![image alt text](/images/psmtest/test/63cd0541cc98eb2ca16202a37544c2938fdd2bad.png)  
<font size='2'>
*Figure 41. Firewall profile configuration*
</font>

### Observability  
Policies can be created around monitoring and auditing, as outlined below.  
#### Alerts and Events  
Creating an Alert Policy involves first creating a destination for the alert, followed by the Event Alert Policy itself.   
![image alt text](/images/psmtest/test/c71cc7e411d470e7298ebcd71cd14a0cfd06b5fe.png)  
<font size='2'>
*Figure 42. Listing existing alert destinations*
</font>

<font size='1'>

</font>

First, select the “Destinations” tab and click “Add Destination” to configure the syslog collector that should receive the Alerts and Events.  
  
Next, select the “Event Alert Policies” tab and click “Add Alert Policy” to provide details. In the example below, an event is sent to the destination for any of the DSC actions. Event alert conditions can be combined into a single Alert Policy, (“+AND”) or be created as individual Alert Policies.  
<font size='1'>

</font>

![image alt text](/images/psmtest/test/b161b3d3d6fb11265c240891d13a5a28477e2f95.png)  
<font size='2'>
*Figure 43. Adding an Alert Policy*
</font>

#### Metrics  
Metrics can be charted by selecting the Metrics menu item.  
<font size='1'>

</font>

On the Metrics window, click CREATE CHART:  
<font size='1'>

</font>

![image alt text](/images/psmtest/test/5aa415ccbc22da5fb3aa3cd631c5c92110805f71.png)  
<font size='2'>
*Figure 44. Creating a chart*
</font>
<font size='2'>

</font>

  
Provide a name for your chart, select the Measurement, in this example “Session Summary Statistics”, then select the fields to be displayed. Once selection is done, click the SAVE CHART button to save your selection.  
<font size='1'>

</font>

 ![image alt text](/images/psmtest/test/71a676171c5109895eb93b3be990aefdd2c4e9cb.png)  
<font size='2'>
*Figure 45. A finished chart in the chart overview*
</font>

<font size='1'>

</font>

The chart is now saved and can be viewed at any time.  
#### Audit Events  
The GUI currently supports exporting Audit Logs as a CSV or JSON file.  Users can filter audit logs using the search tool, as shown in Figure 46::  
![image alt text](/images/psmtest/test/ab80d3786b3478a65b775bd55298849075223837.png)  
  
<font size='2'>
*Figure 46. Audit Events view*
</font>

  
The contents that are exported can be filtered to limit the amount of information, as shown below:  
  
![image alt text](/images/psmtest/test/821a271bdb6270f53135b4405ea63f0f77d9da85.png)  
<font size='2'>
*Figure 47. Filtering events for export*
</font>

  
#### Firewall Logs Export  
Firewall Log Policies allow logs to be shipped to an external destination:  
  
![image alt text](/images/psmtest/test/cddb9d0ffeaf66a9941cc2a954c34d17efeb69f2.png)  
<font size='2'>
*Figure 48. Specifying a syslog collector to receive exported firewall logs*
</font>
  
  
They can be selectively configured for export:  
  
![image alt text](/images/psmtest/test/68fd01a2fbb2cbfd39765604bf2107ebfe04f36d.png)  
  
<font size='2'>
*Figure 49. Choosing which firewall logs to export*
</font>
  
  
  
Currently, syslog is the only supported firewall log destination.  
  
#### Flow Export  
Flow Export (e.g. NetFlow) can be found under the “Troubleshoot” menu.  
  
Flow Export policies can be configured to allow sending information collected for one or more flows matching each rule to a corresponding receiver. Rules are defined in terms of source and destination IP address and transport port, as well as transport protocol (i.e., 5-tuple). IPFIX is supported as the Flow Export format. The Interval value dictates how often the flow information will be exported. The information provided in the export contains all the current active flows and any new flows matching the rule export definitions.  
  
![image alt text](/images/psmtest/test/5dc9ae7d72066e8ee4b74f1281d19795f657bd17.png)  
<font size='2'>
*Figure 50. Defining a Flow Export Policy*
</font>
  
  
Note: The Target Destination IP address configuration has the following restrictions:  
  
- The destination IP address for the collector cannot be a PSM managed/registered endpoint.
- The destination IP address must be on the same network as the management network used to communicate with PSM, OOB or in-band.
- Only IPv4 addresses are supported for Flow and Mirror collectors.
  
#### Mirror Sessions  
Mirror sessions can be configured for exporting packets through ERSPAN sessions directly from one or more DSCs to an ERSPAN collector:  
  
![image alt text](/images/psmtest/test/73daced4ef12873ccdfa6763a54807d58445ebd2.png)  
  
<font size='2'>
*Figure 51. Configuring Mirror Sessions*
</font>

  
## Platform Management  
### Platform Monitoring  
The GUI offers a Cluster Overview that displays the health and status of the PSM cluster itself and the various admitted DSCs. Platform-wide Events and Alerts are also displayed and managed at the bottom of this page.  
  
Events are displayed for the past day by default. Click on “Past day” to change to a different time scope, as shown in Figure 55.  
  
![image alt text](/images/psmtest/test/40aeb856f6066f6a9424e674d5db4272a074efc4.png)  
<font size='2'>
*Figure 52. Changing time scope for event display*
</font>

  
Alerts can be in an *acknowledged* or *resolved* state. The acknowledged state indicates that the user has seen the alert and is aware of it, but still considers the alert to be active. If the same condition occurs again, no new alert will be created. Alerts in an acknowledged state remain indefinitely.  
  
The resolved state indicates that the user believes that the issue that generated the alert is fixed. If the same condition occurs again, a new alert will be created. Alerts in a resolved state are automatically deleted after 24 hours.  
<font size='1'>

</font>

To acknowledge an alert, hover and click the icon on the right-hand side of the alert item, as shown below. Users can also click multiple checkboxes to resolve multiple alerts at once.  
  
![image alt text](/images/psmtest/test/4dc8e13d5ea117aca5c0c27e49e9fcfa2abeed7c.png)  
  
<font size='2'>
*Figure*
</font>
 *53.  Accessing* <font size='2'>
*the*
</font>
 *alert acknowledgement icon*  
#### Archive Logs  
Events and Audit events can be archived to be downloaded from the PSM and analyzed with other tools or browsed at a later time.  
Archiving is possible by clicking the corresponding export button in the Events and Audit Events screens shown in Figure 48.  
![image alt text](/images/psmtest/test/e9b466b1da82d41ea9d74218047ab507ed94ecc4.png)  
  
![image alt text](/images/psmtest/test/2504df7d3fb1a02e7415cb949d8061d8c9717b2a.png)  
  
<font size='2'>
*Figure*
</font>
 *54.* <font size='2'>
*Exporting*
</font>
 *Events and Audit Events*  
  
The user will be able to specify a name for the archive and optionally a time range for the logs to be exported, as shown in Figure 49.  
  
![image alt text](/images/psmtest/test/c72f1b7dc735c5201d0645d1bbc2285488ba5cb0.png)  
<font size='2'>
*Figure*
</font>
 *55.*  <font size='2'>
*Naming*
</font>
 *the archive containing exported events*  
  
The resulting archive will be available for download in the Archive Log Requests view (shown in Figure 50) accessible through the Archive Logs menu.  
  
![image alt text](/images/psmtest/test/8e3e1942d5ecd8155bd9841fbb44e1944fd74d9c.png)  
<font size='2'>

</font>

<font size='2'>
*Figure*
</font>
 *56.* <font size='2'>
*Archive*
</font>
 *Log Requests list*  
### System Upgrade (Rollout)  
System upgrades of both the PSM controller nodes and DSC firmware are available via the Admin Menu.  
  
The System Upgrade view allows the platform to be upgraded to a new software release. The process is broken into two tasks:  

- Upgrading the PSM cluster itself takes approximately 10 minutes per cluster node. 
- Upgrading each DSC in turn takes approximately 3 minutes.   
  
  
The total DSC upgrade time will depend on the “Strategy” and “Max DSCs” as documented below.  
First, a software bundle must be uploaded into the PSM repository via the ROLLOUT IMAGES button:  
  
![image alt text](/images/psmtest/test/b50d17323d59158b0f4871e39113e9924a59f0a8.png)  
<font size='2'>
*Figure*
</font>
 <font size='2'>
*57*
</font>
*.* <font size='2'>
*Uploading*
</font>
 <font size='2'>
*and*
</font>
 *viewing Rollout Images*  
  
Then click on Upload Image File, select the image file to be uploaded, and click Upload:  
  
![image alt text](/images/psmtest/test/01cfe69ca605a160b2dcc34f87edf9a67470b52c.png)  
<font size='2'>
*Figure 58. Choosing an image to upload*
</font>

<font size='2'>

</font>

![image alt text](/images/psmtest/test/10a6dc548ba2abd30851f0ff832fa1b5702dca42.png)  
<font size='2'>
*Figure 59. Newly uploaded image is available*
</font>

  
  
Once uploaded, the new bundle will show in the Images Repository (as shown in Figure 59), and will now be available to be included in a rollout configuration, created by clicking CREATE ROLLOUT:  
  
![image alt text](/images/psmtest/test/9015c7f321939c29f601dd298ed0c041beada5f7.png)  
<font size='2'>
*Figure 60. The CREATE ROLLOUT button*
</font>
  
  
This will take you to the Rollout configuration:  
  
![image alt text](/images/psmtest/test/881b72385e24a33fcde33109bb65cd561d145a70.png)  
<font size='2'>
*Figure 61. Rollout configuration screen*
</font>

  
To create a rollout policy, first select if the update will involve DSC only, PSM Only, or Both DSC and PSM (Default), then fill out the form:  
  
| **Field** | **Description** |
| --- | --- |
| Name | The name of the rollout policy |
| Version | The version to be used from the repository |
| Start Time | Either a date and time (local time, not UTC), or select Schedule Now |
| End Time | (Optional) The default is for the PSM to upgrade all nodes, regardless of reachability. In the event of any potential upgrade error, the admin can specify a maximum rollout duration. If the End Time is reached and all DSCs have not been upgraded, then PSM will post an error. |
| Strategy | **Linear:** Use the same number of parallel DSC upgrades  <br>**Exponential:** Increase the number of parallel DSC as the update progresses successfully |
| Upgrade Type | **Disruptive:** Update the DSC in real time  <br>**OnNextHostReboot:** Update will be performed the next time a host reboots |
| Max DSCs to upgrade | Maximum number of parallel DSC upgrades |
| Max DSC Failures Allowed | Stop upgrade if the number of DSCs failing the upgrade reaches this number.  <br>This number does not include DSCs that may have encountered upgrade pre-check failures. PSM can retry upgrading DSCs multiple times within an upgrade time window. (Example: an upgrade is scheduled for 3 hours to upgrade 10 DSCs. In case, if there are DSCs that failed to upgrade at the first attempt, the PSM will retry upgrading those DSCs within that 3 hour window.) |
| Upgrade DSCs by label | The PSM also supports a concept of labels for the DSCs, which can be used to upgrade a group of DSCs, for example by application, location or department. |
  
NOTE: PSM nodes should be upgraded before DSCs  
  
Once the form is filled out, select SAVE ROLLOUT; the upgrade will start depending on what was chosen in the schedule Field.  
  
![image alt text](/images/psmtest/test/ff72706123197c795e8d6759ed27303c71951b41.png)  
<font size='2'>
*Figure*
</font>
 *62.* <font size='2'>
*View*
</font>
 *of* <font size='2'>
*pending*
</font>
 <font size='2'>
*rollout*
</font>
  
  
The system will first perform a pre-check to make sure all components are ready for update.  
  
  
![image alt text](/images/psmtest/test/2cbbe7a0bc215164ea8ba8105225d26f702205a1.png)  
  
<font size='2'>
*Figure 63. Rollout status screen*
</font>
  
  
  
The CONTROLLER NODES, CONTROLLER SERVICES, and DSC tabs will show the progress of the upgrade.  
  
Once the pre-check is completed, the system is upgraded.  
  
Depending on the browser being used, a “Refresh” may be required to view the current upgrade status.  
  
### Tech Support  
Tech Support collects various logs and troubleshooting information needed by Pensando Support teams in case of an issue. Individual PSM Controller Nodes and DSCs can be selected.  Pensando Support will provide information on what components of the system (including selecting specific DSCs) may need to be collected.   
Tech Support Requests can be created in the view shown below.  
  
![image alt text](/images/psmtest/test/3b7713e684bfa06290b243575b1d1e956a376616.png)  
  
<font size='2'>
*Figure 64. Tech Support Requests screen*
</font>

  
### Configuration Snapshots  
The PSM configuration can be saved and later restored via “Snapshots”.  A PSM configuration Snapshot can be created in the view shown in Figure 65.  
  
![image alt text](/images/psmtest/test/31f3ca49e64b94ef06242a4eb2dbb51f056d1016.png)  
  
<font size='2'>
*Figure 65. Configuration Snapshots screen*
</font>

  
  
To restore the state of the PSM to an earlier configuration, click the “Restore config” icon corresponding to the snapshot, as shown in Figure 66.  
  
![image alt text](/images/psmtest/test/dc68c9e24e2cc8a44f7662ea94dbdc015659a134.png)  
<font size='2'>
*Figure 66. Accessing the Restore config icon*
</font>
  
  
  
The PSM will be unavailable during the configuration restore process.  
  
Configuration backups are backward compatible: a configuration snapshot taken with an older version of the PSM and DSC software can be restored on a later version of the PSM. Features that were not supported when the snapshot was taken will not be configured upon restore. When a configuration is restored, some time might be required to reconcile external entities; for example, if a workload included in the configuration was changed in the vCenter configuration, the PSM must retrieve the relevant information and update the corresponding object.  
## Managing the PSM via the REST API  
The PSM can be accessed programmatically through a REST API by means of dedicated REST tools such as Postman, or via more basic utilities such as `curl`
.  
The full PSM REST API doc is included in the release as `psd_apidoc.pdf`
.  
Sample Postman Collections are provided within the PSM.  
  
The PSM API facility supports the standard REST GET/POST/PUT/DELETE methods.  
  
Note that when modifying an object with PUT, users *must always* follow a read-modify-write process, i.e. they must GET the entire object, change the fields that they want to modify, and PUT the updated object. Failure to do so may result in errors.    The PSM API does not support the REST PATCH method: if object attributes aren’t provided, then they are not set in the object.  
### API Login Sessions into the PSM  
Login is required for PSM API access, which creates a session cookie to be used for subsequent API calls.  
  
The following login command uses a POST request to create a session cookie and store it in a local file named  “PSM-cookie-jar.txt”:  
`curl -sS -k -j -c ./PSM-cookie-jar.txt -X POST -H 'Content-Type: application/json' --write-out "HTTPSTATUS:%{http_code}" --silent -d  '{"username":"admin","password":"Pensando0$","tenant": "default"}' https://$PSMIPaddr/v1/login`

  
NOTE:  
`curl`

-  is not available on ESXi 6.5 and 6.7 hosts, but these commands can be run from any Linux host on the same subnet as the PSM.
- In this and other examples, `$PSMIPaddr` is assumed to be set to the PSM cluster IP address, or the address of any node in the cluster.
- An example username and password are used above. Please substitute appropriate values for your cluster.
  
### Interpreting Status Payloads  
When creating or querying objects (i.e. “Workloads”, “NetworkSecurityPolicies”), the PSM will return a status payload in a format similar to this example:  
  


```
"status": {
               "propagation-status": {
                   "generation-id": "1",
                   "updated": 0,
                   "pending": 2,
                   "min-version": "",
                   "status": "Propagation pending on: 
                              00ae.cd00.0008, 00ae.cd00.10c8",
                   "pending-dscs": [
                       "00ae.cd00.0008",
                       "00ae.cd00.10c8"
                   ]
               }
           }


```
The status attributes are:  
  
`generation-id`
:  A monotonically increasing version number, maintained by the PSM and incremented each time a given object is changed (i.e. a create/update operation).  
  
`updated`
: The number of DSCs, to which a given policy or object has been pushed or updated with respect to `generation-id`
.  
  
`pending`
: The number of DSCs to which a given policy or object has not yet been pushed or updated with respect to `generation-id`
.  
  
`min-version`
:  The absolute minimum `generation-id`
 that might exist anywhere in the cluster, assuming a non-zero value of `pending`
.   If `pending`
 is 0, then `min-version`
 is null (i.e “”).  
### A Full API Deployment Example: Network Security Policy Configuration  
#### 

- Setup vCenter integration
  
Configure PSM to point to one or more vCenter systems, this will automatically discover the VMs and create workloads. See section <ins>vCenter Integration</ins> for details.  
  
  
Example:  
<font size='2'>

</font>



```
# curl -sS  -k -j -b ./PSM-cookie-jar.txt -X POST   \
     -H "Content-Type: application/json"             \
     -d '{ "kind": null, "api-version": null, "meta": {"name": "DC-1-vCenter", "tenant": null, "namespace": null, "generation-id": null, "resource-version": null, "uuid": null, "labels": null, "self-link": null }, "spec": { "type": "vcenter", "uri":  "dc-1-vcenter.local", "credentials": { "auth-type": "username-password", "username": "admin", "password": "xyz!"}, "login-data": null, "manage-namespaces": [ "all_namespaces" ] } } }' https://$PSMIPaddr/configs/orchestration/v1/orchestrator


```
#### 

- Define an App (optional)
  
An App object defines the network specification for a given application or traffic flow. An App object is needed if a rule requires deep protocol inspection, which is done via the “alg” (application level gateway) option.  App objects are referenced from within a NetworkSecurityPolicy object.  
  
Create an App Object with the name of the application or traffic flow “MyftpApp”:  

- Perform a POST request on ”/configs/workload/v1/apps”
- Specify the following key attributes in the payload:
- "proto-ports": [{ "ports": "<port #>", "protocol": "<protocol>" }]
- "alg": {"type": "<alg type>"}
  
Example:  
  


```
# curl -sS  -k -j -b ./PSM-cookie-jar.txt -X POST   \
     -H "Content-Type: application/json"             \
     -d '{ "api-version": "v1", "meta": { "name": "MyftpApp" }, "spec": { "proto-ports": [ { "protocol": "tcp", "ports": "21" } ], "alg": { "type": "FTP" } } }' https://$PSMIPaddr/configs/security/v1/apps

```
  
Where `$PSMIPaddr`
 is assumed to be set to the PSM cluster IP address.  
  
A user can choose to omit creating an App Objectif ALGs are not used, and include the app-related protocol/port information directly into the rule of the NetworkSecurityPolicy Object.  
  
#### 

- Define a NetworkSecurityPolicy
  
Version 1.*x.y* supports only one type of NetworkSecurityPolicy object for the “default” tenant. The NetworkSecurityPolicy contains firewall rules such as “to” and “from”, “ports”, “protocols” etc. These rules can be defined in the NetworkSecurityPolicy itself or within an App object that is referenced in the NetworkSecurityPolicy. An App object is needed if a rule requires deep packet inspection. The attribute “attach-tenant” controls whether the rule applies to all workloads in the tenant; this example specifies tenant-wide application.  

- Perform a `POST` requestq on /`configs/security/v1/NetworkSecuritypolicy`
- Specify the following key attributes in the payload:<font size='1'>
-
</font> 


```
"tenant": "default"
"attach-tenant": "true"
"apps": [ "MyApp" ]
"action": "PERMIT"
"from-ip-addresses": [ "<ip addresses>” ]
"to-ip-addresses": [ "<ip addresses>” ]
"proto-ports": [{ "ports": "<ports>", "protocol": "<protocol>" }]

```
  
  
  
  
  
  
Example:  


```
curl -sS  -k -j -b ./PSM-cookie-jar.txt -X POST   \
     -H "Content-Type: application/json"             \
     -d '{ "api-version": "v1", "meta": { "name": "nsppolicy1" }, "spec": { "attach-tenant": true, "rules": [ { "action": "PERMIT", "from-ip-addresses": [ "10.0.0.1" ], "to-ip-addresses": [ "10.0.0.2", "10.0.0.4" ], "apps": [ "myftpApp" ] }, { "action": "PERMIT", "from-ip-addresses": [ "10.0.0.2" ], "to-ip-addresses": [ "10.0.0.1", "11.0.0.0/24" ], "proto-ports": [ { "protocol": "tcp", "ports": "100-200" } ] } ] } }' https://$PSMIPaddr/configs/security/v1/NetworkSecuritypolicy

```
  
Where `$PSMIPaddr`
 is assumed to be set to the PSM cluster IP address.  
## Appendix A:  PSM API Payload overview  
The PSM API payload uses standard REST API conventions. The PSM endpoints are accessed over https (port 443) only, using `GET, POST, PUT,`
 and` DELETE`
 methods.    
  
SSL certificate validation may have to be disabled to enable the communication.  
  
The input payload is in JSON format and is modeled after Kubernetes in form and structure, as can be seen in the following example to create a “clusterHost” object:  


```
{
  "kind": "clusterHost",
  "meta": {
    "name": "ae-s7-host"
  },
  "spec": {
    "distributedservicecards": [
      {
        "id": "ae-s7-dsc",
        "mac-address": "000c.2976.5b80"
      }
    ]
  }
}

```
  
The output/return payload will include additional metadata and status as can be seen below:  


```
{
    "kind": "HostList",
    "api-version": "v1",
    "list-meta": {},
    "items": [
        {
            "kind": "Host",
            "api-version": "v1",
            "meta": {
                "name": "ae-s7-host",
                "generation-id": "1",
                "resource-version": "13004",
                "uuid": "533ca06d-ade3-46b5-b43e-a2232c185301",
                "creation-time": "2019-02-15T00:05:24.643553247Z",
                "mod-time": "2019-02-15T00:05:24.643555779Z",
                "self-link": "/configs/cluster/v1/hosts/ae-s7-host"
            },
            "spec": {
                "distributedservicecards": [
                    {
                        "name": "ae-s7-dsc",
                        "mac-address": "000c.2976.5b80"
                    }
                ]
            },
            "status": {}
        }
    ]
}

```
  
Please refer to the *PSM REST API Getting Started Guide* for a comprehensive description of PSM API programming. This guide is available online as part of the PSM distribution and can be accessed at `https://IPaddr/docs/gettingStarted.html`
 .<font size='2'>

</font>

  
### Swagger  
The PSM provides a <ins>Swagger</ins> interface for exploring the PSM API.  
The Swagger endpoints can be explored, based on top-level classification, via:  


```
https://IPaddr/swagger/auth
https://IPaddr/swagger/cluster
https://IPaddr/swagger/events
https://IPaddr/swagger/monitoring
https://IPaddr/swagger/network
https://IPaddr/swagger/search
https://IPaddr/swagger/security
https://IPaddr/swagger/workload

```
### Postman Examples  
<ins>Postman</ins> examples are included in the PSM distribution and are accessible online at  `https://IPaddr/docs/examples/Sample.postman_collection.json`
 .  
The sample collections cover lifecycle/CRUD operations for many of the managed objects used in typical PSM operations. These examples are organized as folders, representing the main use cases that are supported:  
  
![image alt text](/images/psmtest/test/ade946348681fc5acf2e21686ef33713b89bd106.png)  
  
<font size='2'>
*Figure 67. Postman sample collections*
</font>

  
## Appendix B: REST API Examples  
### Save the PSM Security Token  
The following sequence can be used to download a DSC security token, which can then be used to gain direct access to a DSC without relying on the PSM cluster by means of the penctl tool (Please refer to the “Penctl CLI utility” section of the “Pensando Distributed Services Card User Guide” for details).  
  
To get the token and save it in a file called `my_cert.crt`
:  


```
curl -b ./PSM-cookie-jar.txt -s -k "https://$PSMIPaddr/tokenauth/v1/node?Audience=*" | cut -d "\"" -f 4 | awk '{gsub(/\\n/,"\n")}1' > my_cert.crt


```
Where `$PSMIPaddr`
 is assumed to be set to the PSM cluster IP address.  
  
***Note:*** *It is highly recommended to download the DSC Security Token immediately after creating a cluster, and store it in a safe place outside of the PSM, in order to be able to access DSCs in case of a PSM cluster outage or loss of connectivity between DSCs and the PSM.*  
### Admit a DSC into the PSM  
Once a DSC has been configured to contact the PSM, it can be *admitted* into a PSM cluster.  
  
To admit a given DSC, a PUT request must be made to the PSM hostname or address on the corresponding `DistributedServiceCard`
 object. For example, DSC `bob-n1`
 is admitted by making a `PUT`
 request to `/configs/cluster/v1/distributedservicecards/bob-n1:`
  
  


```
{
  "kind": "DistributedServiceCard",
  "meta": {
    "name": "bob-n1"
  },
  "spec": {
                "admit": true
          }
 }

```
  
  
NOTE: The name of the `distributedservicecard`
 object *must correspond* to the `--hostname`
 given when its corresponding DSC was configured to contact the PSM.  
  
NOTE: It may take up to 3 minutes for the DSC to be admitted after the `admit`
 flag in the object has been set to `true`
.  
#### Validation  
To validate the DistributedServiceCard object itself, a GET request can be made on the corresponding object, for example `/configs/cluster/v1/distributedservicecards/bob-n1`

  
The status information returned contains details about the card:  
  


```
"status": {
       "admission-phase": "admitted",
       "conditions": [
           {
               "type": "healthy",
               "status": "true",
               "last-transition-time": "2019-09-09T22:23:15Z"
           }
       ],
       "serial-num": "FLM18420016",
       "primary-mac": "00ae.cd00.10c8",
       "ip-config": {
           "ip-address": "192.168.71.247/22"
       },
       "system-info": {
           "bios-info": {
               "version": "0.15.0-E-21"
           },
           "os-info": {
               "type": "Linux",
               "kernel-release": "4.14.18",
               "processor": "ARMv7"
           },
           "cpu-info": {
               "speed": "2.0 Ghz"
           },
           "memory-info": {
               "type": "hbm"
           },
           "storage-info": {
               "devices": [
                   {
                       "serial-num": "0x07ceb35a",
                       "type": "MMC",
                       "capacity": "14942208 Bytes",
                       "percent-life-used-A": 10,
                       "percent-life-used-B": 10
                   }
               ]
           }
       },
       "interfaces": [
           "lo",
           "bond0",
           "inb_mnic0",
           "inb_mnic1",
           "int_mnic0",
           "oob_mnic0"
       ],
       "DSCVersion": "0.15.0-E-21",
       "DSCSku": "68-0003-02 01",
       "host": "bob-n1"
   }

```
  
  
To verify admission by the PSM, perform a `GET`
 request on the list of DistributedServiceCard objects (`/configs/cluster/v1/distributedservicecards`
<font size='1'>
)
</font> 
or on an individual DistributedServiceCard object <font size='1'>
(
</font>
`/configs/cluster/v1/distributedservicecards/bob-n1`
<font size='1'>
)
</font> 

<font size='1'>

</font>

The `admission-phase`
 key in the return payload should have the value “`admitted”,`
as shown below:  


```
{
    "kind": "DistributedServiceCard",
    "api-version": "v1",
    "meta": {
        "name": "bob-n1",
        "generation-id": "2",
        "resource-version": "110165",
        "uuid": "ea10c723-8840-48cf-841a-ce034ff19988",
        "creation-time": "2019-02-15T21:11:46.008703832Z",
        "mod-time": "2019-02-15T21:41:44.843962863Z",
        "self-link": "/configs/cluster/v1/distributedservicecards/bob-n1"
    },
    "spec": {
        "admit": true,
        "hostname": "bob-n1",
        "ip-config": {
            "ip-address": "10.0.0.11/24"
        },
        "mgmt-mode": "NETWORK",
        "network-mode": "OOB",
        "controllers": [
            "192.168.71.52"
        ]
    },
    "status": {
        "admission-phase": "admitted",
        "serial-num": "0x0123456789ABCDEFghijk",
        "distributedservicecardsVersion": "ver1",
        "distributedservicecardsSku": "DSC1"
    }
}

```
  
NOTE:  **A system reboot is required to complete PSM registration**.  Once the host is rebooted,  “`penctl show DSC -a my_cert.crt”`
 should present:  
  


```
"transition-phase": "PSM_REGISTRATION_DONE",


```
where `my_cert.crt`
 is a file containing the DSC Security Token previously downloaded as described in section <ins>Save the PSM Security Token</ins>. After a DSC has been admitted to the cluster, the `penctl`
 command will not work without a valid security token.  
### Create a Host Object  
To create a Host object with the host name `bob-n1`
 and the MAC address of the DSC card, perform a POST request on `/configs/cluster/v1/hosts`
 with these attributes in the payload:  


```
"name": "bob-n1"
"mac-address": "MAC address of DSC card"



```
Example<font size='1'>
:
</font>



```
curl -sS  -k -j -b ./PSM-cookie-jar.txt -X POST      \
     -H "Content-Type: application/json"                \
     -d '{ "api-version": "v1", "meta": { "name": "bob-n1" }, "spec": { "dscs": [ { "mac-address": "00ae.cd00.1958" } ] } }' https://$PSMIPaddr/configs/cluster/v1/hosts


```
Where `$PSMaddr`
 is assumed to be set to the PSM cluster IP address.  
  
Alternatively, it is possible to specify the DSC associated with the host by providing the ID of the DSC:  


```
curl -sS  -k -j -b ./PSM-cookie-jar.txt -X POST      \
     -H "Content-Type: application/json"                \
     -d '{ "api-version": "v1", "meta": { "name": "bob-n1" }, "spec": { "dscs": [ { "id": "dsc-0" } ] } }' https://$PSMIPaddr/configs/cluster/v1/hosts
```
  
  
### Configure Logging  
Alert monitoring and logging can be configured to target `syslog`
 i.e., to be exported in syslog format suitable for consumption by a syslog collector.  
  
Example: ExportThe following example illustrates exporting to syslog all Alerts generated.  
Perform a POST request  to `/configs/monitoring/v1/alertDestinations`

with the following payload:  


```
{
    "kind": "AlertDestination",
    "api-version": "1",
    "meta": {
        "name": "syslog-export",
        "tenant": "default",
        "namespace": "default"
    },
    "spec": {
        "syslog-export": {
            "format": "SYSLOG_BSD",
            "targets": [{
                "destination": "10.0.0.67:10344",
                "transport": "udp"
            }],
            "config": {
                "prefix": "pen-events",
                "facility-override": "LOG_USER"
            }
        }

    }
}

```
### Decommissioning a DSC  
If a DSC needs to be removed from PSM control (known as *decommissioning* the DSC), perform a PUT request on the corresponding `distributedservicecards`
 object to  set its `mgmt-mode`
 key to the value `HOST`
.  
  
Example payload for a PUT request to `/configs/cluster/v1/distributedservicecards/00ae.cd00.0008:`
  
  


```
{
  "kind": "DistributedServiceCard",
  "meta": {
    "name": "00ae.cd00.0008"
  },
  "spec": {
                "mgmt-mode": "HOST"
            }
 }

```
  
Reboot of the host is required after decommissioning a DSC for the DSC to move to host-managed mode.  
  
Decommissioning can be useful in various scenarios, such as:  
  
- Removing a card to return it (RMA: Return Merchandise Authorization):
- Change the mode to `HOST` to decommission. 
- The card can be RMAed.
- Decommissioning and not Readmitting a card (Host Managed) :
- Change the mode to `HOST` to decommission.
- Make sure to set the PSM to not autoadmit DSCs
- Reboot host
- User wants the DSC to move to a less feature-rich DSC Profile (e.g. SmartNIC):
- Change the mode to `HOST` to decommission.
- Change the feature set by assigning a different DSC profile to the card or associating a different Feature Set to the DSC profile assigned to the card.Reboot to start the PSM auto discovery & sets Spec.admit == true
  
  
## Appendix C:  PSM Admission Policy  
The default PSM Admission policy depends on how the PSM Cluster was initialized but can always be changed after the fact.  
  
To view the state of the PSM Admission policy, perform a `GET`
 request on the `/configs/cluster/v1/cluster`
 endpoint; the return payload will include the current value of the key `auto-admit-dscs`
 :  
  


```
{
    "kind": "Cluster",
    "api-version": "v1",
    "meta": {
        "name": "testCluster",
        [...]
        "self-link": "/configs/cluster/v1/cluster"
    },
    "spec": {
        "quorum-nodes": [
            "192.168.71.52"
        ],
        "virtual-ip": "192.168.71.52",
        "ntp-servers": [
            "1.pool.ntp.org",
            "2.pool.ntp.org"
        ],
        "auto-admit-dscs": true
    },
    "status": {
        "leader": "192.168.71.52",
        [...]
        "auth-bootstrapped": true
    }
}

```
  
  
To change the` auto-admit-dscs`
 policy, perform a PUT request on the `/configs/cluster/v1/cluster`
 endpoint, making sure to include all relevant aspects of the cluster object:  


```
{
    "kind": "Cluster",
    "api-version": "v1",
    "meta": {
        "name": "testCluster"
    },
    "spec": {
        "quorum-nodes": [
            "192.168.71.52"
        ],
        "virtual-ip": "192.168.71.52",
        "ntp-servers": [
            "1.pool.ntp.org",
            "2.pool.ntp.org"
        ],
        "auto-admit-dscs": false
    }
 } 
```
  
## Appendix D:  PSM Authentication Bootstrap  
The PSM’s Authentication subsystem requires a bootstrapping, involving the following steps:  
  
- Create the “default” tenant.
- Create the “AdminRoleBinding” object.
- Create the “AuthenticationPolicy” object.
- Create the default “admin” User object.
- Post the “AuthBootstrapComplete” status to the Cluster object.
  
  
Validation can be achieved either by logging in to the GUI or via Postman as the “admin” user.  
  
These steps are automated by the `bootstrap_PSM.py`
 utility, which should be used for this process. This appendix is included for informational purposes only.  
  
## Appendix E: PSM Access Control  
The PSM provides Access Control mechanisms for Local User, LDAP and RADIUS, including management of User, Role and RoleBinding objects.  
  
Examples for Access Control configuration are provided in the PSM, within the online docs section.  
  
Please refer to the Pensando Sample PSM Postman Collection for examples, within the “Users, Authentication and Radius” folder.  
  
## Appendix F: Staging Buffer  
When making REST API calls, a *staging buffer* can be used to submit multiple calls in a single operation. This example demonstrates creating multiple security policies at once:  
  
- Create a staging buffer with a name, for example “TestBuffer”
- Perform `POST` on the `”/configs/staging/v1/buffers”`
- With key attributes in the payload:


```
"namespace": "default"
"tenant": "default"
```
- 
- Create one or more App objects (by repeating this step) in the staging buffer
- Perform `POST` on the `”/staging/TestBuffer/security/v1/apps”`
- With the key attributes in payload:


```
"namespace": "default"
"tenant": "default"
"proto-ports": [{ "ports": "<port #>", "protocol": "<protocol>" }]

```
- Create or modify the NetworkSecurityPolicy (this is a POST example, use PUT to modify)
- Perform a `POST` request on ` /staging/TestBuffer/security/v1/NetworkSecuritypolicies`
- With key attributes in payload:


```
"namespace": "default"
"tenant": "default"
"attach-tenant": "true"
"apps": [ "MyApp" ]
"action": "PERMIT"
"from-ip-addresses": [ "<ip addresses>” ]
"to-ip-addresses": [ "<ip addresses>” ]
"proto-ports": [{ "ports": "<ports>", "protocol": "<protocol>" }]

```
- Verify the staging buffer
- Perform a `GET` request on  `/configs/staging/v1/buffers/TestBuffe`<font size='1'>
- r
</font>
- Commit the staging buffer
- Perform a  `POST` request on` /configs/staging/v1/buffers/TestBuffer/commit`
- Reuse or delete the staging buffer. After a successful commit, the staging buffer is empty and ready to be used again, or it can be deleted. Deletion example:
- Perform a `DEL` request on `/configs/staging/v1/buffers/TestBuffe`<font size='1'>
- r
</font>
##   
##   
## Appendix G: PSM Operational Network Ports  
  
These ports must be opened in each direction in order for the PSM cluster to function correctly.  
  
  
| <font size='2'><br>**TCP Port**<br></font><br><font size='2'><br><br></font> | <font size='2'><br>**Service**<br></font><br><font size='2'><br><br></font> |
| --- | --- |
| **From user station to PSM node** | <font size='1'><br><br></font> |
| <font size='2'><br>22<br></font> | <font size='2'><br>sshd (for node management)<br></font> |
| <font size='2'><br>80<br></font> | <font size='2'><br>redirects to 443<br></font> |
| <font size='2'><br>443<br></font><br><font size='2'><br><br></font> | <font size='2'><br>ApiGw HTTPS<br></font><br><font size='2'><br><br></font> |
| <font size='2'><br>9001<br></font><br><font size='2'><br><br></font> | <font size='2'><br>Initial POST for cluster bootstrap<br></font><br><font size='2'><br><br></font> |
| **From PSM node to PSM node** | <font size='1'><br><br></font> |
| <font size='2'><br>5001<br></font><br><font size='2'><br><br></font> | <font size='2'><br>etcd (peer)<br></font><br><font size='2'><br><br></font> |
| <font size='2'><br>5002<br></font><br><font size='2'><br><br></font> | <font size='2'><br>etcd (client)<br></font><br><font size='2'><br><br></font> |
| <font size='2'><br>6443<br></font><br><font size='2'><br><br></font> | <font size='2'><br>Kubernetes APIServer<br></font><br><font size='2'><br><br></font> |
| <font size='2'><br>7000<br></font><br><font size='2'><br><br></font> | <font size='2'><br>Citadel<br></font><br><font size='2'><br><br></font> |
| <font size='2'><br>7087<br></font><br><font size='2'><br><br></font> | <font size='2'><br>Citadel Query<br></font><br><font size='2'><br><br></font> |
| <font size='2'><br>9002<br></font><br><font size='2'><br><br></font> | <font size='2'><br>Cluster management<br></font><br><font size='2'><br><br></font> |
| <font size='2'><br>9003<br></font><br><font size='2'><br><br></font> | <font size='2'><br>ApiServer<br></font><br><font size='2'><br><br></font> |
| <font size='2'><br>9004<br></font><br><font size='2'><br><br></font> | <font size='2'><br>Orchestrator Hub<br></font><br><font size='2'><br><br></font> |
| <font size='2'><br>9009<br></font><br><font size='2'><br><br></font> | <font size='2'><br>Resolver<br></font><br><font size='2'><br><br></font> |
  
  
| <font size='2'><br>**TCP Port**<br></font><br><font size='2'><br><br></font> | <font size='2'><br>**Service**<br></font><br><font size='2'><br><br></font> |
| --- | --- |
| **From PSM node to PSM node (cont’d)**<font size='2'><br><br></font> | <font size='2'><br><br></font> |
| <font size='2'><br>9010<br></font><br><font size='2'><br><br></font> | <font size='2'><br>EventsManager<br></font><br><font size='2'><br><br></font> |
| <font size='2'><br>9011<br></font><br><font size='2'><br><br></font> | <font size='2'><br>Spyglass<br></font><br><font size='2'><br><br></font> |
| <font size='2'><br>9012<br></font><br><font size='2'><br><br></font> | <font size='2'><br>EventsProxy<br></font><br><font size='2'><br><br></font> |
| <font size='2'><br>9014<br></font><br><font size='2'><br><br></font> | <font size='2'><br>CMD Leader Services<br></font><br><font size='2'><br><br></font> |
| <font size='2'><br>9015<br></font><br><font size='2'><br><br></font> | <font size='2'><br>Rollout<br></font><br><font size='2'><br><br></font> |
| <font size='2'><br>9020<br></font><br><font size='2'><br><br></font> | <font size='2'><br>TPM<br></font><br><font size='2'><br><br></font> |
| <font size='2'><br>9030<br></font><br><font size='2'><br><br></font> | <font size='2'><br>TSM<br></font><br><font size='2'><br><br></font> |
| <font size='2'><br>9051<br></font><br><font size='2'><br><br></font> | <font size='2'><br>VOS<br></font><br><font size='2'><br><br></font> |
| <font size='2'><br>9200<br></font><br><font size='2'><br><br></font> | <font size='2'><br>Elastic (client)<br></font> |
| <font size='2'><br>9300<br></font><br><font size='2'><br><br></font> | <font size='2'><br>Elastic (peer)<br></font> |
| <font size='2'><br>10250<br></font><br><font size='2'><br><br></font> | <font size='2'><br>Kubelet<br></font><br><font size='2'><br><br></font> |
| <font size='2'><br>10257<br></font><br><font size='2'><br><br></font> | <font size='2'><br>Kubernetes Controller Manager<br></font><br><font size='2'><br><br></font> |
| <font size='2'><br>10259<br></font><br><font size='2'><br><br></font> | <font size='2'><br>Kubernete Scheduler<br></font><br><font size='2'><br><br></font> |
| <font size='2'><br>10777<br></font><br><font size='2'><br><br></font> | <font size='2'><br>Citadel Collector<br></font><br><font size='2'><br><br></font> |
| <font size='2'><br>19001<br></font><br><font size='2'><br><br></font> | <font size='2'><br>Minio<br></font> |
| **From PSM to DSC and from management station to PSM** | <font size='1'><br><br></font> |
| <font size='2'><br>8888<br></font><br><font size='2'><br><br></font> | <font size='2'><br>agent reverse proxy for<br></font> <br>`penctl`<br><font size='2'><br> and diagnostics<br></font><br><font size='2'><br><br></font> |
  
  
| <font size='2'><br>**TCP Port**<br></font><br><font size='2'><br><br></font> | <font size='2'><br>**Service**<br></font><br><font size='2'><br><br></font> |
| --- | --- |
| **From DSC to PSM** | <font size='1'><br><br></font> |
| <font size='2'><br>9005<br></font><br><font size='2'><br><br></font> | <font size='2'><br>NPM<br></font><br><font size='2'><br><br></font> |
| <font size='2'><br>9009<br></font><br><font size='2'><br><br></font> | <font size='2'><br>Resolver<br></font><br><font size='2'><br><br></font> |
| <font size='2'><br>9010<br></font><br><font size='2'><br><br></font> | <font size='2'><br>EventsManager<br></font><br><font size='2'><br><br></font> |
| <font size='2'><br>9012<br></font><br><font size='2'><br><br></font> | <font size='2'><br>EventsProxy<br></font><br><font size='2'><br><br></font> |
| <font size='2'><br>9014<br></font><br><font size='2'><br><br></font> | <font size='2'><br>CMD Health Updates<br></font><br><font size='2'><br><br></font> |
| <font size='2'><br>9015<br></font><br><font size='2'><br><br></font> | <font size='2'><br>Rollout<br></font><br><font size='2'><br><br></font> |
| <font size='2'><br>9019<br></font><br><font size='2'><br><br></font> | <font size='2'><br>NIC Registration<br></font><br><font size='2'><br><br></font> |
| <font size='2'><br>9020<br></font><br><font size='2'><br><br></font> | <font size='2'><br>TPM<br></font><br><font size='2'><br><br></font> |
| <font size='2'><br>9030<br></font><br><font size='2'><br><br></font> | <font size='2'><br>TSM<br></font><br><font size='2'><br><br></font> |
| <font size='2'><br>9051<br></font><br><font size='2'><br><br></font> | <font size='2'><br>VOS<br></font><br><font size='2'><br><br></font> |
| <font size='2'><br>10777<br></font><br><font size='2'><br><br></font> | <font size='2'><br>Citadel Collector<br></font><br><font size='2'><br><br></font> |
  
## Appendix H: Changing the PSM VM Password  
Non-admin users should never access the PSM VMs that make up the PSM cluster. In the event that a system administrator wants to change and persist the “root” user password for these VMs, use the command:  
  
`config_PSM_networking.py -p <new_password>`

<font size='1'>

</font>

The root password can also be changed using the standard “`passwd`
” command, but the change will not be persisted unless the command is followed by an invocation of the “`pensave-config.sh`
” script.  
  
  
## Appendix I:  ISC DHCP Server Option 60 and 43 Example  
  
  
ISC DHCP Configs for Option 60 Request and Option 43 Response.  
  


```
option space pensando;
option pensando.wlc code 241 = array of ip-address;

  class "PensandoClass" {
    match if option vendor-class-identifier = "Pensando";
    vendor-option-space pensando;
    option pensando.wlc  1.1.1.1,2.2.2.2;
  }

```
  
## Appendix J: RADIUS Authentication for PSM  
  
To use RADIUS authentication for the PSM, add the below dictionary as part of the RADIUS configuration.  
  


```
##
root@kickseed:/etc/freeradius/3.0# cat dictionary.pensando
######################################################################
#
#       Pensando FreeRADIUS dictionary
#
#
#
######################################################################

VENDOR          Pensando                        51886

BEGIN-VENDOR    Pensando

ATTRIBUTE       Pensando-User-Group                     1       string
ATTRIBUTE       Pensando-Tenant                         2       string

END-VENDOR      Pensando
root@kickseed:/etc/freeradius/3.0#
root@kickseed:/etc/freeradius/3.0# cat dictionary | grep pensando
$INCLUDE dictionary.pensando
root@kickseed:/etc/freeradius/3.0#
##

```
  
Below is sample user syntax defined as part of RADIUS configuration.  
..  
pen123  Cleartext-Password := "pen123"  
        Pensando-User-Group = "NetworkAdmin",  
        Pensando-Tenant = "default"  
pen456  Cleartext-Password := "pen456"  
        Pensando-Tenant = "default"  
..  
  
  
##   
## Appendix K: ESXi Sequence for Upgrading the DSC Firmware and Associating it to a PSM  
  
The `esx-pencli.pyc`
 module is provided for the following tasks:  

- Ensuring that the DSC firmware is running the 1.8.0 version
- Moving the DSC from “host” to “network” managed mode
  
  
#### Prerequisites and Assumptions  

- First time installation of Pensando DSC
- If the system has been previously commissioned with release 1.1.1, then run: 
  
`[root] esxcli software vib remove -n ionic-en`

- SSH access enabled for ESXi host
- The ESXi host is in maintenance mode and reboots are allowed.
- Permanent storage available.  Ex:  “mkdir /vmfs/volumes/<datastore-name>/pnso-1.3.2” 
  
<font size='2'>

</font>

#### Steps for Upgrading Firmware and Associating to a PSM  
<font size='2'>

</font>

<font size='2'>

- Temporarily disable the firewall:
</font>`[root]` `esxcli network firewall set -e 0`
<font size='2'>
- Copy drivers, firmware and
</font> `esx-pencli.pyc` <font size='2'>
- to persistent storage on the ESXi host. Example:
</font>`[root] scp drivers/ionic-en-1.3-1OEM.670.0.0.8169922.x86_64.vib drivers/ionic-en-1.3-1OEM.650.0.0.4598673.x86_64.vib utils/pencli/esx-pencli.pyc fw/DSC_fw.tar and esx-pencli.pyc to ESX host in /vmfs/volumes/<datastore-name>/pnso-1.3`
<font size='2'>
- Install the ESXi VIB/drivers.   Example:
</font>

```
[root]  esxcli software vib install -v file:///vmfs/volumes/<datastore-name>/pnso-1.3/drivers/ionic-en-1.3-1OEM.670.0.0.8169922.x86_64.vib -f
[root] reboot

```
<font size='2'>
- Verify installation:  
</font>`[root] esxcli network nic list | grep Pensando`
<font size='2'>
- Ensure DSC is running 1.3.2 Firmware.   Example:   
</font>

```
[root] python esx-pencli.pyc upgrade_dsc --fw_img /vmfs/volumes/<datastore-name>/pnso-1.3/fw/DSC_fw.tar
[root] reboot

```
<font size='2'>
- Associate to PSM
</font><font size='2'>
- , as per “Command syntax examples” below
</font>
`[root] reboot`
<font size='2'>
- Re-enable the firewall, if desired:
</font>  
`[root] esxcli network firewall set -e 1`
  
#### Command Syntax Examples for Associating a DSC to a PSM  
<font size='2'>
The specific command for associating a DSC to a PSM depends on whether the DSC management IP address is assigned statically or provided by DHCP, and on whether DSC management is done inband or via the OOB interface.  The
</font> 
`esx-pencli.pyc`
<font size='2'>
 command is detailed below with examples for all four possible permutations.
</font>

<font size='2'>

</font>

<font size='2'>

- DHCP with Inband management:
</font>
  


```
[root] python esx-pencli.pyc change_dsc_mode --config_opt dhcp --management_network inband --dsc_id bm18-ucs-100g-a.pensando.io --verbose
Changing DSC mode
Status: 200 and reason: OK
Pensando DSC mode has been changed to network managed successfully, please reboot the host
[root]

```
<font size='2'>

</font>

<font size='2'>

- DHCP with OOB management:
</font>
  


```
[root] python esx-pencli.pyc change_dsc_mode --config_opt dhcp --management_network oob --dsc_id bm18-ucs-100g-a.pensando.io --verbose
Changing DSC mode
Status: 200 and reason: OK
Pensando DSC mode has been changed to network managed successfully, please reboot the host
[root]

```
<font size='2'>

</font>

<font size='2'>

- Static with in-band management:
</font>
  


```
[root] python esx-pencli.pyc change_dsc_mode --config_opt static --mgmt_ip 20.0.1.18/24 --gw 20.0.1.254  --management_network inband --dsc
_id bm18-ucs-100g-a.pensando.io --controllers 20.0.1.61,20.0.1.62,20.0.1.63 --verbose
Changing DSC mode
Status: 200 and reason: OK
Pensando DSC mode has been changed to network managed successfully, please reboot the host
[root]

```
<font size='2'>

</font>

<font size='2'>

- Static with OOB management:
</font>
  


```
[root] python esx-pencli.pyc change_dsc_mode --config_opt static --mgmt_ip 20.0.1.18/24 --gw 20.0.1.254  --management_network oob --dsc
_id bm18-ucs-100g-a.pensando.io --controllers 20.0.1.61,20.0.1.62,20.0.1.63 --verbose
Changing DSC mode
Status: 200 and reason: OK
Pensando DSC mode has been changed to network managed successfully, please reboot the host
[root]

```
<font size='2'>

</font>

  
<font size='2'>

</font>

## Appendix L: Removing a DSC Driver Froman ESXi Host  
In the event that the DSC driver needs to be removed from a host, follow these steps:  
  


```
[root] esxcli software vib remove -n ionic-en
Removal Result
Message: The update completed successfully, but the system needs to be rebooted
for the changes to be effective.
Reboot Required: true
VIBs Installed:
VIBs Removed: VMW_bootbank_ionic-en_0.1-1vmw.670.0.0.8169922
VIBs Skipped:

```
  
## Appendix M: Installing the PSM on a KVM Cluster  
This section provides a more detailed guide to the PSM installation procedure on KVM hosts. In this example, two servers running CentOS 7.6 with KVM support host three PSM cluster nodes. (Pensando recommends that the three PSM cluster nodes should be distributed across multiple servers). Server requirements are specified in the document *Enterprise PSM Design Best Practices*.  
![image alt text](/images/psmtest/test/f1bcc082ab1cb9def88887e545f4734acaf748f0.png)<font size='2'>

</font>

<font size='2'>
*Figure 68. A recommended PSM cluster configuration*
</font>
  
  
<font size='2'>

</font>

In this example, the network configuration is assumed to be:  
<font size='2'>

</font>

<font size='2'>

- VLAN 5: Management Network → 10.29.5.0/24
</font>
<font size='2'>
- Server1: 10.29.5.103
</font>
<font size='2'>
- Server2: 10.29.5.104
</font>
<font size='2'>
- VLAN 11:  PSM Management Network → 10.29.11.0/24
</font>
<font size='2'>
- PSM-N1: 10.29.11.21
</font>
<font size='2'>
- PSM-N2: 10.29.11.22
</font>
<font size='2'>
- PSM-N3: 10.29.11.23
</font>
  
#### Networking Configuration  
Next, configure the needed network bridges for access to the CentOS server and for the PSM. The Top-of-Rack switch is configured to be a trunk interface that has set the “native-vlan” for both servers to be on VLAN 5 that also allows VLAN 11 to traverse the interface. Figure 69 shows how to create bridge interfaces that will be used by the virtual machine running a PSM node. Since in this environment there is only one network interface, create a bridge interface that will allow communication to the CentOS server.  
<font size='2'>

</font>

![image alt text](/images/psmtest/test/44814255e8d79d1b05dcc2c0e1d1ed4cddb2b179.png)<font size='2'>

</font>

<font size='2'>
*Figure 69.*
</font> 
<font size='2'>
*Bridge interface for a PSM node*
</font>
<font size='2'>

</font>

<font size='2'>

</font>

##### Network Interface Configuration  
Make sure the VLAN module is loaded for this server, with the command:  
<font size='2'>

</font>

<font size='1'>

</font>



```
[root]# modprobe --first-time 8021q
modprobe: ERROR: could not insert '8021q': Module already in kernel

```
<font size='2'>

</font>

If the above error message is returned, then the VLAN tagging module was already loaded.  If there is no error message, the module has now been successfully loaded.  
<font size='2'>

</font>

Create a bridge interface named `br0`
 that links interface `eno5`
, which is an active interface on the server. This is done by modifying interface `eno5`
 in the configuration file `/etc/sysconfig/network-scripts/ifcfg-eno5`
:  
<font size='2'>

</font>

<font size='1'>

</font>



```
[root@server1 ~]# cat /etc/sysconfig/network-scripts/ifcfg-eno5
# Generated by dracut initrd
NAME="eno5"
DEVICE="eno5"
ONBOOT=yes
NETBOOT=yes
UUID="ee73d6e6-60a2-4239-b21c-036c00cd6493"
IPV6INIT=yes
BOOTPROTO=static
TYPE=Ethernet
#IPADDR=10.29.5.103
#GATEWAY=10.29.5.1
#NETMASK=255.255.255.0
#DNS1=10.29.5.9
#DNS2=8.8.8.8
#DOMAIN=training.local
BRIDGE=br0


```
<font size='2'>

</font>

<font size='2'>
Note that the IP address, gateway, netmask, DNS, and domain entries are commented out, and the entry
</font>
` BRIDGE=br0`
<font size='2'>
 is added.  This will link the
</font> 
`br0`
 <font size='2'>
interface to
</font> 
`eno5`
<font size='2'>
.
</font>

<font size='2'>

</font>

<font size='2'>
Create the configuration file
</font> 
`/etc/sysconfig/network-scripts/ifcfg-br0`
<font size='2'>
 for interface
</font> 
`br0`
<font size='2'>
:
</font>

<font size='2'>

</font>



```
[root@server1 ~]# cat /etc/sysconfig/network-scripts/ifcfg-br0 
DEVICE=br0
TYPE=Bridge
BOOTPROTO=static
IPADDR=10.29.5.103
NETMASK=255.255.255.0
GATEWAY=10.29.5.1
DNS1=10.29.5.9
DNS2=8.8.8.8
DOMAIN=training.local
ONBOOT=yes
DELAY=0

```
<font size='2'>

</font>

<font size='2'>
Now that these configuration files have been entered, run the following command to restart the network and verify that you can access the CentOS system
</font> 
`server1`
<font size='2'>
.
</font> 

`[root@server1 ~]# systemctl restart network`
<font size='1'>

</font> 

<font size='1'>

</font>

<font size='1'>
**Note:**
</font>
<font size='1'>
 You may lose network connectivity and may have to re-log back into the server.
</font>

<font size='2'>

</font>

<font size='2'>
Log back into the server and check/verify the network interfaces.
</font>

<font size='2'>

</font>



```
[root@server1 ~]# ip addr show
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default qlen 1000
    link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
    inet 127.0.0.1/8 scope host lo
       valid_lft forever preferred_lft forever
    inet6 ::1/128 scope host 
       valid_lft forever preferred_lft forever
2: eno5: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc mq master br0 state UP group default qlen 1000
    link/ether 48:df:37:8f:d5:c8 brd ff:ff:ff:ff:ff:ff
    inet6 fe80::4adf:37ff:fe8f:d5c8/64 scope link 
       valid_lft forever preferred_lft forever
3: eno6: <BROADCAST,MULTICAST> mtu 1500 qdisc noop state DOWN group default qlen 1000
    link/ether 48:df:37:8f:d5:c9 brd ff:ff:ff:ff:ff:ff
4: eno7: <BROADCAST,MULTICAST> mtu 1500 qdisc noop state DOWN group default qlen 1000
    link/ether 48:df:37:8f:d5:ca brd ff:ff:ff:ff:ff:ff
5: eno8: <BROADCAST,MULTICAST> mtu 1500 qdisc noop state DOWN group default qlen 1000
    link/ether 48:df:37:8f:d5:cb brd ff:ff:ff:ff:ff:ff
6: br0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP group default qlen 1000
    link/ether 48:df:37:8f:d5:c8 brd ff:ff:ff:ff:ff:ff
    inet 10.29.5.103/24 brd 10.29.5.255 scope global br0
       valid_lft forever preferred_lft forever
    inet6 fe80::4adf:37ff:fe8f:d5c8/64 scope link 
       valid_lft forever preferred_lft forever
7: virbr0: <NO-CARRIER,BROADCAST,MULTICAST,UP> mtu 1500 qdisc noqueue state DOWN group default qlen 1000
    link/ether 52:54:00:8c:e5:f9 brd ff:ff:ff:ff:ff:ff
    inet 192.168.122.1/24 brd 192.168.122.255 scope global virbr0
       valid_lft forever preferred_lft forever
8: virbr0-nic: <BROADCAST,MULTICAST> mtu 1500 qdisc pfifo_fast master virbr0 state DOWN group default qlen 1000
    link/ether 52:54:00:8c:e5:f9 brd ff:ff:ff:ff:ff:ff

```
<font size='1'>

</font>

<font size='2'>
**Note:**
</font>
<font size='2'>
  Now interface
</font> 
`br0`
<font size='2'>
, not
</font> 
`eno5`
<font size='2'>
, has the CentOS server1 management IP address.
</font>

  
Next, create the interfaces that will be used for the PSM, that will reside on VLAN 11.  Create the interface that is linked to the physical interface, which in this example is `eno5`
.  The syntax to create an interface with a VLAN tag is `interface.VLANID`
.  In this example, the interface file will be `eno5.11`
.   This interface will be bridged to the bridge interface, (called `br11`
 in this example).  Create these two network interface files in the directory `/etc/sysconfig/network-scripts/`
 .  
<font size='2'>

</font>

<font size='2'>
The filenames will be
</font> 
`ifcfg-eno5.11`
<font size='2'>
 and
</font> 
`ifcfg-br11`
<font size='2'>
.
</font>

<font size='2'>

</font>



```
[root@server1 ~]# cat /etc/sysconfig/network-scripts/ifcfg-eno5.11 
DEVICE=eno5.11
BOOTPROTO=none
ONBOOT=yes
USERCTL=no
VLAN=yes
BRIDGE=br11
NM_CONTROLLED=no
DELAY=0


```
<font size='2'>
**Note:**
</font>
<font size='2'>
  For this example, the
</font> 
`VLAN`
<font size='2'>
 entry must be set to
</font> 
`yes`
<font size='2'>
 and the bridge interface should point to the
</font> 
`br11`
<font size='2'>
 interface.
</font>

<font size='2'>

</font>



```
[root@server1 ~]# cat /etc/sysconfig/network-scripts/ifcfg-br11 
DEVICE=br11
TYPE=Bridge
ONBOOT=yes
BOOTPROTO=none
NM_CONTROLLED=no
DELAY=0

```
<font size='2'>

</font>

<font size='2'>
Once these two files are created, restart the network service.
</font>

<font size='2'>

</font>

`[root@server1 ~]# systemctl restart network`
 
<font size='2'>

</font>

<font size='2'>
Check the interfaces for the server:
</font>

<font size='2'>

</font>

`[root@server1 ~]# ip addr show`

<font size='2'>

</font>

<font size='2'>
The interfaces
</font> 
`eno5.11`
<font size='2'>
 and
</font> 
`br11`
 <font size='2'>
have now been created.  Interface
</font> 
`br11`
 <font size='2'>
will be used for the PSM virtual machines.
</font>

<font size='2'>
You can also run the following command to check the bridge interfaces.
</font>

<font size='2'>

</font>



```
[root@server1 ~]# brctl show
bridge name	bridge id		STP enabled	interfaces
br0		8000.48df378fd5c8	no		eno5
br11		8000.48df378fd5c8	no		eno5.11
virbr0	8000.5254008ce5f9	yes		virbr0-nic

```
<font size='2'>

</font>

<font size='2'>

</font>

<font size='2'>
Repeat the above steps to deploy the second and third servers.
</font>

#### Installation of PSM Nodes  
Now that the servers are prepared with the appropriate resources and network configurations, install the PSM software:  
<font size='2'>

</font>

<font size='2'>

- Deploy each PSM node
</font>
<font size='2'>
- Set networking for the nodes
</font>
<font size='2'>
- Bootstrap the PSM cluster
</font>
  
<font size='2'>

</font>

To deploy the PSM, first download the `psm.qcow2`
 image to the CentOS server.  In this example, PSM node 1 will be deployed on server1, PSM node 2 will be deployed on server2 and PSM node 3 will be deployed on server3.  Each PSM node will require its own image, even though these images are copies of the same file.  
#### Deploying PSM Nodes  
<font size='2'>
In this example, a directory is created on the servers under
</font> 
`/root/kvm/images/1.7.0-9`
<font size='2'>
.  Follow the steps below to deploy the PSM nodes.
</font>

<font size='2'>

</font>

<font size='2'>

- Copy the file
</font> `psm.qcow2`<font size='2'>
-  onto server1, server2 and server3
</font>
<font size='2'>
- Copy
</font> `psm.qcow2`<font size='2'>
-  to a new image file on server 1→ ex: pod01-psm-n1
</font>
<font size='2'>
- Copy psm.qcow2 to a new image file on server 2 → ex: pod01-psm-n2
</font>
<font size='2'>
- Copy
</font> `psm.qcow2`<font size='2'>
-  to a new image file on server3 → ex: pod01-psm-n3
</font>
  
<font size='2'>

</font>

Since the CentOS server will be used by the user root, modify qemu.conf file so the user and group root are allowed.  Edit the file` /etc/libvirtd/qemu.conf`
 and uncomment the two entries `user = “root”`
 and `group = “root”`
, as below:  
<font size='2'>

</font>



```
# Some examples of valid values are:
#
#       user = "qemu"   # A user named "qemu"
#       user = "+0"     # Super user (uid=0)
#       user = "100"    # A user named "100" or a user with uid=100
#
user = "root"

# The group for QEMU processes run by the system instance. It can be
# specified in a similar way to user.
group = "root"

```
<font size='2'>

</font>

<font size='2'>
Once the file is saved, restart the
</font> 
`libvirtd`
<font size='2'>
 service:
</font>

<font size='2'>

</font>

<font size='2'>
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
</font>
`[root@server1 ~]# systemctl restart libvirtd`

<font size='2'>

</font>

Deploy the PSM nodes.  
<font size='2'>

</font>

<font size='2'>
Server1:
</font>



```
[root@server1 ~]# cd kvm/images/1.7.0-9/
[root@server1 1.7.0-9]# pwd
/root/kvm/images/1.7.0-9
[root@server1 1.7.0-9]# ls -al
total 2472704
drwxr-xr-x 2 root root         26 Apr  5 14:47 .
drwxr-xr-x 3 root root         21 Apr  5 13:14 ..
-rw-r--r-- 1 root root 2532048896 Apr  5 13:25 psm.qcow2
[root@server1 1.7.0-9]# cp psm.qcow2 pod01-psm-n1.qcow2
[root@server1 1.7.0-9]# ls -al
total 7418112
drwxr-xr-x 2 root root         78 Apr  5 14:43 .
drwxr-xr-x 3 root root         21 Apr  5 12:56 ..
-rw-r--r-- 1 root root 2532048896 Apr  5 14:41 pod01-psm-n1.qcow2
-rw-r--r-- 1 root root 2532048896 Apr  5 13:41 psm.qcow2


```
<font size='2'>
Server2:
</font>



```
[root@server2 ~]# cd kvm/images/1.7.0-9/
[root@server2 1.7.0-9]# pwd
/root/kvm/images/1.7.0-9
[root@server2 1.7.0-9]# ls -al
total 2472704
drwxr-xr-x 2 root root         26 Apr  5 14:47 .
drwxr-xr-x 3 root root         21 Apr  5 13:14 ..
-rw-r--r-- 1 root root 2532048896 Apr  5 13:25 psm.qcow2
[root@server2 1.7.0-9]# cp psm.qcow2 pod01-psm-n2.qcow2
[root@server2 1.7.0-9]# ls -al
total 7418112
drwxr-xr-x 2 root root         78 Apr  5 14:43 .
drwxr-xr-x 3 root root         21 Apr  5 12:56 ..
-rw-r--r-- 1 root root 2532048896 Apr  5 16:20 pod01-psm-n1.qcow2
-rw-r--r-- 1 root root 2532048896 Apr  5 14:53 psm.qcow2


```
<font size='2'>
Server3:
</font>



```
[root@server3 ~]# cd kvm/images/1.7.0-9/
[root@server3 1.7.0-9]# pwd
/root/kvm/images/1.7.0-9
[root@server3 1.7.0-9]# ls -al
total 2472704
drwxr-xr-x 2 root root         26 Apr  5 14:47 .
drwxr-xr-x 3 root root         21 Apr  5 13:14 ..
-rw-r--r-- 1 root root 2532048896 Apr  5 13:25 psm.qcow2
[root@server3 1.7.0-9]# cp psm.qcow2 pod01-psm-n3.qcow2
[root@server3 1.7.0-9]# ls -al
total 7418112
drwxr-xr-x 2 root root         78 Apr  5 18:15 .
drwxr-xr-x 3 root root         21 Apr  5 17:44 ..
-rw-r--r-- 1 root root 2532048896 Apr  5 21:41 pod01-psm-n3.qcow2
-rw-r--r-- 1 root root 2532048896 Apr  5 18:07 psm.qcow2

```
<font size='2'>

</font>

Run the following commands to deploy each node. PSM Node1 is used as an example below; run the same procedure on the remaining nodes as well.  
<font size='2'>

</font>



```
[root@server1 1.7.0-9]# virt-install --import --name pod01-psm-n1 --virt-type kvm --cpu host-passthrough --os-variant rhel7.6 --ram 16384 --vcpu 4 --network=bridge:br11,model=virtio --disk path=/root/kvm/images/1.7.0-9/pod01-psm-n1.qcow2,format=qcow2,bus=scsi --controller scsi,model=virtio-scsi --nographics --check path_in_use=on

Starting install...
Connected to domain pod01-psm-n1
Escape character is ^]
[    0.000000] Initializing cgroup subsys cpuset
[    0.000000] Initializing cgroup subsys cpu
[    0.000000] Initializing cgroup subsys cpuacct
[    0.000000] Linux version 3.10.0-1062.4.3.el7.x86_64 (mockbuild@kbuilder.bsys.centos.org) (gcc version 4.8.5 20150623 (Red Hat 4.8.5-39) (GCC) ) #1 SMP Wed Nov 13 23:58:53 UTC 2019
[    0.000000] Command line: BOOT_IMAGE=/OS-1.7.0-9/vmlinuz0 rw rd.fstab=0 root=live:UUID=e380bc9a-9f04-4d10-9ecc-6d23d32d2fdb rd.live.dir=/OS-1.7.0-9 rd.live.squashimg=squashfs.img console=ttyS0 console=tty0 rd.live.image rd.luks=0 rd.md=0 rd.dm=0 enforcing=0 LANG=en_US.utf8 rd.writable.fsimg=1 pen.venice=OS-1.7.0-9/venice.tgz pen.naples=OS-1.7.0-9/naples_fw.tar
[    0.000000] e820: BIOS-provided physical RAM map:
	.
	.
	.
[   63.099928] Bridge firewalling registered
[   63.122358] nf_conntrack version 0.5.0 (65536 buckets, 262144 max)
[   63.233383] Netfilter messages via NETLINK v0.30.
[   63.237292] ctnetlink v0.93: registering with nfnetlink.
[   63.282430] IPv6: ADDRCONF(NETDEV_UP): docker0: link is not ready

CentOS Linux 7 (Core)
Kernel 3.10.0-1062.4.3.el7.x86_64 on an x86_64

localhost login:

```
<font size='2'>

</font>

The default login userid and password are `root`
 and `centos`
.  
<font size='2'>

</font>

Next, use the `config_PSM_networking.py`
 utility to configure the network settings for each PSM node. (The command `config_PSM_networking.py -h`
 will show all its parameters.)  
<font size='2'>

</font>

`[root@localhost ~]# config_PSM_networking.py -hostname pod01-psm-n1 -password mypassword  -addrtype static -ipaddr 10.29.11.21 -netmask 255.255.255.0 -gateway 10.29.11.1 -dns 10.29.5.9,8.8.8.8`

<font size='1'>

</font>

Note: In the example above, replace `mypassword`
 with one conforming to the appropriate robustness and security guidelines for your site.  
  
Exit the console of the VM (typically by pressing `Ctrl+]`
 ).  Next, set the VM to autostart in case the CentOS server is rebooted.  
<font size='1'>

</font>

<font size='1'>
[root@server1 1.7.0-9]#
</font> 
<font size='1'>
**virsh autostart pod01-psm-n1**
</font>

<font size='1'>
Domain pod01-psm-n1 marked as autostarted
</font>

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;  
