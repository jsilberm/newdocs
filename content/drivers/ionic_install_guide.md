---
title: IONIC Manual for FreeBSD
description: IONIC Manual for FreeBSD
menu:
  docs:
    parent: "drivers"
    weight: 2
quicklinks:
weight: 1
draft: false
toc: true
---

## Introduction

This document provides prerequisites and instructions for building and testing the Pensando IONIC device driver on FreeBSD

## Pre-requisites

Compiling the Pensando IONIC FreeBSD driver requires having FreeBSD source code including kernel source code.

Clone the FreeBSD github repo to checkout FreeBSD Head (12 branch):



```
$ git clone http://github.com/freebsd/freebsd /usr/src
```

Checkout the 11.2 source branch:



```
$ cd /usr/src
$ git checkout  remotes/origin/releng/11.2 -b releng11.2
```

### Configure the FreeBSD Kernel

The IONIC driver requires certain options from the running kernel.  If the running kernel does not support **OFED** and **COMPAT\_LINUXKPI** options, then the kernel will need to be rebuilt.

Add following lines in sys/amd64/conf/GENERIC, anywhere in the file:



```
options 	OFED
options 	COMPAT_LINUXKPI
```

*  **COMPAT\_LINUXKPI** is required for the sonic/storage accelerator driver and ionic\_rdma.  
*  **OFED** is required for RDMA  


Create file /etc/src.conf and add the following line:



```
WITH_OFED='yes'
```

### Build the FreeBSD Kernel



```
$ make -j 8  buildworld buildkernel installworld installkernel
```

When complete, reboot and type `uname  -a` to verify.

## Ethernet

### Building ionic

There are two ways to get Pensando driver source code.

* Checkout Pensaod/sw or copy platform/driver/freebsd directory to the required host and go to platform/drivers/freebsd/usr/src  
* Copy driver-freebsd.tar.gz package from build to host  


```
$ env OS_DIR=/usr/src ./build.sh
```



### Loading ionic

Before installing Pensando drivers, make sure all the devices are visible on PCI bus. Verify as below:



```
# pciconf -l |grep 1dd8
pcib9@pci0:94:0:0:      class=0x060400 card=0x40011dd8 chip=0x10001dd8 rev=0x00 hdr=0x01
pcib10@pci0:95:0:0:     class=0x060400 card=0x40011dd8 chip=0x10011dd8 rev=0x00 hdr=0x01
pcib11@pci0:95:1:0:     class=0x060400 card=0x40011dd8 chip=0x10011dd8 rev=0x00 hdr=0x01
pcib12@pci0:95:2:0:     class=0x060400 card=0x40011dd8 chip=0x10011dd8 rev=0x00 hdr=0x01
ion0@pci0:96:0:0:       class=0x020000 card=0x40011dd8 chip=0x10021dd8 rev=0x00 hdr=0x00 << Network
ion1@pci0:97:0:0:       class=0x020000 card=0x40011dd8 chip=0x10021dd8 rev=0x00 hdr=0x00  << Network
none135@pci0:98:0:0:    class=0xff0000 card=0x40011dd8 chip=0x10071dd8 rev=0x00 hdr=0x00 << Storage accelerator
```
If system doesn’t list all the above devices, add the following line in **/boot/loader.conf** and reboot:



```
hw.pci.enable_ari="0"
```

Once the driver is built, you can load the **ionic** NIC/Ethernet driver:



```
# kldload sys/modules/ionic/ionic.ko
```

To load the **ionic** RDMA driver:



```
# kldload sys/modules/ionic_rdma/ionic_rdma.ko
```

### Configure Network interface

Configure and bring up the network interface.   Ex:



```
 # ifconfig ionic0 10.1.1.1
```

Verify the address is configured.  Ex:



