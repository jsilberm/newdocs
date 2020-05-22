---
title: Windows Drivers Guide
description: Pensando Windows Drivers Guide
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


This document describes how to install and test the Windows package on a single server with a Pensando Distributed Service Card (DSC) installed.

# Prerequisites

| Requirements | Description |
|--------------|-------------|
| Platforms | A server with one of the following Pensando DSCs installed:<br><br>Product<br>Pensando SKU<br>Pensando DSC-25<br>DSC1-2S25-4H8P<br><br>HPE SmartNIC 10/25Gb 2-port 691SFP28 Adapter<br>DSC1-2S25-4H8P-H<br>Pensando DSP DSC-25 10/25G 2p SFP28 Card <br>DSC1-2S25-4H8P-HS<br> |
| Required Space for Installation | 1GB |
| Operating System | Microsoft Windows Server 2019<br>Microsoft Windows Server 2016 |
| Installation Privileges | Installation requires "Administrator" privileges |

# Windows Driver

## Installing Windows Driver

Download the **Windows Release Bundle** to your host.

The file "drivers-windows.zip" contains the following contents:

![image alt text](/images/drivers/windows/image_1.png)

_Figure 4. Contents of the Windows ionic driver bundle_

As Administrator, run the installer script named IonicInstaller-1.8.0.XXXX-E, (where _XXXX_
will represent the build number)

![image alt text](/images/drivers/windows/image_2.png)

_Figure 5. Ionic driver setup wizard_

Click through to accept the End User License Agreement (EULA).

Select "Custom" to install in a specific directory, otherwise select “Typical” or “Complete”.

To install in non-interactive mode, run:



```
C:\> msiexec /i IonicInstaller-1.8.0.XXXX-E ./quiet
```

(where XXXX will represent the build number)

## Verifying Windows Driver Install

The DSC interfaces should be visible in the Windows Device Manager as shown in Figure 8:

![image alt text](/images/drivers/windows/image_3.png)

_Figure 6. DSC interfaces as shown in the Windows Device Manager_

The installer creates a shortcut on the Desktop for easy access to the command line tools.

![image alt text](/images/drivers/windows/image_4.png)

_Figure 7.  Windows Desktop shortcut_

Click on the shortcut to bring up a CLI window. The Penctl and IonicConfig utilities should be visible:

![image alt text](/images/drivers/windows/image_5.png)

_Figure 8. Driver Tools directory_

IonicConfig.exe can be used to query/set any physical layer statistics and configuration settings:

![image alt text](/images/drivers/windows/image_6.png)

_Figure 9. IonicConfig options_

To validate that the driver installed properly, run the command IonicConfig Port. Three Ethernet interfaces should be present per DSC card, as shown in Figure 10.



![image alt text](/images/drivers/windows/image_7.png)

_Figure 10. Output from_
IonicConfig Port _command_

Run the command penctl show dsc to validate proper communication with the DSC, as shown in Figure 11:

![image alt text](/images/drivers/windows/image_8.png)

_Figure 11. Output from_
penctl show dsc _command_

## Upgrading DSC Firmware

Download and unarchive the DSC Release distribution from [https://pensando.force.com/portal/s/downloads](https://pensando.force.com/portal/s/downloads)

Run the penctl system firmware-install command to upgrade the DSC to the latest firmware version. For example, if the DSC Release was downloaded to the Desktop:



```
    C:\> penctl system firmware-install -f C:\Users\Administrator\Desktop\PNSO-1.8.0-E-17-dsc-04302020-1425\fw\naples_fw_VERSION.tar
```

Reboot the server.   (NB: _VERSION_
refers to the specific version of firmware)

After reboot, run the following command to verify the firmware upgrade:

C:\> penctl show firmware-version

## Removing Driver on Windows

Run the IonicInstaller script and select the "Remove" option, as shown in Figure 12:

![image alt text](/images/drivers/windows/image_9.png)

_Figure 12. Select the Remove option from the Setup wizard_

To uninstall in non-interactive mode, run:



```
C:\> msiexec /x IonicInstaller-1.8.0.XXXX-E ./quiet
```

(where XXXX will represent the build number)

Uninstall/Change/Repair can also be done from :

"Control Panel\Programs\Programs and Features"

