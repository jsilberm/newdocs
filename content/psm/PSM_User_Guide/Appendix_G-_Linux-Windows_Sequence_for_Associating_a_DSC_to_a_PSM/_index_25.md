---
title: "Appendix G: Linux/Windows Sequence for Associating a DSC to a PSM"
menu:
  docs:
    parent: "PSM Enterprise Edition User Guide"
weight: 26
categories: [psm]
toc: true
---
## Appendix G: Linux/Windows Sequence for Associating a DSC to a PSM
The `penctl` utility is used on both Linux and Windows for upgrading firmware and moving a DSC from “host” to “network managed” mode.
Please refer to the Pensando *Linux Drivers Guide* or *Windows Drivers Guide* for details on installing the corresponding drivers and upgrading to the most recent firmware.
The specific command for associating a DSC to a PSM depends on whether the DSC management IP address is assigned statically or provided by DHCP, and on whether DSC management is done inband or via the OOB interface.  Below are examples of changing DSC mode for these scenarios :
#### Inband, Static IP


```
# penctl update dsc --mgmt-ip 10.0.0.11/24                       \
                     --management-network inband                 \
                     --managed-by network                        \
                     --id dsc-n1                                 \
                     --controllers 10.0.0.100,10.0.0.101,10.0.0.102
  
  

```

#### Inband, DHCP


```
# penctl update dsc --management-network inband           \
                     --managed-by network                 \
                     --id dsc-n1
  
  

```

#### OOB, Static IP


```
# penctl update dsc --mgmt-ip 10.0.0.11/24                \
                     --management-network oob             \
                     --managed-by network                 \
                     --id dsc-n1                          \
                     --inband-ip 10.0.0.21/24             \
                     --controllers 10.0.0.100,10.0.0.101,10.0.0.102
  
  

```

#### OOB, DHCP


```
# penctl update dsc --management-network oob               \
                     --inband-ip 10.0.0.21/24              \
                     --managed-by network
  
  

```
