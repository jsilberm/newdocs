---
title: Netapp Katana Pensando User Guide Version 0.2.0
description: Netapp Katana Pensando User Guide Version 0.2.0
menu:
  docs:
    parent: "management"
    weight: 2
quicklinks:
weight: 1
draft: false
toc: true
---
# NetApp Katana Pensando User Guide

Version:  0.2.0

Date:      Jan 2, 2019

![image alt text](/images/management/netapp_userguide/image_0.png)

![image alt text](/images/management/netapp_userguide/image_1.png)

[[TOC]]

# 1 Pensando Legal Note

All information in this document is provided on a non-disclosure basis.   Anyone reading this document implicitly agrees to be bound by Pensando Systems’ non-disclosure terms.

# Document  Glossary

The following table describes the product "code names" used in this document and release.  Final product names are TBD.

| Name | Reference |
|------|-----------|
| NAPLES | Pensando Systems Adapter Card.  "“Network Adapter with Programmable Logic and Enhanced Security/Storage/Services" |
| Capri | Pensando System custom ASIC on the NAPLES Card |
| SONIC | Pensando Kernel driver that supports compress/decompression services in hardware  |
| IONIC | Pensando Kernel driver for NAPLES network adapter |
| penctl | CLI utility for managing NAPLES from the local host |

# 2 NAPLES Product Overview

The NAPLES Product is designed to connect rapidly evolving compute and storage servers to a new generation of scalable, programmable data center networks.  The NAPLES product includes a highly configurable network pipeline, a customizable host interface, and flexible hardware offload engines for storage, security, and network functions that can be processed in a pipelined manner at line rate.

The name "NAPLES" stands for “Network Adapter with Programmable Logic and Enhanced Security/Storage/Services”