```
 # ifconfig ionic0
ionic0: flags=8843<UP,BROADCAST,RUNNING,SIMPLEX,MULTICAST> metric 0 mtu 1500
       options=e507bb<RXCSUM,TXCSUM,VLAN_MTU,VLAN_HWTAGGING,JUMBO_MTU,VLAN_HWCSUM,TSO4,TSO6,LRO,VLAN_HWFILTER,VLAN_HWTSO,RXCSUM_IPV6,
TXCSUM_IPV6>
       ether 00:02:00:00:01:03
       hwaddr 00:02:00:00:01:03
       inet 10.1.1.1 netmask 0xff000000 broadcast 10.255.255.255  
       nd6 options=29<PERFORMNUD,IFDISABLED,AUTO_LINKLOCAL>
       media: Ethernet autoselect (100GBase-CR4 <full-duplex>)
       status: active
```

### Basic ionic Test

* Ping sanity test  


```
# ping 10.1.1.2
PING 10.1.1.2 (10.1.1.2): 56 data bytes
64 bytes from 10.1.1.2: icmp_seq=0 ttl=64 time=0.247 ms
64 bytes from 10.1.1.2: icmp_seq=1 ttl=64 time=0.033 ms
^C
--- 10.1.1.2 ping statistics ---
2 packets transmitted, 2 packets received, 0.0% packet loss

round-trip min/avg/max/stddev = 0.033/0.140/0.247/0.107 ms
```
### Performance ionic Test (iperf)

*  **Start iperf3 server on other end**   


```
# ifconfig enp94s0f0
enp94s0f0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500
       inet 10.1.1.2  netmask 255.0.0.0  broadcast 10.255.255.255
       inet6 fe80::268a:7ff:fea5:2940  prefixlen 64  scopeid 0x20<link>
       ether 24:8a:07:a5:29:40  txqueuelen 1000  (Ethernet)
       RX packets 54046959744  bytes 76438965608198 (76.4 TB)
       RX errors 0  dropped 125919  overruns 0  frame 0
       TX packets 52827427998  bytes 78088427628680 (78.0 TB)
       TX errors 0  dropped 0 overruns 0  carrier 0  collisions 0
# iperf3 -s          
-----------------------------------------------------------
Server listening on 5201
-----------------------------------------------------------
```

*  **Start iperf3 client from ionic, IP address 10.1.1.1. This will generate transmit side traffic.**   


```
 # iperf3 -c 10.1.1.2 -i 1 -t 60
Connecting to host 10.1.1.2, port 5201
[  5] local 10.1.1.1 port 37457 connected to 10.1.1.2 port 5201
[ ID] Interval           Transfer     Bitrate         Retr  Cwnd
[  5]   0.00-1.00   sec  2.79 GBytes  24.0 Gbits/sec    0    626 KBytes        
[  5]   1.00-2.00   sec  2.95 GBytes  25.4 Gbits/sec    0    704 KBytes      
```



..

*  **To stress Receive side, use -R which will create traffic in reverse flow.**   


```
 # iperf3 -c 10.1.1.2 -i 1 -t 60 -R
Connecting to host 10.1.1.2, port 5201
Reverse mode, remote host 10.1.1.2 is sending
[  5] local 10.1.1.1 port 61119 connected to 10.1.1.2 port 5201
[ ID] Interval           Transfer     Bitrate
[  5]   0.00-1.00   sec  2.52 GBytes  21.6 Gbits/sec                   
[  5]   1.00-2.00   sec  2.47 GBytes  21.2 Gbits/sec
```

*  **Iperf3 also has option to generate JSON output using -J**   


#### Iperf for UDP

*  **Start iperf3 client from ionic, IP address 10.1.1.1. This will generate transmit side traffic.**   


