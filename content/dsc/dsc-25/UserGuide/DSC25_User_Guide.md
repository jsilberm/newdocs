---
title: DSC-25 Card User Guide 
description: Pensando DSC-25 Distributed Services Card User Guide For Enterprise Solutions
menu:
    DSC-25:
       parent: dsc
weight: 1
draft: false
toc: true
---

Date:      May 15th, 2020

Revision History

| Version | Description | Date |
|---------|-------------|------|
| 1.0 | GA Release | May 2020 |


# About this Manual

This manual describes the Pensando Distributed Services Card (DSC), providing details on specifications, system requirements, and installation.

## DSC Card Product Portfolio and Ordering Information

| Pensando SKU | Part Number | Product |
|--------------|-------------|---------|
| DSC1-2S25-4H8P | 68-0005-xx yy | Pensando DSC-25  |
| DSC1-2S25-4H8P-H | P18669-001 | HPE SmartNIC 10/25Gb 2-port 691SFP28 Adapter |
| DSC1-2S25-4H8P-HS | P26968-001 | Pensando DSP DSC-25 10/25G 2p SFP28 Card |

_Table 1. Pensando DSC SKU with description_

The DSC comes in several models; this document describes the DSC-25.

DSC-25 meets the requirements for a x8 PCIe based half height, half length (Low Profile, LP) card supporting standard PCIe HHHL form factor.

![image alt text](/images/DSC/image_1.png)

_Figure 1. Pensando DSC-25 Dual-port 25Gb/s Ethernet Distributed Services Card_

__

![image alt text](/images/DSC/image_2.png)

_Figure 2. DSC-25 tail bracket and LEDs_

| LED Function | Status | Description |
|--------------|--------|-------------|
| SFP/Data Port 1 and 2 Link/Activity (bi-color) | Off | Link not established |
|  | Solid green | Valid Ethernet link |
|  | Blinking green | Passing traffic; blink frequency indicates traffic intensity |
|  | Solid amber | Link fault |
| Management Port Link | Off | Link not established  |
|  | Solid green | Valid Ethernet link |
| Management Port Activity | Off | No activity |
|  | Blinking | Passing traffic; blink frequency indicates traffic intensity  |
| Card Status | Off | System is not powered |
|  | Solid amber | Power is up, DSC software has not booted yet |
|  | Solid green | DSC is up and fully operational |
---------------------------------------------------------------------------------
_Table 2. LED operation_

## Referencing the MAC, Serial Number, and Part Number on the DSC-25

Each DSC-25 card has a unique part number, serial number and MAC address printed both on the package label and on the back of the card. Example card label is shown in Figure 3.

![image alt text](/images/DSC/image_3.png)

_Figure 3. Example Pensando DSC-25 label_
_on the card_

# Specifications: DSC-25

| Form factor and dimensions | Size | Half Height Half Length<br>2.54 in. x 6.79 in. (64.4 mm x 172.4 mm) |
|----------------------------|------|------------------------------------------------------------------|
|  | Primary Enet Connectors | Dual SFP28 |
|  | Mgmt Enet Connector | RJ45 |
| Cable support |  | DAC copper, or optical fiber |
| Protocol Support | Ethernet Standards | 25GBASE-CR/CR-S, 25GBASE-SR,  25G Ethernet Consortium,  10GBASE-CR, 10GBASE-SR, 10GBASE-ER |
|  | Data Rate (primary ports) | 10/25 Gb/s Ethernet |
|  | PCI Express | Gen 3, SERDES @ 8.0GT/s, 8 lanes; <br>Gen 2.0 and 1.1 compatible |
| Power and Environmental | Voltage | 12V, 3.3V via PCIe gold fingers |
|  | Typical Power | Passive DAC Cabling: 16W<br>Optical SFP Cables: 18.4W |
|  | Maximum Power | Passive DAC Interconnect: 19W |
|  |  | 1.5W Active Cables/Transceivers: 22W |
|  |  | 2.5W Active Cables/Transceivers: 24W |
|  | Maximum power available at each SFP28 port: 2.5W |  |
|  | Temperature | Operational: 0°C to 55°C |
|  |  | Non-operational: -40°C to 70°C |
|  | Humidity | 90% relative humidity |
| Regulatory | Safety | CSA NRTL / CB (in progress) |
|  | EMC | CE / FCC |
|  | ROHS | RoHS-R6 |
| Packaging | Weight | 0.71 lbs (including box) |

_Table 3. DSC-25 Specification_

# System Requirements

