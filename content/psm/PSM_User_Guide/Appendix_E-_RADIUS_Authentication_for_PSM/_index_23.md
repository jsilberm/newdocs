---
title: "Appendix E: RADIUS Authentication for PSM"
menu:
  docs:
    parent: "PSM Enterprise Edition User Guide"
weight: 24
categories: [psm]
toc: true
---
## Appendix E: RADIUS Authentication for PSM
To use RADIUS authentication for the PSM, first create the dictionary file `/etc/freeradius/3.0/dictionary.pensando`.


```
##
######################################################################
#
#       Pensando FreeRADIUS dictionary
#
#
#
######################################################################

VENDOR          Pensando                        51886

BEGIN-VENDOR    Pensando

ATTRIBUTE       Pensando-User-Group                     1       string
ATTRIBUTE       Pensando-Tenant                         2       string

END-VENDOR      Pensando

##
  
  

```

Next, add a line to the master dictionary file `/etc/freeradius/3.0/dictionary` to include the Pensando file:


```
$INCLUDE dictionary.pensando
  
  

```

Below is an example of the syntax for defining two users as part of a RADIUS configuration:


```
--snip--
pen123  Cleartext-Password := "pen123"
        Pensando-User-Group = "NetworkAdmin",
        Pensando-Tenant = "default"
pen456  Cleartext-Password := "pen456"
        Pensando-Tenant = "default"
--snip--
  
  

```
