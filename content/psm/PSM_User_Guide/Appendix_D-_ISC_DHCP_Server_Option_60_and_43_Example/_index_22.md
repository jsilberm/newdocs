---
title: "Appendix D: ISC DHCP Server Option 60 and 43 Example"
menu:
  docs:
    parent: "PSM Enterprise Edition User Guide"
weight: 23
categories: [psm]
toc: true
---
## Appendix D:  ISC DHCP Server Option 60 and 43 Example
ISC DHCP configs for Option 60 Request and Option 43 Response.


```
option space pensando;
option pensando.wlc code 241 = array of ip-address;

  class "PensandoClass" {
    match if option vendor-class-identifier = "Pensando";
    vendor-option-space pensando;
    option pensando.wlc  1.1.1.1,2.2.2.2;
  }
  
  

```

Sample `/etc/dhcp/dhcpd.conf` configuration file:


```
#
# DHCP Server Configuration file.
#   see /usr/share/doc/dhcp*/dhcpd.conf.example
#   see dhcpd.conf(5) man page

# option definitions common to all supported networks...
option domain-name "demo.local";
option domain-name-servers 8.8.8.8, 10.29.9.9;

#### Options below is for Pensando forwarding option 43 for DSCs #######
#### These are global options
option space pensando;
option pensando.wlc code 241 = array of ip-address;
option rfc3442-classless-static-routes code 121 = array of integer 8;

default-lease-time 600;
max-lease-time 7200;

# If this DHCP server is the official DHCP server for the local
# network, the authoritative directive should be uncommented.
authoritative;

# Subnet Declarations
# 10.29.65.21,10.29.65.22 are IPaddrs for PSM nodes

subnet 10.29.65.0 netmask 255.255.255.0 {
  range 10.29.65.64 10.29.65.70;
  option routers 10.29.65.1;
  if option vendor-class-identifier = "Pensando" {
     vendor-option-space pensando;
     option pensando.wlc 10.29.65.21,10.29.65.22;
  }
}


# Host Declarations
# 10.29.65.21,10.29.65.22 are IPaddrs for PSM nodes

host pod-5-dsc-1 {
    hardware ethernet 00:AE:CD:01:0A:6E;
    fixed-address 10.29.65.61;
    option host-name "pod-5-dsc-1";
    if option vendor-class-identifier = "Pensando" {
     vendor-option-space pensando;
     option pensando.wlc 10.29.65.21,10.29.65.22;
    }
}

host pod-5-dsc-2 {
    hardware ethernet 00:ae:cd:01:1d:ee;
    fixed-address 10.29.65.62;
    option host-name "pod-5-dsc-2";
    if option vendor-class-identifier = "Pensando" {
     vendor-option-space pensando;
     option pensando.wlc 10.29.65.21,10.29.65.22;
    }
}
  
  

```
