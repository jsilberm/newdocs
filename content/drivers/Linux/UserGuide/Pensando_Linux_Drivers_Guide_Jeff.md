---
title: Linux Drivers Guide 
description: Linux Drivers Guide 
draft: false
toc: true
---


Date:      May 15th, 2020

Document Revision History

| Version | Description | Date |
|---------|-------------|------|
| 1.0 | GA Release | May 2020 |

## Contents

This document describes how to install and test the Linux package on a single server with a Pensando Distributed Service Card (DSC) installed.

## Prerequisites

| Requirements | Description |
|--------------|-------------|
| Platforms | A server with one of the following Pensando DSCs installed:<br><br>Product<br>Pensando SKU<br>Pensando DSC-25<br>DSC1-2S25-4H8P<br><br>HPE SmartNIC 10/25Gb 2-port 691SFP28 Adapter<br>DSC1-2S25-4H8P-H<br>Pensando DSP DSC-25 10/25G 2p SFP28 Card <br>DSC1-2S25-4H8P-HS<br> |
| Required Space for Installation | 1GB |
| Operating System | Linux Operating System.<br>For a complete list of operating systems and distributions supported, please refer to the Linux Driver Release Notes. |
| Installation Privileges | Installation requires "root" privileges |

# Linux Driver

The Linux Release distribution includes RPM packages containing prebuilt versions of the Pensando DSC "ionic" driver software for many Linux distributions. If you are using the standard kernel for any of the included releases, you can simply install the binary driver package.

However, if you are running a modified kernel, you may need to  use the included source RPM to build the driver. The bundle also includes a tar file of driver source and a build script.

Please see the _Release Notes_
for all supported OS and distro versions of the DSC Linux driver.  Using the latest driver software is always recommended for a given OS, which may contain bug fixes not available in the upstream kernel.

## Download and Unarchive the Linux Release Distribution

Download the **Linux Release Bundle** to your host.

Use tar xzvf to un-tar the release distribution, which should have the following general directory structure:



```
drivers/ - contains drivers, source rpms, and driver source for linux
bin/     - contains the "penctl.linux" utility
```

DSC driver installation requires root privileges.

# Build and Install Linux Drivers

1. Installing Prebuilt Drivers  


Select and install the appropriate RPM for the Linux distribution from the drivers/linux directory.  For example, with Red Hat Enterprise Linux 7.6:

```
# rpm -ivh kmod-ionic-1.8.0-1.rhel7u6.x86_64.rpm
```

2. Building from Source RPMs  


Steps for building from source RPMs is as follows:

1. Building from Source RPMs may require installation of the additional packages:  

```
# yum install -y kernel-devel kernel-headers
```

2. Copy the appropriate source RPM for the Linux distribution from the drivers/linux directory to your build directory.  For example, with Red Hat Enterprise Linux 7.6 it is kmod-ionic-1.8.0-1.rhel7u6.src.rpm  


Install the source rpm:



```
# rpm -ivh kmod-ionic-1.8.0-1.rhel7u6.src.rpm
// installs source image in /root/rpmbuild/SOURCES directory
```

3. Change into the source directory. Untar the source, build and load the driver:  


```
# cd /root/rpmbuild/SOURCES/
# tar zxvf kmod-ionic-1.8.0.tar.gz
# cd kmod-ionic-1.8.0
# ./build.sh
# insmod drivers/eth/ionic/ionic.ko
```

3. Building from Source Code  


Building from Source Code may require installation of the additional packages:

```
# yum install -y kernel-devel kernel-headers
```

Unpack the driver source tar package:

```
# xz -d drivers-linux-eth.tar.xz
# tar xvf drivers-linux-eth.tar
```

Change into the source directory. Build and load the driver:

```
# cd drivers-linux-eth/drivers
# make
# insmod eth/ionic/ionic.ko
```

If you see no error messages during installation and driver load, the installation process was successful.

### Verifying Linux Driver Install