Please refer to the Release Notes for which servers, Top-of-Rack switches, operating systems, cables and transceivers are supported with the Pensando DSC-25.

# Installing the DSC

Follow standard safety procedures for working with components sensitive to static electricity discharge:

1. Remove any metallic objects from hands and wrists.   
2. Use only insulated tools as shown in the picture below.   
3. Verify that the system is powered off and unplugged.   
4. It is strongly recommended to use an ESD strap or other antistatic devices and follow standard practices of ESD installation.  


To Install the card:

1. Before installing the card, make sure that the system is off and the power cord is not connected to the server. Please follow proper electrical grounding procedures.   
2. Follow the server manufacturer instructions for inserting new cards into a server.  
3. Remove the card from its package. Please note that the card must be placed on an antistatic surface.   
4. Check the card for visible signs of damage. Do not attempt to install the card if damaged.   
5. Open the system case.   
6. Locate an available PCI Express slot for the adapter card. Do not force the bracket onto the adapter card, as this may damage the EMI fingers on the cages. A lesser width adapter can be seated into a greater width slot (x8 in a x16), but a greater width adapter cannot be seated into a lesser width slot (x16 in a x8). Align the adapter connector edge with the PCI Express connector slot.  
7. Applying even pressure at both corners of the card, insert the adapter card into the PCI Express slot until firmly seated.   
8. When the adapter is properly seated, the port connectors are aligned with the slot opening, and the adapter faceplate is visible against the system chassis.   
9. Secure the adapter with adapter clips or screws.   
10. Close the system case.  


## Removal Instructions

Follow the same precautions as above when removing the card.  The adapter is installed in a system that operates at high voltages.

1. Follow any server manufacturer instructions for removing cards from a server.  
2. Verify that the system is powered off and unplugged.   
3. Wait 30 seconds.   
4. Disengage the retention mechanisms on the bracket (clips or screws).   
5. Holding the adapter card from its center, gently pull the adapter card from the PCI Express slot.   
6. When the port connectors reach the top of the chassis window, gently pull the adapter card in parallel to the motherboard.  


# Connecting a DSC-25 to the Network

To obtain the list of supported active optical cables, including transceivers, and direct copper cables for the Pensando DSC-25, please refer to the 1.8.0-E Release Notes.

1. Cables can be inserted or removed with the unit powered on.  
2. Support the weight of the cable before connecting the cable to the adapter card. Do this by using a cable holder or tying the cable to the rack.   
3. Determine the correct orientation of the connector to the adapter card before inserting the connector. Do not attempt to insert the connector upside down. This may damage the adapter card.   
4. Insert the connector into the adapter card. Be careful to insert the connector straight into the cage. Do not apply any torque, up or down, to the connector cage in the adapter card.   
5. Press the connector into the port receptacle until the connector is firmly seated.  
6. Lock the connector using the latching mechanism particular to the cable vendor.   


The link LED indicator on the DSC-25 will turn green when a connection is established (that is, when the unit is powered on and a cable is plugged into the port with the other end of the connector plugged into a functioning port). When data is being transferred the green LED will blink at a rate indicating traffic intensity. Table 1 describes the LED operations. Please refer to the \_Pensando Enterprise Troubleshooting_
guide for more information on debugging link issues.

Care should be taken as not to impede the air exhaust flow through the ventilation holes. Use cable lengths which allow for routing horizontally around to the side of the chassis before bending upward or downward in the rack.



To remove a cable, disengage the locks and slowly pull the connector away from the port receptacle.

# Penctl CLI utility

The penctl utility is available for Linux and Windows and allows a server admin to manage most aspects of the DSC, including:

* Upgrading firmware (as described in previous sections)  
* Health monitoring  
* Viewing statistics  


penctl runs on the host operating system the card is installed in (Windows, Linux), and uses REST calls over the management link to the card. The command requires administrator or root privileges to execute.

### See all available penctl Commands