The NAPLES product is based on a customized ASIC ("Capri") that implements a full match + action pipeline. All traffic is fully programmable through [P4](https://p4.org/) network programming specification.

The Capri ASIC implements a match + action pipeline using parsers, deparsers, table engines and match processing units (MPU). The forwarding logic is expressed in P4 language as a P4 program.

The NAPLES software subsystem runs on the ARM cores present in the Capri ASIC and includes Compression/Decompression offload as provided through the SONIC driver.

This document describes the NAPLES product.  Tasks for managing the control and data plane of Naples will be explained in this document. Internals of Naples card and offload architecture will be shown. Administrators should use this guide to understand how to use and manage Naples.

# 3 Naples Components

Naples is a PCIe card providing for offload of network, storage, and security services. Naples is a full-height half-width PCIe card containing a processor (Capri), network ports, management port and flash memory.

## 3.1 Naples Hardware Diagram

![image alt text](/images/management/netapp_userguide/image_2.png)

![image alt text](/images/management/netapp_userguide/image_3.png)

The "2x100G / 8x25G" uplinks label refers to the various link speeds that are supported, including:

* 2x 100G  
* 4x   50G  
* 4x   40G  
* 8x   25G  


## 3.2 Naples / Capri Overview

![image alt text](/images/management/netapp_userguide/image_4.png)

![image alt text](/images/management/netapp_userguide/image_5.png)

## 3.3 NAPLES Software and Services

NAPLES achieves service offload by implementing full network stack on its custom ASIC chip Capri. As presented in the above diagram, the platform contains memory to support data path operations, ARM CPUs to support the control path, and interfaces towards network and PCIe. To process packets according to programmed network policy, match processing units (MPUs) are used. Service acceleration is used to accelerate encryption, compression, hashing and storage functions.  This highly programmable data path, with full network stack on the NAPLES product provides for hardware accelerated, pipelined services offload at wire speed.

# 4 Installing Naples into the Server

## 4.1 Adapter Card Installation Instructions

Installation of the Naples adapter card requires following standard safety procedures for working with systems sensitive to static electricity discharge. The following safety procedures involve:

1. Removing any metallic objects from hands and wrists.   
2. Making sure to use only insulated tools as shown on the picture below.   
3. Verifying that the system is powered off and is unplugged.   
4. It is strongly recommended to use an ESD strap shown on a picture below or other antistatic devices.   


![image alt text](/images/management/netapp_userguide/image_6.png)![image alt text](/images/management/netapp_userguide/image_7.png)

To successfully install the card,  double check the following:

1. Verify that the system meets the hardware and software requirements   
2. After shutting down the system, turn off power and unplug the cord.   
3. Remove the card from its package. Please note that the card must be placed on an antistatic surface.   
4. Check the card for visible signs of damage. Do not attempt to install the card if damaged.   


To Install the card, follow the instructions below:

1. Before installing the card, make sure that the system is off and the power cord is not connected to the server. Please follow proper electrical grounding procedures.   
2. Open the system case.   
3. Locate an available PCI Express slot for the adapter card. Please avoid damaging the LEDs with a screwdriver.  Do not force the bracket onto the adapter card as to not damage the EMI fingers on the cages.  Please note that the following figures are for illustration purposes only.  A lesser width adapter can be seated into a greater width slot (x8 in a x16), but a greater width adapter cannot be seated into a lesser width slot (x16 in a x8).  Align the adapter connector edge with the PCI Express connector slot.  
4. Applying even pressure at both corners of the card, insert the adapter card into the PCI Express slot until firmly seated.   
5. When the adapter is properly seated, the port connectors are aligned with the slot opening, and the adapter faceplate is visible against the system chassis.   


![image alt text](/images/management/netapp_userguide/image_8.png)

6. Secure the adapter with the adapter clips or screws.   
7. Close the system case.   


## 4.2 Adapter Card Un-installation Instructions

Use Safety Precautions when working on removing the network card.  Follow the safety instructions described above for installing the network card.   The adapter is installed in a system that operates at high voltages.

1. Verify that the system is powered off and unplugged.   
2. Wait 30 seconds.   
3. To remove the card, disengage the retention mechanisms on the bracket (clips or screws).   
4. Holding the adapter card from its center, gently pull the adapter card from the PCI Express slot.   
5. When the port connectors reach the top of the chassis window, gently pull the adapter card in parallel to the motherboard like shown on Figure 1.  


.![image alt text](/images/management/netapp_userguide/image_9.png)

## 4.3 PCIe Supported

The Naples Smart I/O subsystem requires hardware systems that support PCI Express Gen 3 (1.0 and 2.0 compatible)  x16 slots. The device can be either an initiator/master, initiating the PCI Express bus operations, or a target/slave, responding to PCI bus operations.

The following lists PCIe interface features:

* PCIe Gen 3.0 compliant, 1.1 and 2.0 compatible   
* 2.5, 5.0, or 8.0 GT/s link rate x8 and x16   
* Auto-negotiates to x16, x8, x4, x2, or x1   
* Support for MSI/MSI-X mechanisms  
* Advanced Error Reporting (AER) capability  
* PCIe Atomic operations  
* SRIOV up to 1000 virtual functions  


## 4.4 Number of Naples Supported

The number of Naples Smart I/O subsystems depend on the number of PCIe slots on the motherboard and the server’s available power budget.

## 4.5 Power and Cooling Requirements

Naples Smart I/O subsystem requires that the server’s cooling system support cooling of a maximum of 50W during regular operations.  Specifications can be found in Section 7 of this document.

# 5 Penctl Utility

 **penctl** is the management utility that provides a CLI interface to manage NAPLES from the local host.   **penctl** runs on the local host operating system as a userspace utility. **penctl** is currently available for Linux and  FreeBSD.

### penctl Overview

The overall design is described in the following diagram, which allows the host to manage Naples through internal IP connectivity.

![image alt text](/images/management/netapp_userguide/image_10.png)

In the above diagram, IP1 = 169.254.0.1 and IP2 = 169.254.0.2

As seen above, **penctl** communicates with the Agent on Naples side using REST calls over IP connectivity. The IP address configuration on the Naples side is pre-defined, whereas the netdev’s interface IP is configured by using the commands specific to the host OS. In order to allow for IPs to not be colliding with some other IP used on the host-side, **penctl** establishes a separate network namespace on the host side.

## 5.1 penctl main features

*  **Naples Configuration:** provide ability to call Agent REST APIs  
*  **Firmware Management:** Install firmware versions, show running firmware versions, set firmware version for next reboot.  
*  **Provide Events and System Information of Naples:** allows examining the following on NAPLES:  


    * System logs (e.g. coming from Naples)

    * Process logs (e.g. debug output from various processes that may be running in Naples)

    * Alerts, warnings produced by the system

    * System information: memory usage

*  **Examine Metrics on Naples Subsystem:** allows examining the following stats  


    * Interface Statistics 

    * System metrics: ASIC error stats, cache stats, process stats, cpu stats, memory stats, rpc stats

*  **Penctl Versioning:** **penctl** is bundled and versioned independently  


## 5.2 penctl Installation and Setup on FreeBSD

The **penctl** version structure is major.minor.patch, designated as "0.2.0" for this release.

 **Pre-requisites** :

*  **_penctl_**
requires that the Naples IONIC Network driver has been built and loaded into the FreeBSD kernel.  
*  **_penctl_**
requires that the Naples management interface has been configured with an unused address on the 169.254.0.0/24 subnet.  


Please review the README.txt Release Notes for instructions on how to build the IONIC driver and configure the management interface.

 **Please note:** 

_In the previous version 0.1.0,_
**_penctl_**
_used a tunnel interface to communicate with the NAPLES Agent (Running in the NAPLES Card), relying on a pensando tool called_
**_‘memtun’_**
_which created a tunnel interface call ‘tun0’.    Version 0.2.0 and above of_
**_penctl_**
_do_
**_NOT_**
_require this tunnel interface and instead use the NAPLES card management interface.  Please remove any instances of the_
**_‘memtun’_**
_binary and any related startup scripts that may have been installed in /etc/rc.d._

* Download **penctl** (as obtained from Pensando), and install in an appropriate directory (i.e. /usr/local/bin)  
* Ensure the management interface **ionic2** is up and has been configured with an unused address on the 169.254.0.0/24 subnet.  Ex:  

```
ifconfig ionic2 169.254.0.2/24
```


## 5.3 Using the penctl Command in FreeBSD

### 5.3.1  Referencing the Management Interface

 **penctl** requires a reference to the management interface of a corresponding Naples card.

The management interface reference can be conveyed by one of two methods:

*  **penctl** can use the ‘ **PENETHDEV** ’ environment variable to reference the NAPLES management interface.  Ex:  "setenv PENETHDEV ionic2"  
*  **penctl** can take a ‘-i’ option to specify for any command command.  


Ex:  "penctl show running-firmware -i ionic2"

### 5.3.2 penctl command usage

The following section describes the **penctl** commands and flags available. With examples for the major commands.

### Help

To get help use the -h or --help:

# penctl -h

You should see something similar:



```
--------------------------
 Pensando Management CLIs
--------------------------
Usage:
  penctl [command]
Available Commands:
  delete      Delete Object
  help        Help about any command
  list        List Objects
  show        Show Object and Information
  system      System Operations
  update      Update Object
  version     Show version information
Flags:
  -h, --help               help for penctl
  -i, --interface string   ethernet device of naples
  -j, --json               display in json format
  -t, --tabular            display in tabular format (default true)
  -y, --yaml               display in yaml format
Use "penctl [command] --help" for more information about a command.
```

### High Level Command Summary

| Command | Description |
|---------|-------------|
| penctl show [ events | logs | metrics | mode |    <br>firmware | running-firmware | core <br>proc-meminfo | system-memory-usage  ] | Show object and information |
| penctl help  | Help about any command |
| penctl system [ firmware-install | tech-support ] | System operations |
| penctl update [ startup-firmware ] | Update object |
| penctl list  [ core-dumps ] |  List objects |
| penctl delete [ core-dump ] |  Delete object |


### Command Details

| Command | Flags | Description/ Command Flags |
|---------|-------|----------------------------|
| penctl version |  | Shows the version of Penctl utility |
| penctl delete core-dump |  | Delete a core dump files from Naples |
| penctl list core-dumps |  | Show core dump files on Naples |
| penctl show events |  | Show events from Naples |
| penctl show logs |  | Show logs from Naples |
|  | -m, --module string | Module to show logs for, valid modules are:<br>nmd  :  general system<br>netagent :  hardware abstraction layer (hal) <br>tmagent :   metrics agent<br>(Required) |
| penctl show metrics |  | Show metrics from Naples |
|  | -k, --kind string | Kind of metrics object :  [ upgrademetrics, … ? ]<br>(Required) |
|  | -n, --name string | Specific Name/Key for metrics object |
| penctl show firmware |  | Show firmware details on Naples |
| penctl show running-firmware |  | Show running firmware image name from Naples |
| penctl show startup-firmware |  | Show name of startup firmware image |
| penctl help |  | Help about any command |
| penctl system firmware-install |  | Copy and install firmware image to Naples |
|  | -f, --file string | Firmware file location/name<br>(Required)  |
| penctl update startup-firmware |  | Set Startup Image to Other (Non-Running) Image on Naples |
| penctl show proc-meminfo |  |  |
| penctl show system-memory-usage |  |  |

### penctl Global Flags

These flags apply globally to all commands

| Flag | Description |
|------|-------------|
| -i, --interface string | Ethernet device of naples; Note that this value can be set in PENETHDEV environment variable as well to avoid having to specify for each command invocation |
| -j, --json | Display in JSON format |
| -t, --tabular | Display in tabular format (Default) |
| -y, --yaml | Display in YAML format |
| -v, --version | Display ‘penctl’ version |

## 5.4 Logs

NAPLES Logs can be received through the ‘ **penctl show logs** ’ command.

### Log Severity Levels

The logs contains severity levels, the severity has three different levels as follow:

| Severity Levels | Description |
|-----------------|-------------|
| Info | Informational message |
| Warning | Warning, need attention |
| Error | Error, need immediate attention |

## 5.5 penctl Command

### 5.5.1 Caveats

Some aspects of the **‘penctl’** command are undergoing active development.  As a result, the actual output may not exactly match the expected output in the examples below.

### 5.5.2  Tabular, JSON and Yaml output

There are three options for retrieving the output from pentctl:  Tabular (Default), JSON and YAML.

The output format is selected by the flags ‘ **-t** ’, ‘ **-j** ’ and ‘ **-y** ’, please see below for examples

### Tabular Formatted (-t)

 **To retrieve the response in Tabular format tmagent log from Naples:** 

_Please note that the ‘-t’ is the default and can be omitted._



```
# penctl show logs -m tmagent -t -i ionic2
```

Level	Ts				Module		Caller	PID	MSG

------------- ----------------------------------------------------- -------------------------- ------------- ------------- --------------------------------------------------

Info	1970-01-01T00:00:02.911603803Z	pen-tmagent	ipc.go:70	701	size of ma: 196608, specified: 196608

### JSON Formatted (-j)

 **To retrieve the response in Tabular format tmagent log from Naples:** 



```
# penctl show logs -m tmagent -j -i ionic2
[{
	"level": "info",
	"ts": "1970-01-01T00:00:02.911603803Z",
	"module": "pen-tmagent",
	"caller": "ipc.go:70",
	"pid": "701",
	"msg": "size of ma: 196608, specified: 196608"
}, {
...
}]
```

### YAML Formatted (-y)

 **To retrieve the response in Tabular format tmagent log from Naples:** 



```
# penctl show logs -m tmagent -y -i ionic2
- level: info
  ts: '1970-01-01T00:00:02.911603803Z'
  module: pen-tmagent
  caller: ipc.go:70
  pid: '701'
  msg: 'size of ma: 196608, specified: 196608'
```

## 5.6 penctl Examples

Below are examples of common **penctl** commands.

 **To display current version information:** 



```
# penctl version

Sha:       c3919af
Version:   0.2.0 
BuiltTime: 2018.12.27-08:25:09

```
### 5.6.1 Firmware Install Process

Naples card uses two locations to store firmware images: " **mainfwa** " and “ **mainfwb** ”.  When Naples starts up, it will boot from one to the two firmware locations based on the “startup-firmware” setting.

 **_Please note:_**
_The example below shows the running firmware to be \*_
*_‘mainfwa’_**
_.   If your Naples card is using_
**_‘mainfwb’_**
_, then please change your command sequence accordingly._

The upgrade is done through 4 steps:

* Verify the current firmware information (Optional, but recommended)  
* Install Firmware   
* Set startup firmware pointer  
* Reboot server  


### 5.6.2 Verify the current firmware information

Before upgrading the firmware, verify the current firmware information.

 **To display current firmware information on Naples:** 
 
``` 
# penctl show firmware -j -i ionic2
```


Output should be similar to:



```
{
  "uboot": {
    "image": {
      "build_date": "Tue Nov 20 22:23:28 UTC 2018",
      "build_user": "",
      "base_version": "2018.08-git-gb28f69045e-dirty",
      "software_version": "v0.2-1559-gd08a1d9"
    }
  },
  "mainfwa": {
    "system_image": {
      "build_date": "Tue Nov 20 22:23:28 UTC 2018",
      "build_user": "",
      "base_version": "2018.08-git-gb28f69045e-dirty",
      "software_version": "v0.2-1559-gd08a1d9"
    },
    "kernel_fit": {
      "build_date": "Tue Nov 20 22:23:28 UTC 2018",
      "build_user": "",
      "base_version": "2018.08-git-gb28f69045e-dirty",
      "software_version": "v0.2-1559-gd08a1d9"
    }
  },
"mainfwb": {
	"system_image": {
	"build_date": "Fri Nov 16 20:54:02 UTC 2018",
	"build_user": "",
	"base_version": "2018.08-git-g58ecbed36e-dirty",
	"software_version": "v0.2-1482-gf8b43d0"
    },
    "kernel_fit": {
    "build_date": "Fri Nov 16 20:54:02 UTC 2018",
    "build_user": "",
    "base_version": "2018.08-git-g58ecbed36e-dirty",
    "software_version": "v0.2-1482-gf8b43d0"
    }
  },
  "goldfw": {
    "kernel_fit": {
      "version": "br:2018.08-git-g9a91db08e9-dirty fs:v0.2-1182-g35b05e8-dirty"
    }
  },
  "diagfw": {}
}
```

The above shows the two firmware images present are:

 **mainfwa** , Version: v0.2-1559-gd08a1d9

 **mainfwb** , Version: v0.2-1482-gf8b43d0

 **To display the running firmware, run the following command:** 

```
# ./penctl.freebsd show running-firmware -i ionic2
```

Output should be similar to:

```
mainfwa
```

This shows that **mainfwa** is the running firmware (v0.2-1559-gd08a1d9)

 **To display the startup firmware (To be started at host next reboot), run command:** 

```
# penctl show startup-firmware -i ionic2
```

Output should be similar to:

```
mainfwa
```

This show that the same firmware **‘mainfwa’** will be used at next reboot

### 5.6.3 Firmware Install

The install process uploads the new firmware to the location that is not currently running (in our case it will be **‘mainfwb’** ).

 **To upload the firmware:** 

1. Obtain the new firmware from pensando, i.e.: ‘ **Naples100\_v0.2-1559-gd08a1d9.tar** ’  
2. Put the firmware file in a known location, for example the home directory  
3. Run the **penctl** command to upload the firmware:  

```
# cd ~
# penctl system firmware-install -f ./Naples100_v0.2-1559-gd08a1d9.tar -i ionic2
```

Output should be similar to:

```
File Copied Successfully

===\u003e Verifying package
Verifying package file: u-boot.img... OK
Verifying package file: kernel.img... OK
Verifying package file: system.img... OK
Package file OK
===\u003e Dry-Run Install
===\u003e Installing mainfwb
(no action)
===\u003e Install mainfwb system_image system.img (119652762 bytes)
(no action)
===\u003e Install mainfwb kernel_fit kernel.img (3242926 bytes)
(no action)
===\u003e Installing uboot
(no action)
===\u003e Install uboot image u-boot.img (313352 bytes)
(no action)
===\u003e Real Install
===\u003e Installing mainfwb
Invalidating /dev/mtd9... OK
===\u003e Install mainfwb system_image system.img (119652762 bytes)
Writing system.img to /dev/mmcblk0p4 (119652762 bytes)...
Writing... OK
Verifying...OK
===\u003e Install mainfwb kernel_fit kernel.img (3242926 bytes)
Writing kernel.img to /dev/mtd9 offset 0 (3242926 bytes)...
Erasing... OK
Writing... OK
Verifying... OK
===\u003e Installing uboot
Invalidating /dev/mtd0... OK
===\u003e Install uboot image u-boot.img (313352 bytes)
Writing u-boot.img to /dev/mtd0 offset 0 (313352 bytes)...
Erasing... OK
Writing... OK
Verifying... OK
Package naples_fw_20181126_1452.tar installed
Package /root/naples_fw_20181126_1452.tar installed
```

This shows that the new firmware was successfully installed in **mainfwb** .

 **To verify that the new firmware is present, run the command:** 

```
# penctl show firmware -j -i ionic2
```

Output should be similar to:

```

{
  "uboot": {
    "image": {
      "build_date": "Mon Nov 26 22:52:10 UTC 2018",
      "build_user": "",
      "base_version": "2018.08-git-gb28f69045e-dirty",
      "software_version": "v0.2-1620-g3359003"
    }
  },
  "mainfwa": {
    "system_image": {
      "build_date": "Tue Nov 20 22:23:28 UTC 2018",
      "build_user": "",
      "base_version": "2018.08-git-gb28f69045e-dirty",
      "software_version": "v0.2-1559-gd08a1d9"
    },
    "kernel_fit": {
      "build_date": "Tue Nov 20 22:23:28 UTC 2018",
      "build_user": "",
      "base_version": "2018.08-git-gb28f69045e-dirty",
      "software_version": "v0.2-1559-gd08a1d9"
    }
  },
  "mainfwb": {
    "system_image": {
      "build_date": "Mon Nov 26 22:52:10 UTC 2018",
      "build_user": "",
      "base_version": "2018.08-git-gb28f69045e-dirty",
      "software_version": "v0.2-1620-g3359003"
    },
    "kernel_fit": {
      "build_date": "Mon Nov 26 22:52:10 UTC 2018",
      "build_user": "",
      "base_version": "2018.08-git-gb28f69045e-dirty",
      "software_version": "v0.2-1620-g3359003"
    }
  },
  "goldfw": {
    "kernel_fit": {
      "version": "br:2018.08-git-g9a91db08e9-dirty fs:v0.2-1182-g35b05e8-dirty"
    }
  },
  "diagfw": {}
}
```

This show that **‘mainfwb’** now has the new firmware (v0.2-1620-g3359003)

### 5.6.4 Set The Startup Firmware Pointer

To set the startup firmware pointer to the new firmware, run the command:



```
# penctl update startup-firmware mainfwb
```

Output should be similar to:



```
main
===\u003e Setting startup firmware to mainfwb
OK
```

This shows that **‘mainfwb’** will be the firmware Naples will boot upon the next host reboot.

To verify and display the startup firmware:



```
# penctl show startup-firmware -i ionic2
```

Output should be similar to:



```
mainfwb
```

 **Please Note** :  This step can be avoided by specifying the "alternate" firmware location during firmware installation with the “-a” option.   Ex:



```
# penctl system firmware-install -f ./Naples100_v0.2-1559-gd08a1d9.tar -a -i ionic2
```

In this case, the subsequent "update startup-firmware" command can be avoided

### 5.6.5 Reboot Host and Verify Running Firmware

The new firmware will now be loaded and run upon the next host reboot.  Please reboot the host during the next maintenance window, since the reboot will impact service.

Once the host has rebooted, verify the current running firmware version.

 **To view the current firmware information, run the command:** 


```
# penctl show firmware -j -i ionic2
```

Output should be similar to:


```
{
  "uboot": {
    "image": {
      "build_date": "Mon Nov 26 22:52:10 UTC 2018",
      "build_user": "",
      "base_version": "2018.08-git-gb28f69045e-dirty",
      "software_version": "v0.2-1620-g3359003"
    }
  },
  "mainfwa": {
    "system_image": {
      "build_date": "Tue Nov 20 22:23:28 UTC 2018",
      "build_user": "",
      "base_version": "2018.08-git-gb28f69045e-dirty",
      "software_version": "v0.2-1559-gd08a1d9"
    },
    "kernel_fit": {
      "build_date": "Tue Nov 20 22:23:28 UTC 2018",
      "build_user": "",
      "base_version": "2018.08-git-gb28f69045e-dirty",
      "software_version": "v0.2-1559-gd08a1d9"
    }
  },
  "mainfwb": {
    "system_image": {
      "build_date": "Mon Nov 26 22:52:10 UTC 2018",
      "build_user": "",
      "base_version": "2018.08-git-gb28f69045e-dirty",
      "software_version": "v0.2-1620-g3359003"
    },
    "kernel_fit": {
      "build_date": "Mon Nov 26 22:52:10 UTC 2018",
      "build_user": "",
      "base_version": "2018.08-git-gb28f69045e-dirty",
      "software_version": "v0.2-1620-g3359003"
    }
  },
  "goldfw": {
    "kernel_fit": {
      "version": "br:2018.08-git-g9a91db08e9-dirty fs:v0.2-1182-g35b05e8-dirty"
    }
  },
  "diagfw": {}
}
```

 **To display the running firmware, run the following command:** 

```
# penctl show running-firmware -i ionic2
```

Output should be similar to:


```
mainfwb
```

This shows that **‘mainfwb’** is now the running firmware (v0.2-1620-g3359003).

This shows that the firmware upgrade process was successful and that the new firmware is now active.  The firmware tar file ~/Naples100\_v0.2-1559-gd08a1d9.tar can be removed or archived if desired.

### 5.6.6 Logs and Support files

 **To retrieve the tech support file:** 



```
# penctl system tech-support -i ionic2
```

Output should be similar to:



```
Collecting tech-support from Naples
Fetching cores...
Cores fetched
Fetching events
Events fetched
Fetching logs................................
Logs fetched
Creating tarball: naples-tech-support.tar.gz
naples-tech-support.tar.gz generated
Please transfer the "naples-tech-support.tar.gz" to Pensando Systems, as directed.
```

 **To retrieve the nmd log from Naples:** 

```
# penctl show logs -m nmd -j -i ionic2
```

Output should be similar to:


```
[{
	"level": "info",
	"ts": "1970-01-01T00:00:02.705189544Z",
	"module": "pen-nmd",
	"caller": "naples_handler.go:341",
	"pid": "700",
	"msg": "NIC in classic mode, mac: "
},{
	"level": "info",
	"ts": "1970-01-01T00:00:02.727667636Z",
	"module": "pen-nmd",
	"caller": "nmd_state.go:347",
	"pid": "700",
	"msg": "Started NMD Rest server at 0.0.0.0:9008"
},{
…..
}]
```

 **To retrieve the tmagent log from Naples:** 


```
# penctl show logs -m tmagent -j -i ionic2
```

Output should be similar to:



```
[{
	"level": "info",
	"ts": "1970-01-01T00:00:02.911603803Z",
	"module": "pen-tmagent",
	"caller": "ipc.go:70",
	"pid": "701",
	"msg": "size of ma: 196608, specified: 196608"
}, {
	"level": "info",
	"ts": "1970-01-01T00:00:02.913174713Z",
	"module": "pen-tmagent",
	"caller": "restapi.go:60",
	"pid": "701",
	"msg": "Starting server at :9013"
}, {
...
}]
```

 **To list all cores dumps on Naples:** 



```
# penctl list cores -i ionic2
```

Output should be similar to:



```
core.asicerrord.5784
core.asicrw.698.19700101000006.gz
core.asicrw.699.19700101000006.gz
```

### 5.6.7 Upgrade penctl

Upgrade is done by replacing the **penctl** binary.

* Download latest version of **penctl** obtained by Pensando  
* Copy the **penctl** binary into the appropriate directory (i.e. /usr/local/bin)  
* Verify the new version:  

```
# penctl -v
```

### 5.7.8 Uninstall penctl

Uninstall is done by deleting the **penctl** binary.

Ex:

```
# rm /usr/local/bin/penctl
```

# 6 NAPLES Troubleshooting

## 6.1 NAPLES Device is not detected by the host.

Address possible reasons:

* Bad PCIe connection (reseat the card in the PCIe slot)  
* PCIe slot is disabled from the BIOS (check BIOS settings)  
* Incorrect firmware image   




Sample device presentation:



```
# lspci -d 1dd8:
5e:00.0 PCI bridge: Device 1dd8:1000
5f:00.0 PCI bridge: Device 1dd8:1001
5f:01.0 PCI bridge: Device 1dd8:1001
5f:02.0 PCI bridge: Device 1dd8:1001
5f:03.0 PCI bridge: Device 1dd8:1001
60:00.0 Ethernet controller: Device 1dd8:1002 
61:00.0 Ethernet controller: Device 1dd8:1002  
62:00.0 Ethernet controller: Device 1dd8:1004  
63:00.0 Processing accelerators: Device 1dd8:1007
```



In the above example:

| 60:00.0 Ethernet controller: Device 1dd8:1002 | NAPLES Ethernet Port 1 |
|-----------------------------------------------|------------------------|
| 61:00.0 Ethernet controller: Device 1dd8:1002 | NAPLES Ethernet Port 2 |
| 62:00.0 Ethernet controller: Device 1dd8:1004 | NAPLES Management Port |
| 63:00.0 Processing accelerators: Device 1dd8:1007 | NAPLES Storage Offload  |

Also check "dmesg" for possible errors.

# 7 Specifications

## 7.1 <NAPLES-100 (OPN TBD)> Specifications

_Table 5. <NAPLES-100 (OPN TBD)> Specification Table_

| Form factor and dimensions | Size | Full Height Half Length<br>4.53 in. x 5.60 in. (115.00mm x 142.24 mm) |
|----------------------------|------|--------------------------------------------------------------------|
|  | Connector | Dual QSFP28 (copper and optical) |
| Protocol Support | Ethernet | 100GBASE-CR4, 100GBASE-KR4, 100GBASE-SR4, 50G Ethernet Consortium, 40GBASE-CR4, 40GBASE-SR4, 40GBASE-LR4, 40GBASE-ER4,
|  | Data Rate | 10/25/40/50/100 Gb/s Ethernet |
|  | PCI Express | Gen 3, SERDES @ 8.0GT/s, 16 lanes; <br>Gen 4, SERDES @ 16.0GT/s, 8 lanes;<br>Gen 2.0 and 1.1 compatible |
| Power and Environmental | Voltage | 12V, 3.3V |
|  | Power | Cable Type |
|  | Typical Power | Passive Cables: |
|  | Maximum Power | Passive Cables: |
|  |  | 1.5W Active Cables/Transceivers: |
|  |  | 2.5W Active Cables/Transceivers: |
|  | Maximum power available through QSFP28 port: 3.5W |  |
|  | Temperature | Operational: 0°C to 55°C |
|  |  | Non-operational: -40°C to 70°C |
|  | Humidity | 90% relative humidity |
|  | Air Flow | See Airflow Specifications on page xxx |
| Regulatory | Safety | CB / cTUVus / CE (to be confirmed) |
|  | EMC | CE / FCC |
|  | ROHS | RoHS-R6 |



## 7.2 Airflow Specifications

_Table 7. Airflow Specification Table_
_1_

| Air Flow (LFM) - TBD |  |  |  |  |  |
|----------------------|---|---|---|---|---|
| Cable Type | Passive | Active 1.5W | Active 2.5W | Active 3.5W | Active 5W |
| NAPLES-100 |    TBD | TBD | TBD | TBD | TBD |

1) Air Flow Direction - Heat Sink to Port