```
 # iperf3 -c 100.1.1.2 -i 1 -u -b 100G
Connecting to host 100.1.1.2, port 5201
[  5] local 100.1.1.1 port 10961 connected to 100.1.1.2 port 5201
[ ID] Interval           Transfer     Bitrate         Total Datagrams
[  5]   0.00-1.00   sec   501 MBytes  4.21 Gbits/sec  360096   
[  5]   1.00-2.00   sec   503 MBytes  4.22 Gbits/sec  360907   
[  5]   2.00-3.00   sec   502 MBytes  4.22 Gbits/sec  360889 
```

*  **Use -R to generate traffic in reverse direction.**   


```
 # iperf3 -c 10.1.1.2 -i 1 -t 60 -R
```



Connecting to host 10.1.1.2, port 5201

## Collecting statistics

*  **Run sysctl dev.ionic.0, it will provide very detailed statistics.**   


```
# sysctl dev.ionic.0
...
dev.ionic.0.txq15.dma_map_error: 0
dev.ionic.0.txq15.num_descs: 16384
dev.ionic.0.txq15.comp_index: 9521
dev.ionic.0.txq15.tail: 9521
dev.ionic.0.txq15.head: 9522
dev.ionic.0.txq14.tso_max_sg: 0
dev.ionic.0.txq14.tso_max_size: 0
dev.ionic.0.txq14.tso_ipv6: 0
dev.ionic.0.txq14.tso_ipv4: 0
dev.ionic.0.txq14.no_csum_offload: 0
dev.ionic.0.txq14.csum_offload: 224802440
dev.ionic.0.txq14.bytes: 15288359411
dev.ionic.0.txq14.pkts: 224802440
dev.ionic.0.txq14.bad_ethtype: 0
dev.ionic.0.txq14.linearize_err: 0
dev.ionic.0.txq14.linearize: 0
dev.ionic.0.txq14.no_descs: 0
dev.ionic.0.txq14.pkts_retry: 0
dev.ionic.0.txq14.tx_clean: 284816431
dev.ionic.0.txq14.dma_map_error: 0
dev.ionic.0.txq14.num_descs: 16384
```

*  **In case you are interested in particular queue, say receive queue 0 stats, run:**   


```
# sysctl dev.ionic.0.rxq0
dev.ionic.0.rxq0.rss_unknown: 0
dev.ionic.0.rxq0.rss_udp_ip6_ex: 0
dev.ionic.0.rxq0.rss_tcp_ip6_ex: 0
dev.ionic.0.rxq0.rss_ip6_ex: 0
dev.ionic.0.rxq0.rss_udp_ip6: 0
dev.ionic.0.rxq0.rss_tcp_ip6: 0
dev.ionic.0.rxq0.rss_ip6: 0
dev.ionic.0.rxq0.rss_udp_ip4: 0
dev.ionic.0.rxq0.rss_tcp_ip4: 313362
dev.ionic.0.rxq0.rss_ip4: 0
dev.ionic.0.rxq0.lro_bad_csum: 0
dev.ionic.0.rxq0.lro_flushed: 240745
dev.ionic.0.rxq0.lro_queued: 312625
dev.ionic.0.rxq0.mbuf_free: 0
dev.ionic.0.rxq0.mbuf_alloc: 329633
dev.ionic.0.rxq0.isr_count: 185068
dev.ionic.0.rxq0.csum_l4_bad: 0
dev.ionic.0.rxq0.csum_l4_ok: 313362
dev.ionic.0.rxq0.csum_ip_bad: 0
dev.ionic.0.rxq0.csum_ip_ok: 313362
dev.ionic.0.rxq0.bytes: 20691314
dev.ionic.0.rxq0.pkts: 313376
dev.ionic.0.rxq0.comp_err: 0
dev.ionic.0.rxq0.alloc_error: 0
dev.ionic.0.rxq0.dma_setup_error: 0
dev.ionic.0.rxq0.num_descs: 16384
dev.ionic.0.rxq0.comp_index: 2080
dev.ionic.0.rxq0.tail: 2080
dev.ionic.0.rxq0.head: 1953
```

*  **Similarly for transmit side.**   


