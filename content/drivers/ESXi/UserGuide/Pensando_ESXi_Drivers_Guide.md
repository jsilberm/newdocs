---
title: ESXi Drivers Guide
menu:
  docs:
    parent: "drivers"
    weight: 2
quicklinks:
weight: 1
draft: false
toc: true
---

Date:      May 15th, 2020

Document Revision History

| Version | Description | Date |
|---------|-------------|------|
| 1.0 | GA Release | May 2020 |

Contents

[[TOC]]

This document describes how to install and test the ESXi package on a single server with a Pensando Distributed Service Card (DSC) installed.

# Prerequisites

| Requirements | Description |
|--------------|-------------|
| Platforms | A server with one of the following Pensando DSCs installed:<br><br>Product<br>Pensando SKU<br>Pensando DSC-25<br>DSC1-2S25-4H8P<br><br>HPE SmartNIC 10/25Gb 2-port 691SFP28 Adapter<br>DSC1-2S25-4H8P-H<br>Pensando DSP DSC-25 10/25G 2p SFP28 Card <br>DSC1-2S25-4H8P-HS<br> |
| Required Space for Installation | 1GB |
| VMware ESXi Operating System | 6.5.0 <br>6.5.0-U1<br>6.5.0-U2<br>6.5.0-U3<br>6.7.0<br>6.7.0-U1<br>6.7.0-U2<br>6.7.0-U3 |
| Installation Privileges | Installation requires "root" privileges |

# ESXi Driver

## Download and Unarchive the ESXi Release Distribution

Download the **ESXi Release Bundle** to your host.

Be sure to download into a location with sufficient disk space (example: /vmfs/volumes/datastore1), and not the root directory.

## Installing ESXi Driver

### Method 1: VIB Install

The ESXi drivers for Pensando are located under the drivers/esxi directory, for each supported release (i.e.: "6.5" or “6.7”), with a corresponding “.vib” suffix (example: ionic-en-1.8-1OEM.670.0.0.8169922.x86_64.vib).

1. Place the host in maintenance mode.  
2. Log in to the ESXi console as root, using SSH, PuTTY, or iLO/DRAC/CIMC.  
3. Install the driver:   






```
[root] esxcli software vib install -v file:///vmfs/volumes/datastore1/drivers/ionic-en-1.8-1OEM.670.0.0.8169922.x86_64.vib -f
Installation Result
  Message: The update completed successfully, but the system needs to be rebooted for the changes to be effective.
  Reboot Required: true
  VIBs Installed: VMW_bootbank_ionic-en-1.8-1OEM.670.0.0.8169922
  VIBs Removed:
  VIBs Skipped:
```

Note: If the install fails due to signature check error, repeat the command with the addition of the --no-sig-check option.

5. Reboot the ESXi host  
6. Exit Maintenance mode on the ESXi host  
7. Verify the driver is installed, using the command  esxcli software vib list or esxcli software vib get -n ionic-en :  


```
[root] esxcli software vib list | grep ionic
ionic-en                       1.8-1OEM.670.0.0.8169922             VMW     VMwareCertified   2020-04-30
```



### Method 2: Offline bundle install

The ESXi driver offline bundles for Pensando are located under the "drivers/esxi" directory, for each supported release (Ex: “6.5” or “6.7”), with a corresponding “.zip” suffix. For example, the ESXi 6.7 driver offline bundle is VMW-ESX-6.7.0-ionic-en-1.8-offline_bundle.zip , located in the drivers/esxi/6.7 directory)

1. Log in to VMware vCenter Server or the ESXi host directly with administrator privileges. Using the Datastore Browser, upload the ...offline-bundle.zip file to a datastore in the ESXi host.  


(Alternatively, log in to the host and use scp to copy the offline bundle file into a directory on a datastore.)

2. Place the host in maintenance mode.  
3. Log in to the ESXi console as root using SSH, PuTTY, or iLO/DRAC/CIMC.  
4. Install the drivers using the offline bundle, with the esxcli command.  Note that this command requires an absolute path.  


```
[root] esxcli software vib install -d "/vmfs/volumes/datastore_name/directory-name/offline-bundle.zip"
```



or



```
[root] esxcli software vib install -d "/vmfs/volumes/9b637d7a-f79de690-af75-818e331bf9ab/driver-directory/VMW-ESX-6.7.0-ionic-en-1.8-offline_bundle.zip"
```

5. Restart the ESXi host.  
6.  Exit maintenance mode.  
7.  To confirm that the VIB is installed successfully, log back into the ESXi host and run the command:  


```
[root] esxcli software vib list | grep -i ionic
```



or



```
[root] esxcli software vib get -n ionic-en
```

## Verifying ESXi Driver Install