Upon successful installation the driver will be loaded into the kernel and Pensando DSC network interfaces will be available to use.

To see if the driver module is loaded use:

```
# lsmod | grep ionic
```

To check the kernel message log for the driver's load information use:

```
# dmesg | grep ionic
```
To see the network interfaces presented, use:



```
# ip addr
[...]
10: enp181s0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc mq state UP group default qlen 1000
    link/ether 00:ae:cd:00:00:08 brd ff:ff:ff:ff:ff:ff
11: enp182s0: <NO-CARRIER,BROADCAST,MULTICAST,UP> mtu 1500 qdisc mq state DOWN group default qlen 1000
    link/ether 00:ae:cd:00:00:09 brd ff:ff:ff:ff:ff:ff
12: enp183s0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc pfifo_fast state UP group default qlen 1000
    link/ether 00:ae:cd:00:00:0a brd ff:ff:ff:ff:ff:ff
```

DSCs can be identified by their 00:ae:cd MAC prefix.

### Ensuring Linux Driver Loads on Reboot

Configure the host to ensure the ionic driver loads after each reboot.  Example: on RHEL/CentOS distributions:



```
# cat <<EOF > /etc/sysconfig/modules/ionic.modules
#!/bin/sh
insmod [...]/drivers-linux/drivers/eth/ionic/ionic.ko
EOF
# chmod 755 /etc/sysconfig/modules/ionic.modules
```

 **Note** : _Be sure to specify the correct path where the driver ".ko" file resides_

 **Note** : _This step is not needed if installing via "rpm"_

Other commands such as ip link can be used to show the available network ports on the Linux system. The Linux command ethtool <netdev-name> can be used to see the speed and link state of the DSC device.

