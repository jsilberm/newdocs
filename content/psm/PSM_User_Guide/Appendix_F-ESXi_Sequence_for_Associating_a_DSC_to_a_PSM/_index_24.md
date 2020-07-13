---
title: "Appendix F: ESXi Sequence for Associating a DSC to a PSM"
menu:
  docs:
    parent: "PSM Enterprise Edition User Guide"
weight: 25
categories: [psm]
toc: true
---
## Appendix F: ESXi Sequence forAssociating a DSC to a PSM
The Pensando ESXi Driver distribution includes the `esx-pencli.pyc` utility, which can be used to:

- Ensure that a DSC has the most recent firmware version installed;
- Move the DSC from “host” to “network” managed mode
  
Please refer to the *Pensando ESXi Drivers Guide* for details on installing the ESXi Drivers and Upgrading to the most recent firmware.

1. Temporarily disable the firewall:
  


```
[root]  esxcli network firewall set -e 0
  
  

```

1. Install the ESXi VIB/drivers, upgrade to latest firmware, and reboot, as per the *Pensando ESXi Drivers Guide*.  Associate to the PSM, per “<ins>Command Syntax Example</ins>” immediately below.
1. Reboot.
1. Re-enable the firewall, if desired:  
  


```
[root] esxcli network firewall set -e 1
  
  
 

```
### Command Syntax Examples
The specific command for associating a DSC to a PSM depends on whether the DSC management IP address is assigned statically or provided by DHCP, and on whether DSC management is done inband or via the OOB interface.  The `esx-pencli.pyc` command is detailed below with examples for the four possible permutations.

1. DHCP with Inband management:
  


```
[root] python esx-pencli.pyc change_dsc_mode --config_opt dhcp --management_network inband --dsc_id bm18-ucs-100g-a.pensando.io --verbose
Changing DSC mode
Status: 200 and reason: OK
Pensando DSC mode has been changed to network managed successfully, please reboot the host
  
  

```

1. DHCP with OOB management:
  


```
[root] python esx-pencli.pyc change_dsc_mode --config_opt dhcp --management_network oob --dsc_id bm18-ucs-100g-a.pensando.io --verbose
Changing DSC mode
Status: 200 and reason: OK
Pensando DSC mode has been changed to network managed successfully, please reboot the host
  
  

```

1. Static with in-band management:
  


```
[root] python esx-pencli.pyc change_dsc_mode --config_opt static --mgmt_ip 20.0.1.18/24 --gw 20.0.1.254  --management_network inband --dsc_id bm18-ucs-100g-a.pensando.io --controllers 20.0.1.61,20.0.1.62,20.0.1.63 --verbose
Changing DSC mode
Status: 200 and reason: OK
Pensando DSC mode has been changed to network managed successfully, please reboot the host
  
  

```

1. Static with OOB management:
  


```
[root]  python esx-pencli.pyc change_dsc_mode --config_opt static --mgmt_ip 20.0.1.18/24 --gw 20.0.1.254 --management_network oob --dsc_id bm18-ucs-100g-a.pensando.io --inband_ip 1.1.1.1/24 --controllers 20.0.1.61,20.0.1.62,20.0.1.63 --verbose
Changing DSC mode
Status: 200 and reason: OK
Pensando DSC mode has been changed to network managed successfully, please reboot the host
  
  

```

The option `--inband_ip` is used to configure an *exporter* address.   Please see <ins>Associating a DSC with a PSM</ins> for details.