```
[root] dmesg | grep ionic
2020-04-30T00:55:09.404Z cpu3:1001390391)Loading module ionic_en ...
2020-04-30T00:55:09.405Z cpu3:1001390391)Elf: SetLicenseInfo:2101: module ionic_en has license BSD
2020-04-30T00:55:09.406Z cpu3:1001390391)<IONIC_INFO> ionic: init module...
2020-04-30T00:55:09.407Z cpu3:1001390391)Mod: LoadDone:4962: Initialization of ionic_en succeeded with module ID 22.
2020-04-30T00:55:09.407Z cpu3:1001390391)ionic_en loaded successfully.
[root] esxcfg-nics -l
Name    PCI          Driver      Link Speed      Duplex MAC Address       MTU    Description
vmnic0  0000:65:00.0 ixgbe       Up   1000Mbps   Full   f8:0f:6f:83:8c:12 1500   Intel(R) Ethernet Controller 10G X550T
vmnic1  0000:65:00.1 ixgbe       Down 0Mbps      Half   f8:0f:6f:83:8c:13 1500   Intel(R) Ethernet Controller 10G X550T
vmnic2  0000:b5:00.0 ionic_en    Up   100000Mbps Full   00:de:ad:be:ef:00 1500   Pensando Systems, Inc Pensando Ethernet PF
vmnic3  0000:b6:00.0 ionic_en    Up   100000Mbps Full   00:de:ad:be:ef:01 1500   Pensando Systems, Inc Pensando Ethernet PF
vmnic4  0000:b7:00.0 ionic_en    Up   1000Mbps   Full   00:de:ad:be:ef:02 1500   Pensando Systems, Inc Pensando Ethernet Management
[root] esxcli hardware pci list
0000:03:00.0
Address: 0000:03:00.0
Segment: 0x0000
Bus: 0x03
Slot: 0x00
Function: 0x0
VMkernel Name: vmnic1
Vendor Name: Pensando Systems, Inc
Device Name: Pensando Ethernet PF
Configured Owner: VMkernel
Current Owner: VMkernel
Vendor ID: 0x1dd8
Device ID: 0x1002
SubVendor ID: 0x1dd8
SubDevice ID: 0x4001
Device Class: 0x0200
Device Class Name: Ethernet controller
Programming Interface: 0x00
Revision ID: 0x00
Interrupt Line: 0x0b
IRQ: 255
Interrupt Vector: 0x00
PCI Pin: 0x00
Spawned Bus: 0x00
Flags: 0x3201
Module ID: 97
Module Name: ionic_en
Chassis: 0
Physical Slot: 4294967295
Slot Description: Chassis slot 2; function 0; relative bdf 02:00.0
Passthru Capable: false
Parent Device: PCI 0:2:0:0
Dependent Device: PCI 0:3:0:0
Reset Method: Function reset
```

FPT Sharable: false

## Upgrading from a Previous Release

The procedure for upgrading the Pensando ionic ethernet driver is similar to the driver installation steps described in the earlier section.

1. Log in to VMware vCenter or the ESXi host directly with administrator privileges. Using the Datastore Browser, upload the ...offline-bundle.zip file to a datastore in the ESXi host.  


(Alternatively, log in to the host and use scp to copy the offline bundle file into a directory on a datastore.)

2. Place the host in maintenance mode.  
3. Log in to the ESXi console as root using SSH or iLO/DRAC/CIMC.  
4. Install the drivers using the offline bundle, with the esxcli command.  Note that this command requires an absolute path.  


For example:



```
[root] esxcli software vib update -d "/vmfs/volumes/datastore_name/directory-name/offline-bundle.zip"
```

or



```
[root] esxcli software vib update -d "/vmfs/volumes/9b637d7a-f79de690-af75-818e331bf9ab/driver-directory/VMW-ESX-6.7.0-ionic-en-1.8-offline_bundle.zip"
```

5. Restart the ESXi host.  
6. To confirm that the VIB is installed successfully, log back into the ESXi host and run the command:  


```
[root] esxcli software vib list | grep -i ionic
```



_7._
Verify the new version of the driver is installed:



```
[root] esxcli software vib get -n ionic-en
```

8. Exit maintenance mode.  


## Removing the Ionic Driver on ESXi

Run the esxcli command to remove the VIB and reboot the host to remove the driver.



```
[root] esxcli software vib remove -n ionic-en
Removal Result
Message: The update completed successfully, but the system needs to be rebooted
for the changes to be effective.
Reboot Required: true
VIBs Installed:
VIBs Removed: VMW_bootbank_ionic-en_1.8-1OEM.650.0.0.4598673
VIBs Skipped:
```

## Verifying ESXi Driver Removal

After the server reboot, use the command below to verify successful removal:



```
[root] esxcli software vib list | grep ionic
```

No ionic software should be listed.

## Upgrading DSC Firmware

Download and unarchive the **DSC Release** **bundle** to your host.

Be sure to download into a location with sufficient disk space (Ex: /vmfs/volumes/datastore1), and not the root directory.

Upgrading firmware for an ESXi host requires the esx-pencli.pyc utility, as provided in the ESXi Release Distribution.

Run the following command to upgrade the DSC to the latest firmware version:



```
[root] esx-pencli upgrade_dsc --fw_img naples_fw_VERSION.tar    
```

Where naples_fw_VERSION.tar  is extracted from the DSC Release distribution and _VERSION_
refers to the specific version .

Reboot the host.