```
# sysctl dev.ionic.0.txq10
dev.ionic.0.txq10.tso_max_sg: 0
dev.ionic.0.txq10.tso_max_size: 0
dev.ionic.0.txq10.tso_ipv6: 0
dev.ionic.0.txq10.tso_ipv4: 0
dev.ionic.0.txq10.no_csum_offload: 0
dev.ionic.0.txq10.csum_offload: 0
dev.ionic.0.txq10.bytes: 0
dev.ionic.0.txq10.pkts: 0
dev.ionic.0.txq10.bad_ethtype: 0
dev.ionic.0.txq10.linearize_err: 0
dev.ionic.0.txq10.linearize: 0
dev.ionic.0.txq10.no_descs: 0
dev.ionic.0.txq10.pkts_retry: 0
dev.ionic.0.txq10.tx_clean: 14
dev.ionic.0.txq10.dma_map_error: 0
dev.ionic.0.txq10.num_descs: 16384
dev.ionic.0.txq10.comp_index: 0
dev.ionic.0.txq10.tail: 0
dev.ionic.0.txq10.head: 0
```



### Change MTU size

* To change the MTU size, run following  


```
# ifconfig ionic0 mtu 1500
```

* Verify by running ifconfig  


```
# ifconfig ionic0

ionic0: flags=8843<UP,BROADCAST,RUNNING,SIMPLEX,MULTICAST> metric 0 mtu 1500
```
### Enabling/disabling checksum, TSO and LRO

Ex:



```
# ifconfig ionic0 -rxcsum — Disable Rx checksum
# ifconfig ionic0 rxcsum — Reenable Rx checksum
# ifconfig ionic0 -txcsum — Disable Tx checksum
# ifconfig ionic0 txcsum — Reeable Tx checksum
# ifconfig ionic0 -tso — Disable TSO
# ifconfig ionic0 tso — Re-enable TSO
# ifconfig ionic0 -lro — Disable LRO
# ifconfig ionic0 lro — Reenable LRO
```

### Changing number of queues

Changing number of queues require reloading the ionic driver.



```
root # kenv hw.ionic.max_queues=8
hw.ionic.max_queues="8"
root# kldunload ionic
root # kldload ionic.ko
root # sysctl hw.ionic
hw.ionic.max_sg: 0
hw.ionic.rx_coalesce_usecs: 64
hw.ionic.tx_coalesce_usecs: 64
hw.ionic.rx_process_limit: 128
hw.ionic.tx_clean_threshold: 128
hw.ionic.rx_fill_threshold: 128
hw.ionic.rx_stride: 32
hw.ionic.rx_descs: 16384
hw.ionic.tx_descs: 16384
hw.ionic.adminq_descs: 16
hw.ionic.enable_msix: 1
hw.ionic.max_queues: 8 << Number of queues is 8 now.
```

### Changing Ring size

To change the ring size:

* set hw.ionic.tx\_descs for Transmit side descriptors  

```
# kenv hw.ionic.tx_descs=16384
```

* set hw.ionic.rx\_descs for Receive side descriptors  


```
# kenv hw.ionic.rx_descs=16384
```

* Verify by running:  


```
# sysctl hw.ionic
hw.ionic.max_sg: 0
hw.ionic.rx_coalesce_usecs: 64
hw.ionic.tx_coalesce_usecs: 64
hw.ionic.rx_process_limit: 128
hw.ionic.tx_clean_threshold: 128
hw.ionic.rx_fill_threshold: 128
hw.ionic.rx_stride: 32
hw.ionic.rx_descs: 16384
hw.ionic.tx_descs: 16384
hw.ionic.adminq_descs: 16
hw.ionic.enable_msix: 1
hw.ionic.max_queues: 16
```

* Reload ionic driver  

```
# kldunload ionic
# kldload ionic.ko
```

## RDMA/RoCEv2

These steps pertain to building RDMA driver ("ionic\_rdma.ko").

