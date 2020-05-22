---
title: PSM User Guide
description: PSM User Guide
weight: 1
draft: false
toc: true
---
<img src="/images/PSM/Pictures/1000020100000100000001009B15C8156A7B0FE8.png" style="width:3.6839in;height:1.6402in" />

<span id="anchor"></span>

<span id="anchor-1"></span>

<span id="anchor-2"></span>

<span id="anchor-3"></span>

<span id="anchor-4"></span>PSM Enterprise User Guide

<span id="anchor-5"></span>

<span id="anchor-6"></span>  
Date:*May 15*, 2020

Contents

<span id="anchor-7"></span>

<span id="anchor-8"></span>Introduction

This guide describes how to install and operate the Pensando Policy and
Service Manager (PSM) and deploy the Distributed Services Card (DSC).
Please refer to the *Pensando Distributed Services Card (DSC) User
Guide* for DSC installation and setup instructions.

A Distributed Services Card (DSC) is installed in a PCIe slot and
provides network and storage services to the host, allowing fully
programmable control of all services including security and visibility
features.

The Policy and Services Manager (PSM) allows for configuration and
delivery of network, security, and telemetry policies to Pensando DSCs
at scale.

The PSM is accessible through either a secure RESTful API or a
browser-based GUI, both described in this document. The full Pensando
API Reference Guide for PSM is available online as part of PSM at
[https://](https://ipaddr/docs)[*IPaddr*](https://ipaddr/docs)[/docs](https://ipaddr/docs),
where [*IPaddr*](https://ipaddr/docs) corresponds to the PSM cluster
address, and is also available in the release as PSM\_apidoc.pdf. The
API can be used by posting REST calls in JSON format to the same URI.
The GUI is a browser-based interface, accessible at the PSM cluster IP
through the URI https://*IPaddr*.

Parts of this document assume that readers have VMware ESXi or KVM
system administration experience.

Users of PSM and this guide are assumed to be familiar with REST APIs
and JSON-based payloads. The term “endpoint”, used in the context of
REST API calls and curl commands, refers to the URI with respect to the
PSM instance [https://](https://ipaddr)[*IPaddr*](https://ipaddr) .

Developers and operators are strongly recommended to use tools such as
Postman and swagger-generated client libraries for API-based development
whenever possible. The PSM distribution includes a working Postman
collection with sample calls and payloads for multiple common use cases.

This document corresponds to the PSM 1.X.Y release. Differences will
exist with respect to certain PSM managed objects in earlier PSM
releases. See the *Pensando Release Notes, Version 1.X.Y *document for
details and further information about supported third party switches,
cables, known issues, and fixed bugs.

<span id="anchor-9"></span>Glossary

<table>
<tbody>
<tr class="odd">
<td><strong>Name</strong></td>
<td><strong>Description</strong></td>
</tr>
<tr class="even">
<td>PSM</td>
<td>Pensando Policy and Services Manager</td>
</tr>
<tr class="odd">
<td>DSC</td>
<td>Pensando Distributed Services Card</td>
</tr>
<tr class="even">
<td>ionic_en</td>
<td>DSC Ethernet device driver</td>
</tr>
<tr class="odd">
<td><p>NetworkSecurity</p>
<p>Policy</p></td>
<td>PSM name for Network Security Policy object</td>
</tr>
<tr class="even">
<td>Vmware Installation Bundle (VIB)</td>
<td>vSphere Installation Bundle, VMware’s device driver package format</td>
</tr>
<tr class="odd">
<td>AAA</td>
<td>Authentication, Authorization, Accounting</td>
</tr>
<tr class="even">
<td>Host</td>
<td>A system that includes a managed DSC</td>
</tr>
</tbody>
</table>

<span id="anchor-10"></span>PSM Overview

The Pensando PSM platform is a policy and services manager based on a
programmable, secure, highly available, comprehensive single point for
managing infrastructure policy management and functions for:

-   Distributed firewall security
-   Telemetry and analytics
-   Troubleshooting
-   Distributed Service Card (DSC) lifecycle management
-   Operations and maintenance: events, alerts, technical support
-   Authentication, authorization, and accounting (AAA)

The PSM platform is designed to provide consistent policies for
thousands of DSCs (refer to *Pensando Release Notes *for current support
limits). The PSM platform operates as a 3-node quorum-based cluster
running on VMs hosted on multiple servers for fault tolerance. The PSM
can tolerate the loss of one controller node in the cluster and continue
to maintain full service. The PSM controller is not involved in datapath
operations; if it becomes unreachable, data traffic will continue
working seamlessly on disconnected DSC hosts. Figure 1 is a diagram of
the interconnection between the PSM and the DSCs it manages;
interactions take place through an IP network.

*Figure 1. PSM/DSC interconnection*

PSM employs an *intent-based* configuration management structure,
similar to Kubernetes. Any configuration changes are continuously
monitored within the PSM until it has been confirmed that the changes
have been propagated to DSCs.

Each DSC is configured with an IP address that is used for communication
with its associated PSM over any IP network. This is commonly referred
to as its *management address*.

Each DSC runs an agent which constantly watches for incoming
configuration changes upon which it must take action. This agent runs
within the DSC and is completely transparent to and independent of the
host and its operating system.

The PSM resends configuration requests until the desired state is
reported back from each DSC, as shown in Figure 2:

*Figure 2. Working principles of intent-based configuration*

Intent is expressed in terms of *policies*; the PSM uses an object model
to describe the various entities involved in the policies. Objects
include *Host Objects*, *Workload Objects*, and *App Objects*. More
information can be found in the [*PSM Object Model*](#_sym3ueouwi3b)
section.

Figure 3 is a sample topology of two ESXi hosts deploying DSCs
connecting to two Top-of-Rack switches.

Note:

-   Management traffic for both the ESXi host and the DSC is untagged
    and, as such, gets associated by the switch to the native VLAN; such
    traffic is not subject to policy evaluation. The PSM supports
    untagged workload uplink traffic. All workload traffic, even if
    untagged, will be subject to policy enforcement.
-   “microsegmentation VLANs” are used on a given ESXi host to enforce
    traffic isolation and are facilitated by ESXi port groups: each VM
    is associated to a port group (PG) with its own VLAN (e.g., 10,
    20, 30) in the figure below.
-   VMs on different hosts can communicate with each other if they share
    the same external VLAN (or Workload VLAN) that was specified and
    associated with the Workloads. For further details, please see the
    section [*First Time Workload Configuration*](#dqm65valsla3).

*Figure 3. ESXi host physical interconnection and virtual networking
configuration*

<span id="anchor-11"></span>Initial Deployment Workflow: High-Level
Overview

This is an outline of the steps necessary for initial deployment of a
PSM cluster and its associated DSC-equipped hosts. Detailed steps are
provided further below in this document; also refer to the *Enterprise
PSM Best Practices* document for further guidance on configuration.  

-   Installing the PSM

    -   Install the PSM as either an ESX-based or KVM-based 3-node
        > cluster.

    -   Configure the PSM using the bootstrap\_PSM.py utility.

    -   Save a copy of the DSC security token.

    -   Set the PSM user authentication policy, and create PSM users
        > with appropriate roles.

-   Network Switch Port Configuration

    -   Configure the top-of-rack switch ports connecting to DSC
        > uplinks.

-   Host Configuration

    -   Download and install DSC device drivers on each host.

    -   Associate each DSC to the PSM either from its host or via DHCP.

    -   Plan for one additional IP address allocated to each DSC as a
        > management interface, configured either from its host or via
        > DHCP.

    -   Admit the DSC into its PSM cluster. The PSM can be configured to
        > allow this to happen automatically.

    -   (optional) Create a “Host” object corresponding to the admitted
        > DSC.

-   Create and Manage Network Policies

    -   Create “Workload” objects corresponding to each VM instance.

    -   (optional) Create “App” objects, corresponding to network
        > services.

    -   Create and manage policies corresponding to various features
        > such as flow export and firewall rules and permissions between
        > Workloads and Apps.

Installation of the PSM cluster is a one-time activity; other procedures
may be performed during initial installation, but will also be part of
the standard operation of the PSM, performed for each addition of hosts,
users, and policies.

<span id="anchor-12"></span>PSM Object Model

The PSM implements an intent-based paradigm that relies on an object
model described in this section. Each object can be associated with one
or more labels that can be used to refer to a group of objects, which is
a very effective way to enable “administration at scale”.

NOTE: Labels that begin with "io.pensando." are reserved for system use,
and cannot be created or modified by the user. If the user includes such
a system label in an operation (e.g., association of labels to an
object, identification of objects by label), the label will be silently
removed from the operation.

<span id="anchor-13"></span>Host Objects

The primary compute objects are illustrated in Figure 4. A physical
server is represented by a *Host* object. A Host can have one or more
*DistributedServicesCard* objects, each representing a DSC card. Each VM
is represented by a *Workload* object.

*Figure 4. PSM primary compute objects*

  
Once a DSC card has been admitted into a PSM, it needs to be associated
with a Host object representing the host it is mounted on. In general,
Host objects cannot be changed or updated<sup>[1]</sup>.

<span id="anchor-14"></span>Firewall Objects

The primary firewall objects are illustrated in Figure 5. The *NSPRule*
(Network Security Policy Rule) specifies the firewall behavior, but is
not a managed object itself. Instead, the
*NetworkSecurityPolicy*<sup>*[2]*</sup> is the managed object that
contains an array of NSPRule specifications.

*Figure 5. PSM primary firewall objects: NetworkSecurityPolicy, NSPRule,
and App*

<span id="anchor-15"></span>Workloads, Apps, and Network Policy

In PSM terminology, a *Workload* corresponds to an OS-provisioned VM,
bare-metal server, or container. A Workload is defined by its
“host-name” and by one or more “interfaces” defined by:

-   mac-address
-   ip-addresses
-   micro-seg-vlan
-   external-vlan

When applied to an ESXi environment, the “micro-segment VLAN” of a
Workload corresponds to a “port-VLAN” within the DVS that is unique and
associated to the VM network interface.

In PSM terminology, an *App* is a service defined either by a “protocol,
port” pair, or by an application level gateway (i.e. “ALG”)

In PSM terminology, a *Network Security Policy* is a collection of
firewall rules, governing App connectivity between Workloads.

<span id="anchor-16"></span>Key PSM Objects

The following table contains sample key PSM objects. For a complete list
please refer to the REST API online help available through the PSM GUI.

<table>
<tbody>
<tr class="odd">
<td><strong>Object</strong></td>
<td><strong>Description</strong></td>
</tr>
<tr class="even">
<td><p>Distributed</p>
<p>ServiceCard</p></td>
<td><p>• DSC Object, one per DSC, identified by the hostname assigned by the penctl or esx-pencli CLI tool. If no name was assigned, the card’s MAC address is used.</p>
<p>• A DistributedServiceCard object is subsequently associated to a Host object</p></td>
</tr>
<tr class="odd">
<td>Host</td>
<td><p>• One Host object for every ESXi (or bare-metal) host</p>
<p>• Associated to one or more DistributedServiceCard objects based on their MAC addresses</p>
<p>• Allows the PSM to correlate one or more DSC cards to a Host</p>
<p>• A Host object is subsequently referred to by a Workload object</p></td>
</tr>
<tr class="even">
<td>Workload</td>
<td><p>• One Workload object for each VM, container or bare metal server</p>
<p>• Refers to a Host object</p>
<p>• Allows PSM to correlate a Workload with Host and DSC</p>
<p>• Workload object is subsequently referred to by a NetworkSecurityPolicy </p>
<p><em><strong>Note:</strong> A Workload object belongs to the “default” tenant unless specified. Please see the REST API guide A NetworkSecurityPolicy rule is typically deployed tenant-wide. ("attach-tenant": true in NetworkSecurityPolicy object)</em></p></td>
</tr>
<tr class="odd">
<td>Network</td>
<td><p>• A Network object represents a VLAN to which a workload is connected</p>
<p>•It is identified by a name</p>
<p>•It contains the VLAN number and the Orchestrator(s) in which such VLAN exists and is associated to Workloads </p></td>
</tr>
</tbody>
</table>

<span id="anchor-17"></span>

<table>
<tbody>
<tr class="odd">
<td><strong>Object</strong></td>
<td><strong>Description</strong></td>
</tr>
<tr class="even">
<td>App</td>
<td><p>• Describes the networking specification of an application, service or traffic</p>
<p>• An App object is subsequently referred to by a NetworkSecurityPolicy object</p>
<p><em><strong>Note: </strong>The App object belongs to the “default” tenant unless specified. Please see the REST API guide for a detailed description of the Tenant object. </em></p>
<p><em>A NetworkSecurityPolicy rule is typically deployed tenant-wide. ("attach-tenant": true in NetworkSecurityPolicy object)</em></p></td>
</tr>
<tr class="odd">
<td><p>Flow</p>
<p>Export</p></td>
<td><p>• One object is created for each flow export rule</p>
<p>• It contains the information necessary to identify flows whose information should be exported (i.e., a 5-tuple).</p>
<p>• It specifies the export format (IPFIX in this release)</p>
<p>• It identifies the collector(s) that should receive the traffic</p></td>
</tr>
<tr class="even">
<td><p>Mirror</p>
<p>Sessions</p></td>
<td><p>• One object is created for each bidirectional traffic mirroring rule</p>
<p>• It contains the information necessary to identify flows whose packets should be captured and exported (i.e., a 5-tuple).</p>
<p>• It defines a schedule for the mirroring to start</p>
<p>• It specifies a protocol (currently ERSPAN is supported) and an address for the collector</p>
<p>• It indicates the size to which packets should be truncated.</p></td>
</tr>
<tr class="odd">
<td><p>Network</p>
<p>Security</p>
<p>Policy</p></td>
<td><p>• Contains traffic rules (embedded objects) and/or references to App objects</p>
<p><em><strong>Note: </strong>The NetworkSecurityPolicy object belongs to the “default” tenant unless specified. Please see the REST API guide for detailed description on object ‘Tenant’. </em></p>
<p><em>NetworkSecurityPolicy defined rules are deployed tenant wide. ("attach-tenant": true in NetworkSecurityPolicy object)</em></p></td>
</tr>
</tbody>
</table>

<span id="anchor-18"></span>

<span id="anchor-19"></span>Installing the PSM

**NOTE**: Before installation, refer to the Release Notes for the
minimum resource requirements needed to operate the PSM.

<span id="anchor-20"></span>Install and Configure the PSM (ESXi Cluster)

The PSM installs as a virtual appliance (OVA format file), deployed
through VMware Virtual Center (vCenter). The PSM deployment depends on
vApp and requires vCenter for installation. *While it is recommended
that vCenter or OVFtool is used to deploy the PSM OVA, more savvy users
can use native ESXi tools.*

See the* PSM for Enterprise Solution Design Best Practices* document for
details on hardware and software requirements for PSM installation.
Please plan for 60 minutes as an upper-bound limit to install a 3-node
PSM cluster.

A PSM instance is deployed as a high-availability quorum-based cluster.
To ensure the highest availability, the PSM should be installed on 3
VMs<sup>[3]</sup>, each on separate host that are part of a VMware HA
cluster<sup>[4]</sup>.

-   Log in to vCenter. Locate the ESXi host you want to install a PSM
    node on and select “Deploy OVF Template” from the Action button.

-   Specify the URI or Local File name of the PSM OVA file psm.ova.

-   Specify the PSM VM name.

-   Under the storage section, select Thick Provision.

-   Specify the OVA properties: hostname, IP address, etc.

    -   If using DHCP, leave the IPaddress blank, and configure a static
        > MAC address-to-IP binding (reservation) for this host in the
        > DHCP server.

    -   Note that changing PSM cluster node IP addresses after
        > bootstrapping is not supported.

    -   It is strongly suggested that static IP is used.

    -   Under Password, specify the SSH/console password.

-   Review details. Click “Next” to accept the advanced configuration
    warning and lack of Publisher certificate<sup>[5]</sup>.

-   Start the VM in vCenter once the OVA deployment status shows
    “Completed”. The boot process will untar and install the PSM
    distribution from a read-only partition.

-   When the VM comes up, validate that the hostname has changed to what
    was specified in the OVA properties above and is not “localhost”. If
    “localhost” appears, then contact Pensando Support, as this
    indicates that the initialization did not complete successfully.

-   Login to the PSM as user root, with the password specified in the
    OVA properties above (if one was not defined in the OVA properties,
    the default password is centos). If a non-default root password is
    configured, it may take 1-2 mins for the password to take effect
    after the login prompt becomes available. If this is a concern, make
    sure network access to the VM is disabled until the password has
    been reset.

-   Initialize the cluster, as described in the section [*Bootstrap the
    PSM Cluster*](#_badmexb3oyp5).

NOTE: Deploying a 3-node cluster involves importing the psm.ova file
once for each VM instance. The number of imports can be reduced by
cloning the first VM as a template, and then deploying subsequent VMs
from the template. If taking this approach, follow these steps:

1.  Create the first VM from the psm.ova file

2.  In vCenter, choose “Clone as Template to Library” to save the VM as
    > a Template (.vmtx) file. Be sure to give the VM a unique name.

3.  Select the new VM in vCenter. Select the “Configure” Menu item.
    > Expand “Settings” and select “vApp Options”. Scroll down to
    > “Properties”. Click the radio button for “hostname” and the “Set
    > Value” action to change the hostname to a unique value (typically
    > corresponding to the VM unique name).

4.  If applicable, apply any network-specific settings that may have
    > been used in deploying the original VM from the psm.ova file.

5.  Start the new VM and verify that the VM name and network setting are
    > as intended before bootstrapping the cluster as described in the
    > below section [*Bootstrap The PSM Cluster*](#_badmexb3oyp5).

<span id="anchor-21"></span>Install and Configure the PSM (KVM Cluster)

The PSM is supported on KVM as well as ESXIi; this section provides a
short summary of the steps required to set up a KVM-based PSM appliance.
For a detailed guide, see [*Appendix M*](#_bvz3v9v0nixx).

-   Create three KVM hosts. Server requirements are specified in the
    document *Enterprise PSM Design Best Practices*. (Pensando
    recommends that the three PSM cluster nodes should be distributed
    across multiple servers).

-   Configure the needed network bridges for access to the CentOS server
    and for the PSM.

-   Make sure the VLAN module is loaded for each server.

-   Create a bridge interface named br0 that links interface eno5, which
    is an active interface on the server.

-   Restart the network and verify that the CentOS system server1 is
    accessible.

-   Verify the network interfaces.

-   Create the interfaces that will be used for the PSM.

-   Create the interface that is linked to the physical interface.

-   Restart the network service.

-   Repeat the above steps to deploy the second server (server2) in the
    environment (a third one you might have in your setup).

-   Install the PSM software:

    -   Deploy each PSM node using the psm.qcow2 image

    -   Set networking for the nodes

-   Bootstrap the cluster, as described in the next section.

<span id="anchor-22"></span>Bootstrap The PSM Cluster

Before the PSM cluster can be administered, it must be initialized via
the bootstrap\_PSM.py utility. Below are some usage examples. The
command bootstrap\_PSM.py -h will show all parameters that can be
specified.

  
Determine the IP address assigned to each PSM VM that has been deployed.
In ESXi deployments this can be obtained from vCenter, or from within a
CentOS VM with ip addr. This address is required when launching the
bootstrap\_PSM.py utility and is provided through the -v option.

NOTE: a PSM VM should have a single L3 interface that it uses to
communicate to other PSM VMs as well as its DSCs. The IP address of this
interface should be used in bootstrapping the cluster. The default IP
route should point to this interface.  

**Example:** If you have only one PSM VM (for testing only):  
  

<table>
<tbody>
<tr class="odd">
<td><p># <strong>bootstrap_PSM.py -v 192.168.68.49</strong></p>
<p>2019-09-26 11:48:05.405149: * start PSM bootstrapping process</p>
<p>2019-09-26 11:48:05.405195: * - list of PSM ips: ['192.168.68.49']</p>
<p>2019-09-26 11:48:05.405214: * - list of ntp servers: ['0.us.pool.ntp.org', '1.us.pool.ntp.org']</p>
<p>2019-09-26 11:48:05.405228: * - using domain name: pensando.io</p>
<p>2019-09-26 11:48:05.405240: * - auto-admit dsc: True</p>
<p>2019-09-26 11:48:05.405252: * checking for reachability</p>
<p>2019-09-26 11:48:09.415351: * connectivity check to 192.168.68.49 passed</p>
<p>2019-09-26 11:48:09.415436: * creating PSM cluster</p>
<p>2019-09-26 11:48:09.416110: * sending: POST http://localhost:9001/api/v1/cluster</p>
<p>2019-09-26 11:48:09.416144: {"api-version": "v1", "kind": "Cluster", "meta</p>
<p><em>(..snip..)</em></p></td>
</tr>
</tbody>
</table>

**Example: **To bootstrap a 3-node PSM cluster for production, specify
all three IP addresses. Before executing this command, make sure that
all three PSM VMs are already running. The PSM VMs can be deployed using
the same OVA, but must have unique IP addresses. The bootstrap script
only needs to be executed on one of the nodes.

\# **bootstrap\_PSM.py -v 192.168.68.49 192.168.68.50 192.168.68.51**

If everything completes successfully, the message below can be seen in
the log:

<table>
<tbody>
<tr class="odd">
<td><p><em>(..snip..)</em></p>
<p>2019-09-26 18:52:13.693626: * PSM cluster created successfully</p>
<p>2019-09-26 18:52:13.693656: * you may access PSM at https://192.168.68.49</p></td>
</tr>
</tbody>
</table>

The PSM browser GUI and REST API should now be available at any of the
PSM addresses. Note that there is no virtual IP address for the 3 node
cluster. A load balancer should be installed in front of the cluster to
enable such functionality.

If a password is not specified when bootstrapping the PSM cluster, the
default is Pensando0$.

The bootstrap\_PSM.py utility can be used to provide configuration
information to the PSM. The following example provides a cluster name, a
domain name, and the address of an NTP server, and activates automatic
DSC admission:

\# **bootstrap\_PSM.py -clustername Pod02 -domain training.local
-ntpservers 10.29.5.5 -autoadmit True 10.29.12.11 10.29.12.12
10.29.12.13**

To change the PSM cluster root password once the cluster is operational,
see [*Appendix H*](#_zg3pzv61fve6).

**Note**: Please make sure to save the DSC Security Token and store it
in a safe place. This may be needed for advanced troubleshooting through
the penctl tool, in situations where the PSM and a DSC cannot
communicate.

See: [*Appendix B - *](#_rxxgzoh3wyg)[*Save the
*](#_rxxgzoh3wyg)[*PSM*](#_rxxgzoh3wyg)[* Security
Token*](#_rxxgzoh3wyg).

<span id="anchor-23"></span>Network Switch Port Configuration

This section details the configuration required on Top-of-Rack (ToR)
switches to which DSCs are connected.

Since each DSC card can send and receive traffic over multiple VLANs,
DSCs *must* connect to switch ports configured as trunk ports under
certain conditions:

-   If the Workloads on a host are configured to use an IEEE 802.1q
    External VLAN, then the corresponding switch port ***must*** be
    configured as a trunk port.
-   If all the Workloads on a host are sending untagged traffic
    (External VLAN 0), then the switch port associated with DSC can be
    configured as an access port.

All management traffic (towards an ESXi host or DSC) is expected to be
untagged. Any management traffic must be configured with the native VLAN
of the network switch. Most network switches use "VLAN 1" as the native
VLAN on a trunk port, when not explicitly configured with a native VLAN.
If the management traffic is not using VLAN 1, then adjust the "trunk
native vlan" switch port configuration to match the VLAN ID used by
management traffic to ensure that it will be transmitted untagged on the
links to DSCs.

<span id="anchor-24"></span>PSM Graphical User Interface

The PSM Graphical User Interface (GUI) is accessible via a web browser
at https://*IPaddr*, where *IPaddr* corresponds to the IP address of any
of the PSM cluster nodes. Figure 6 shows a configurable dashboard that
offers an overview of the status of the Pensando Distributed Services
Platform, while the main menu on the left hand side provides access to
the configuration of all supported features.

<img src="/images/PSM/Pictures/1000020100000545000002A2275F58BAFB0F3CBD.png" style="width:6.5in;height:3.25in" />

*Figure 6. Pensando PSM dashboard*

<span id="anchor-25"></span>Online Help

Detailed and comprehensive online help is offered in a context-sensitive
manner for each page in the PSM GUI, accessible through the help icon in
the upper right-hand corner:

<img src="/images/PSM/Pictures/10000201000000460000005629D26F7911113DA9.png" style="width:0.598in;height:0.7339in" />

  
The help icon is context sensitive, showing information related to the
currently displayed GUI elements. For example, clicking the help icon
while in the Workload overview will display descriptive help and
examples on how to create a Workload object, as shown in Figure 7.
Similarly, clicking the help icon while in the Monitoring -&gt; Alerts
and Events view will show help on configuring Alert Policies.

<img src="/images/PSM/Pictures/10000000000009C40000048B1EA1F4B70D627AD6.png" style="width:6.5in;height:3.028in" />

*Figure 7. Example of PSM help *

Online Help windows can be easily undocked, redocked, resized, or
closed.

Online Help has its own presentation context, so it does not need to be
closed prior to subsequent operations; selecting different items from
the left-hand-side Navigation pane will automatically display the
corresponding Online Help information.

<span id="anchor-26"></span>Searching

The easy-to-use search facility is accessed from the search bar at the
top of the screen.

<img src="/images/PSM/Pictures/10000201000005EE000002105DEE46BC39B7EE4C.png" style="width:6.5in;height:2.2638in" />

*Figure 8. PSM search facility*

In the example in Figure 8 above, doing a free form text search for the
string “ae-s7”, shows a summary of the various objects where that string
appears, along with a count of the number of occurrences for each object
type.

*Figure 9. Accessing Advanced Search*

Clicking on the downward arrow on the right hand side of the text box
(shown in Figure 9 above) gives access to the Advanced Search capability
shown in Figure 10, where users can search based on object Category,
Kind or Tag (arbitrary labels associated to objects):

<span
id="anchor-27"></span><img src="/images/PSM/Pictures/10000201000004C800000256779BC6F47EAD6D6A.png" style="width:6.5in;height:3.1807in" />

*Figure 10. Advanced Search*

All the keywords used in Advanced Search can also be typed directly into
the search bar to avoid having to bring up the Advanced Search tab.

<span id="anchor-28"></span>Global Icons

The GUI makes use of common/global icons for many actions, regardless of
context, such as “Edit” or “Delete”, as shown in Figure 11 :

<img src="/images/PSM/Pictures/100002010000005E0000003EC9E4C10900BBDD05.png" style="width:0.9398in;height:0.6193in" />

<img src="/images/PSM/Pictures/10000201000007280000017074183721F959F4FC.png" style="width:6.5in;height:1.3055in" />

*Figure 11. Edit and Delete icons*

Many of the tables displayed in the GUI can be exported as CSV or JSON
text files, as shown in Figure 12:

<img src="/images/PSM/Pictures/10000201000001F4000001141DA6EC27BE777F16.png" style="width:1.8484in;height:1.0201in" />

<span
id="anchor-29"></span><img src="/images/PSM/Pictures/100002010000072C000001627C977C72268E3401.png" style="width:6.5in;height:1.25in" />

*Figure 12: Example of how a table can be exported in CSV or JSON
format*

<span id="anchor-30"></span>Server Certificate

By default, a self-signed certificate is created by the PSM during
installation, and is used to authenticate connections to the
browser-based GUI or REST clients. Users may instead provide a custom
key and certificate to the PSM to be used instead of the default
self-signed one. If the root Certification Authority (CA) of the signer
of such certificate is included in either the browser or the client
hosts’ trusted root CA certificate list, warning messages related to the
certificate validity will no longer be shown when accessing the PSM
cluster login page.

The two supported encoded key formats are RSA and ECDSA. To change the
PSM certificate, click "Admin" --&gt; "Server Certificate". On the top
right hand side, click "UPDATE". Enter the key and certificate in PEM
format and then click "Upload" to apply the change, as shown in Figure
13. **Note:** this action will not disrupt existing connections, even if
they were established with the previous certificate.

<img src="/images/PSM/Pictures/10000201000008B000000170F12852CA550A741B.png" style="width:6.5in;height:1.0693in" />*Figure
13. Changing the PSM server certificate*

<span id="anchor-31"></span>API Capture

The PSM GUI can display the REST API calls sent from the GUI to the PSM
as it implements the configurations created by the user. When the API
Capture menu item is selected, a view as shown in the figure below
appears. Use this screen to browse sample API calls (in the API Capture
tab) or a live capture of APIs generated while navigating the GUI (in
the Live API Capture tab). This can be a valuable tool to explore how
the PSM API can be used for external integrations. The live capture tool
is per GUI session; large responses are trimmed down to two records to
present the look and feel of the response, rather than the entire
response.

<img src="/images/PSM/Pictures/100002010000084E000003B6D77E88FEFDB54F36.png" style="width:6.5in;height:2.9028in" />

*Figure 14. Examples of captured REST API calls*

<span id="anchor-32"></span>Online Documentation

The PSM Reference guide is provided in online format, and included
within the PSM itself. The online documentation can be accessed at
https://*IPaddr*/docs , where *IPaddr* corresponds to the PSM cluster
address.

<span id="anchor-33"></span>Create PSM Authentication Policy and Users

Each PSM will have one or more users defined. Users are assigned roles
granting them privileges depending on the tasks they need to perform;
during the installation process, a default user, named admin with the
password Pensando0$ , is created with full administrator privileges. A
different name for the default user as well as its password can be
provided as parameters to the bootstrap\_PSM.py utility used to
initialize the cluster as described in the section “[*Bootstrap The PSM
Cluster*](#_badmexb3oyp5)”.

<span id="anchor-34"></span>Authentication Policy

The PSM supports Local (i.e., username and password), LDAP and RADIUS
Authenticators, as shown in Figure 15. Creation of authenticators should
be done early in the system setup process. Once two or more
authenticators are created, they can be re-ordered dynamically to
specify the priority with which they should be applied.  

<img src="/images/PSM/Pictures/1000020100000461000002EF4D973F0052FC6F3E.png" style="width:6.5in;height:4.361in" />

*Figure 15. Setting user authentication policy*

To create an LDAP Authenticator, click the “CREATE LDAP AUTHENTICATOR”
button. Active Directory (AD) and OpenLDAP providers are supported.

Configure *Credentials*, *Scope* (which controls user and group entry
search) and *Attribute* mapping (which contains the name of the
attributes that should be extracted from the LDAP entry of the user,
such as full name and email address) as appropriate, ensuring all
required (\*) fields are properly filled, as in Figure 16:

<img src="/images/PSM/Pictures/10000000000009C4000004C04744EFDA08BC5B9C.png" style="width:6.5in;height:3.1665in" />

*Figure 16. LDAP configuration*

Once saved, the values should be visible, as shown in Figure 17. The
order of the various authenticators can be changed (using the small
arrows on the right hand side).

<img src="/images/PSM/Pictures/10000201000004680000020C5496C2FDE0FADC01.png" style="width:6.5in;height:3.0138in" />

*Figure 17. Changing authentication order*

<span id="anchor-35"></span>Role Based Access Control (RBAC)

The User Management menu gives access to the RBAC Management screen,
shown in Figure 18, which allows management of either users or roles, or
the association of users to roles (“rolebinding”) based on the selection
made with the drop-down menu on the top right corner of the view. The
recommended User Management sequence consists of first creating one or
more Roles, followed by one or more Users, and then creating the
corresponding associations (rolebinding).

<img src="/images/PSM/Pictures/100002010000054400000332C8B4493BB52A583D.png" style="width:6.5in;height:3.9445in" />

*Figure 18. RBAC management*

<span id="anchor-36"></span>

<span id="anchor-37"></span>Roles

Roles are created to control access to classes of features by sets of
users. Roles can have scope over various objects, which are grouped by
the PSM in the categories:

[1]  If the mapping between a Host and a DSC needs to be changed within
a Host object, the following procedure must be used:

[2] * Please check the Release Notes for the number of
NetworkSecurityPolicy objects supported.*

[3]  The PSM can be installed as a single VM for test and evaluation
purposes.

[4]  A PSM controlling DSC cards running on ESXi servers that are
hosting the PSM itself is currently not a supported feature.

[5]  In this release, certificates are self-signed, triggering a
warning. This will be changed to authority-signed in a future release.