```
# penctl --help
--------------------------
 Pensando Management CLIs
--------------------------
Usage:
  penctl [flags]
  penctl [command]
Available Commands:
  create      Create Object
  delete      Delete Object
  help        Help about any command
  list        List Objects
  show        Show Object and Information
  system      System Operations
  update      Update Object
  version     Show version of penctl
Flags:
  -a, --authtoken string   path to file containing authorization token
      --compat-1.1         run in 1.1 firmware compatibility mode
      --dsc-url string     set url for Distributed Service Card
  -h, --help               help for penctl
  -j, --json               display in json format (default true)
      --verbose            display penctl debug log
  -v, --version            display version of penctl
  -y, --yaml               display in yaml format
Use "penctl [command] --help" for more information about a command.
# penctl show --help
-----------------------------
 Show Object and Information
-----------------------------
Usage:
  penctl show [command]
Available Commands:
  dsc                 Show Distributed Service Card Modes and Profiles
  dsc-config          Show Distributed Service Card Configuration
  dsc-profiles        Show Available Distributed Service Card Profiles
  events              Show events from Distributed Service Card
  firmware-version    Get firmware version on Distributed Service Card
  interface           Show interface
  logs                Show logs from Distributed Service Card
  metrics             Show metrics from Distributed Service Card
  port                show port object
  proc-meminfo        Check /proc/meminfo file on Distributed Service Card
  qos-class           show qos-class object
  running-firmware    Show running firmware from Distributed Service Card (To be deprecated. Please use: penctl show firmware-version)
  startup-firmware    Show startup firmware from Distributed Service Card
  system              show system information
  system-memory-usage Show free/used memory on Distributed Service Card (in MB)
```

time                Show system clock time from Distributed Service Card

## Examples

### Firmware Management

Checking current version:



```
# penctl show firmware-version
```

Installing new firmware:



```
# penctl system firmware-install -f local-firmware-filename
```

### Access DSC When Under PSM Control

Obtain session cookie

| ➜  ~ curl -k -d '{"username":"admin", "password":"<current password>", "tenant":"default"}' -c cookie -H "Content-Type: application/json" -X POST "https://192.168.70.102/v1/login" |
|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|


Obtain PSM certificate

| ➜  ~ curl -b cookie -s -k "https://192.168.70.102/tokenauth/v1/node?Audience=\*" \| cut -d "\"" -f 4 \| awk '{gsub(/\\n/,"\n")}1' > psmcert    |
|----------------------------------------------------------------------------------------------------------------------------------------------|

Use PSM certificate to request DSC tech support file

| ➜  ~ penctl -a psmcrt system tech-support Downloaded tech-support file: ./naples-tech-support.tar.gz |
|------------------------------------------------------------------------------------------------------|

### Health Monitoring

Overall/top-level health (normal status check):

```
# penctl show metrics { pcie | system }
```

PCIe metrics (troubleshooting):
```
# penctl show metrics pcie { pciemgr | port }
```
System metrics (monitoring temperature, power, etc.):

```
# penctl show metrics system { frequency | memory | power | temp }
```

Units used:

Frequency of the system in MHz

Memory is KB

Power is milli Watt

Temperature is degree Celsius

Kernel memory details:

```
# penctl show proc-meminfo
```

Interface configuration and status (equivalent to ip a ):

```
# penctl show interface {management }
```

Card FRU information:

```
# penctl show dsc
```

### Tech Support and Logs

Generating support logs: use these commands to find core files after unexplained reboots, when opening support cases, and for debugging purposes:



```
# penctl list core-dumps
```

Show core dumps from DSC



```
# penctl system tech-support -b file-name
```

-b - specify tarball file name without the tar.gz extension

If the -b option is not specified a default tarball - ./naples-tech-support.tar.gz - will be created.



Show Module Logs from DSC
```
# penctl show logs -m { nmd | netagent | tmagent | pcimgrd }
```

### Checking Driver Version



```
# ethtool -i enp22s0
Driver: ionic
Version: 1.8.0-E-24
```

Read the EEPROM of an SFP28 cable attached to a given interface:



```
# ethtool -m enp20s0
	   Identifier          : 0x03 (SFP)
        Extended identifier  : 0x04 (GBIC/SFP defined by 2-wire interface ID)
        Connector : 0x23 (No separable connector)
        Transceiver codes : 0x00 0x00 0x00 0x00 0x00 0x08 0x00 0x00
        Transceiver type  : Active Cable
        Encoding  : 0x06 (64B/66B)
        BR, Nominal   : 25500MBd
        Rate identifier   : 0x00 (unspecified)
        Length (SMF,km)   : 0km
        Length (SMF)  : 0m
        Length (50um) : 0m
        Length (62.5um)   : 0m
        Length (Copper)   : 3m
        Length (OM3)  : 0m
        Active Cu cmplnce.: 0x04 (SFF-8431 limiting) [SFF-8472 rev10.4 only]
        Vendor name   : AOI
        Vendor OUI: 00:29:26
        Vendor PN : AHJA9N03BDMN0848
        Vendor rev: B 40
        Option values : 0x18 0x1a
        Option: RX_LOS implemented
        Option: TX_FAULT implemented
        Option: TX_DISABLE implemented
        Option: Retimer or CDR implemented
        Option: Paging implemented
        BR margin, max: 103%
        BR margin, min: 0%
        Vendor SN : 22918H20010
        Date code : 180828
```

