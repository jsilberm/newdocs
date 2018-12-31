---
title: FreeBSD IONIC Manual for Katana
menu:
  docs:
    parent: "drivers"
    weight: 2
quicklinks:
weight: 1
draft: false
toc: true
---

# FreeBSD IONIC Manual 

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

When complete, reboot and type ‘uname  -a’ to verify.

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

Once the module is loaded and if ARI is disabled, you should see 3 network interfaces



```
ionic0: flags=8802<BROADCAST,SIMPLEX,MULTICAST> metric 0 mtu 1500
	options=e507bb<RXCSUM,TXCSUM,VLAN_MTU,VLAN_HWTAGGING,JUMBO_MTU,VLAN_HWCSUM,TSO4,TSO6,LRO,VLAN_HWFILTER,VLAN_HWTSO,RXCSUM_IPV6,TXCSUM_IPV6>
	ether 00:ae:cd:00:01:3a
	hwaddr 00:ae:cd:00:01:3a
	nd6 options=29<PERFORMNUD,IFDISABLED,AUTO_LINKLOCAL>
	media: Ethernet autoselect (100GBase-CR4 <full-duplex>)
	status: active
ionic1: flags=8802<BROADCAST,SIMPLEX,MULTICAST> metric 0 mtu 1500
	options=e507bb<RXCSUM,TXCSUM,VLAN_MTU,VLAN_HWTAGGING,JUMBO_MTU,VLAN_HWCSUM,TSO4,TSO6,LRO,VLAN_HWFILTER,VLAN_HWTSO,RXCSUM_IPV6,TXCSUM_IPV6>
	ether 00:ae:cd:00:01:3b
	hwaddr 00:ae:cd:00:01:3b
	nd6 options=29<PERFORMNUD,IFDISABLED,AUTO_LINKLOCAL>
	media: Ethernet autoselect (100GBase-CR4 <full-duplex>)
	status: active
ionic2: flags=8802<BROADCAST,SIMPLEX,MULTICAST> metric 0 mtu 1500
	options=e507bb<RXCSUM,TXCSUM,VLAN_MTU,VLAN_HWTAGGING,JUMBO_MTU,VLAN_HWCSUM,TSO4,TSO6,LRO,VLAN_HWFILTER,VLAN_HWTSO,RXCSUM_IPV6,TXCSUM_IPV6>
	ether 00:ae:cd:00:01:3c
	hwaddr 00:ae:cd:00:01:3c
	nd6 options=29<PERFORMNUD,IFDISABLED,AUTO_LINKLOCAL>
	media: Ethernet autoselect (1000Base-KX <full-duplex>)
	status: active
```

NB:  First two ports, **ionic0** and **ionic1** are 100G data ports. **ionic2** is mgmt interface to NIC and is used as the Management port by **_penctl_**
.

## Collecting statistics

*  **Statistics are available through "sysctl dev.ionic.0" and “sysctl dev.ionic1” for the respective ports, providing detailed statistics.   Ex:**   


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

*  **To focus on a particular queue, (e.g. receive queue 0 stats), run:**   


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

*  **To focus on transmit queue 10:**   


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

* Change the MTU size through "ifconfig".  Ex:  


```
# ifconfig ionic0 mtu 1500
```



### Enable/disable checksum, TSO and LRO through "ifconfig"

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

Changing number of queues is done through "kenv" and requires reloading the ionic driver.  Ex:



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
* set hw.ionic.rx\_descs for Receive side descriptors  

```
# kenv hw.ionic.tx_descs=16384
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