The ionic.ko module must be loaded before the ionic\_rdma.ko module.

### FreeBSD Module Parameters

These are rdma module parameters and descriptions:



```
compat.linuxkpi.ionic_rdma_max_gid: Max number GIDs.
compat.linuxkpi.ionic_rdma_max_pd: Max number of PDs.
compat.linuxkpi.ionic_rdma_rqcmb_order: Only alloc rq cmb less than order.
compat.linuxkpi.ionic_rdma_rqcmb_sqcmb: Only alloc rq cmb if sq is cmb.
compat.linuxkpi.ionic_rdma_sqcmb_order: Only alloc sq cmb less than order.
compat.linuxkpi.ionic_rdma_sqcmb_inline: Only alloc sq cmb for inline data capability.
compat.linuxkpi.ionic_rdma_work_budget: Max events to poll per round in work context.
compat.linuxkpi.ionic_rdma_isr_budget: Max events to poll per round in isr context.
compat.linuxkpi.ionic_rdma_eq_depth: Min depth for event queues.
compat.linuxkpi.ionic_rdma_aq_depth: Min depth for admin queues.
compat.linuxkpi.ionic_rdma_dbgfs_enable: Expose resource info in debugfs.
compat.linuxkpi.ionic_rdma_dyndbg_enable: Print to dmesg for dev_dbg, et al.
```

Of the above parameters, the following can also be changed at runtime:



```
compat.linuxkpi.ionic_rdma_rqcmb_order: Only alloc rq cmb less than order.
compat.linuxkpi.ionic_rdma_rqcmb_sqcmb: Only alloc rq cmb if sq is cmb.
compat.linuxkpi.ionic_rdma_sqcmb_order: Only alloc sq cmb less than order.
compat.linuxkpi.ionic_rdma_sqcmb_inline: Only alloc sq cmb for inline data capability.
compat.linuxkpi.ionic_rdma_dyndbg_enable: Print to dmesg for dev_dbg, etc.
```

For user space, there is a corresponding libionic.so which is built by our build script.  For freebsd, applications should be built referencing this library as a dependency.  If not, this can be loaded by LD\_PRELOAD.  (FreeBSD)

### Linux Module Parameters

These are the module params and descriptions, from `modinfo ionic\_rdma.ko`:



```
parm:           dbgfs:Enable debugfs for this driver. (bool)
parm:           aq_depth:Min depth for admin queues. (ushort)
parm:           eq_depth:Min depth for event queues. (ushort)
parm:           isr_budget:Max events to poll per round in isr context. (ushort)
parm:           work_budget:Max events to poll per round in work context. (ushort)
parm:           sqcmb_inline:Only alloc sq cmb for inline data capability. (bool)
parm:           sqcmb_order:Only alloc sq cmb less than order. (int)
parm:           rqcmb_sqcmb:Only alloc rq cmb if sq is cmb. (bool)
parm:           rqcmb_order:Only alloc rq cmb less than order. (int)
parm:           max_pd:Max number of PDs. (int)
parm:           max_gid:Max number of GIDs. (int)
```

Of the above parameters, these can also be modified at runtime via sysfs:



```
/sys/module/ionic_rdma/parameters/sqcmb_inline
/sys/module/ionic_rdma/parameters/sqcmb_order
/sys/module/ionic_rdma/parameters/rqcmb_inline
/sys/module/ionic_rdma/parameters/rqcmb_order
```

The metaparameter dyndbg and the file /sys/kernel/debug/dynamic\_debug/control can be used to control dynamic debugging to dmesg.

For user space, libionic\_rdmav19.so is built with, and can be installed with rdma-core according to the build and install instructions of rdma-core.  We provide a copy of rdma-core with our driver added.  The version v19 comes from rdma-core, and changes with the rdma-core release cycle.

RDMA device information:

```
ibv_devinfo [-v]
```