For host-level device statistics and monitoring, please refer to [Appendix A](https://docs.google.com/document/d/1TTQbdyHFWmRsWRCy_u4R70c4aKMkXsI2SPg2dmquDdM/edit#heading=h.8utkv96cwqdv) and the _Pensando Enterprise Troubleshooting_
guide.

### DSC Management Assignment

The penctl CLI tool is used to manage the DSC and install upgrades to its firmware as needed, and is provided as part of the Linux package. Prior to first use, the DSC management interface must be assigned a network address.  Whenever executing penctl, the environment variable DSC_URL must be set.

The following script will set the DSC’s internal link-local address, and show the appropriate command to set DSC_URL:



```
#!/bin/sh
dbdf_list=`lspci -Dnd 1dd8:1004 | awk '{ print $1; }'`
if [ -z "$dbdf_list" ]; then
    echo "No management device 1dd8:1004 found"
    exit 1
fi
for dbdf in $dbdf_list
do
    ifname=`ls /sys/bus/pci/devices/$dbdf/net`
    if [ -z "$ifname" ]; then
        echo "No management interface (load ionic driver)"
        exit 1
    fi
    busx=`echo $dbdf | awk -F : '{ print $2; }'`
    bus=`printf "%d" 0x$busx`
    ipaddr=169.254.$bus.2
    netmask=255.255.255.0
    echo "Setting DSC management interface:"  ifconfig $ifname $ipaddr netmask $netmask
    ifconfig $ifname $ipaddr netmask $netmask
    echo Please run \"export DSC_URL=http://169.254.$bus.1\" before using \'penctl\' to control this DSC
done
```

## Upgrading DSC Firmware

1. Download and unarchive the **DSC Release** **bundle** to your host.  
2. Copy the penctl binary from the **Linux Release bundle** to /usr/local/bin/penctl  
3. Run the following command to upgrade the DSC to the latest firmware version:  


```
# penctl system firmware-install -f naples_fw_VERSION.tar
```

Where naples_fw_VERSION.tar  is extracted from the DSC Release distribution and VERSION refers to the specific version.

4. Reboot the host.  
5. After reboot, run the following command to verify firmware upgrade:  


```
# penctl show firmware-version
```

## Removing the Driver

If you need to remove the Ionic driver package from your system, follow these steps.



Before removing the driver:

* Bring down any associated network interfaces (i.e., ifconfig down)  
* Remove /etc/sysconfig/modules/ionic.modules if created  


If the package was installed via rpm, then uninstall/remove it via:

```
# rpm -evh ionic
```

Unload the active driver:

```
# rmmod ionic
```

Verifying Driver Removal

To verify the driver has been removed, check the kernel message log:

```
# dmesg | grep ionic
```

A message should appear in the output indicating that the driver was removed.

# Appendix A: Linux Debugging Tools

Standard Linux utilities used with network interfaces, such as ifconfig, ip, and ethtool, should work as expected with the Pensando DSC-25.

## Linux Driver Debug Parameters

The metaparameters dyndbg and the file /sys/kernel/debug/dynamic_debug/control can be used to control dynamic debugging to dmesg system utility.

### Driver Statistics

There are several different sets of counters available from the ionic Linux driver; some are collected by software, while some are collected from the hardware. There is also a variety of extra debug statistics that can be enabled if desired.

### Basic ethtool -S Usage

The statistics output from the ethtool -S command are software counters from the driver's internal logic and may not exactly match the hardware counters. As with any other driver, these are vendor-specific counters, and their format and use may change over time. Pensando advises against automating any procedures that depend on this output.

For the most part, this output should be self-explanatory. Note, however, that the tx_csum counter is for non-TSO packets as the tx_tso packets are assumed to have csum offload enabled. Any routine determining the total number of Tx packets that had a checksum offload, must add tx_csum to tx_tso.



```
	$ ethtool -S enp181s0
	NIC statistics:
	     tx_packets: 2373131
	     tx_bytes: 156755278
	     rx_packets: 14431996
	     rx_bytes: 21832254212
	     tx_tso: 0
	     tx_no_csum: 5
	     tx_csum: 2373126
	     rx_csum_none: 2
	     rx_csum_complete: 14431994
	     rx_csum_error: 0
	     tx_0_pkts: 586393
	     tx_0_bytes: 38702366
		...
	     rx_0_pkts: 2033163
	     rx_0_bytes: 3078196946
		...
```

### Debug Extended ethtool -S

There is an extended set of software debug counters that can be enabled for ethtool -S output, via the --set-priv-flags option.

For example:



```
# ethtool --set-priv-flags enp181s0 sw-dbg-stats on
     txq_0_stop: 0
     txq_0_wake: 0
     txq_0_drop: 0
     txq_0_dbell_count: 586393
     txq_0_cq_compl_count: 586393
     txq_0_intr_rearm_count: 0
     txq_0_napi_poll_count: 0
     txq_0_napi_work_done_0: 0
     txq_0_napi_work_done_1: 0
     txq_0_napi_work_done_2: 0
     txq_0_sg_cntr_0: 586393
     txq_0_sg_cntr_1: 0
     txq_0_sg_cntr_2: 0
     txq_0_sg_cntr_3: 0
     rxq_0_cq_compl_count: 2033163
     rxq_0_intr_rearm_count: 792030
     rxq_0_napi_poll_count: 792030
     rxq_0_napi_work_done_0: 167913
     rxq_0_napi_work_done_1: 45891
     rxq_0_napi_work_done_2: 80976
     rxq_0_napi_work_done_3: 321995
```

### Stats in debugfs

There are many statistics available through the Linux debugfs facility.  Rx and Tx queue statistics can be found under a path such as:



```
    # ls /sys/kernel/debug/ionic/0000\:b5\:00.0/lif0/L0-rx0/q/rx_stats
    alloc_err  bytes  csum_complete  csum_error  csum_none  dma_map_err  pkts
    # ls /sys/kernel/debug/ionic/0000\:b5\:00.0/lif0/L0-tx0/q/tx_stats
    bytes  clean  crc32_csum  csum  dma_map_err  frags  linearize  no_csum  pkts  tso
```