# Appendix A: Deployment Scenarios

## High Availability and NIC Teaming

Highly available designs with connectivity to redundant leaf switches are supported, through operating system adapter teaming. The teaming configuration in the operating system will dictate how/if network traffic will be load-balanced across the available DSC uplinks.

Operating systems vary in terms of what they support for active/backup and active/active teaming configurations, but the overall goal is that the NIC interface for workloads should remain available, if uplinks in a bonded pair become disconnected/unavailable.

For example, VMware ESXi typically supports the following load-balancing policies:

* Route based on originating port ID (default)  
* Route based on source MAC hash  
* Route based on IP hash  
* Use explicit failover order  


Linux releases typically support the following load-balancing policies:

* Round Robin  
* Active Backup  
* XOR [exclusive OR]  
* Broadcast	  
* Dynamic Link Aggregation [Switch must support 802.3ad]  
* Transmit Load Balancing (TLB)  
* Adaptive Load Balancing (ALB)  


The above operating system level NIC teaming load-balancing configurations, are supported with our product, in either single or dual DSC configurations.

For active/active fully non-blocking configurations, this is often combined with networking solutions like Cisco Virtual Port Channel (VPC) or Arista MLAG (Multi-Chassis Link Aggregation), which are types of Multi-Chassis EtherChannel (MEC). In essence, they ensure that the downstream server NICs, see the upstream switches (the MLAG/vPC Peers) as a single switch, thus eliminating STP blocked ports and allowing forwarding on all ports.

 **Note:** Please refer to the relevant documentation for your operating system for further specifics on server-side bonding configurations, and see Cisco/Arista switching guides for specifics on supported configurations with Cisco VPC or Arista MLAG.

# DSC-25 Deployment Scenario

Pensando DSC-25 presents dual 10G or 25G ethernet ports that can be connected to external top of rack (ToR) switches. A typical configuration with dual ToR in a virtualized environment and a bare metal environment is shown below.

![image alt text](/images/DSC/image_4.png)

_Figure 4. Single DSC-25 deployment in virtualized and bare-metal environments_

# Dual DSC-25 Deployment Scenarios

Often for traffic isolation or hardware redundancy, customers choose to deploy redundant adapters in servers. While the DSC-25 has two uplink ports to provide server connectivity protection against switch port downtime events, it doesn’t help to address the need for protection against adapter failures within the compute node, or enable traffic isolation use-cases (See Figure 5 & Figure 7 below for example configurations).

Refer to _Release Notes, Version 1.8.0-E_
for a list of servers and operating systems supporting dual DSCs.

 **_Note:_**
_Enabling NIC Teaming across different DSCs with services enabled is not supported._

## Example Dual DSC Configurations

### Dual DSC Deployment with VMware ESXi

![image alt text](/images/DSC/image_5.png)

\_Figure 5. Pensando dual DSC-25 and VMware vSphere configuration with two vDS/vSS_

Switch Configuration:

* MLAG or vPC enabled between the ToR switch pairs in Active/Active mode  


Hypervisor Networking Configuration:

* Dual vSphere Standard Switch (vDS/vSS)  
* Two port groups (PGs) (e.g: "PG Storage", and “PG Host”)  
* Two VNICs per VM:  


    * vnic1 connected to PG Storage

    * vnic2 connected to PG Host

ESXi Port Group & vSwitch Configuration:

* PG Storage - VLAN Storage trunked on uplinks from DSC-1 (vmnic0, vmnic1 bonded) on vSwitch0, and ToR ports  
* PG Host - VLAN Host trunked on uplinks from DSC-2 (vmnic2, vmnic3 bonded) on vSwitch1, and ToR ports  




Hypervisor NIC Teaming Policy (see Figure 6 below) :

* Teaming Policy: Route based on originating virtual port  
* Network failure detection: Link Status only  
* Notify switches – Yes  
* Failback – Yes  


![image alt text](/images/DSC/image_6.png)

_Figure 6. vSwitch NIC teaming and failover policy_

### Dual DSC Deployment with Linux

![image alt text](/images/DSC/image_7.png)

_Figure 7. Pensando Dual DSC-25 and bare-metal configuration with host LAG_

Switch Configuration:

* MLAG or vPC enabled between the ToR switch pairs in Active/Active mode  


Server Networking Configuration:

* NIC bonding enabled in the OS, mode 0 round-robin (default)  
