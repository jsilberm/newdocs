---
title: "Bringing a DSC under PSM Management"
menu:
  docs:
    parent: "PSM Enterprise Edition User Guide"
weight: 14
categories: [psm]
toc: true
---
<style>
   .p-table th {
       align: center;
       border: 1px solid #ccc;
       text-align: center;
       background: #44546A;
       border-color: white;
       font-weight: bold;
       color: white;
   }

   .p-table table {
       margin-left:auto;
       margin-right:auto;
   }

   .p-table td {
       border: 1px solid #ccc;
       text-align: left;
       border-left: none;
       border-right: none;
   }
</style>
## Bringing a DSC under PSM Management
In order to have a DSC managed by the PSM, it is necessary to first have the DSC discovered by the PSM, and then for the PSM admin to authorize the DSC to join the cluster.
### Associating a DSC with a PSM
In order for a DSC to communicate with the PSM, it must have its own management IP address.  As the DSC obtains its address, it must also obtain the IP addresses of its assigned PSM.
There are several options involved in associating a DSC with a PSM:

- In-band versus out-of-band (OOB) access for management traffic
- Static versus DHCP address assignment
  
If the communication between the PSM and a DSC is OOB, then the dedicated physical DSC 1G Ethernet port will be used for management, and that port should be connected to a network through which the PSM is accessible. If the communication is in-band, then management traffic will go through the main uplink ports and the PSM must be configured to use the in-band management network. 
When a service requires the DSC to transfer large amounts of data to a collector, the main uplink ports are used, no matter whether in-band or OOB management is deployed. However, in case of OOB management, the DSC needs an *exporter address* configured to be used as the source for such data export, which must be on the native VLAN, and must not be on the same subnet as the DSC’s management address.
Please note that both in-band management traffic and exported data are transferred through the uplink interfaces untagged; hence the ToR switch associates them to the native VLAN configured on the ports connected to the DSC uplinks.
Independently of whether OOB or in-band communication is deployed, the DSC management IP address can be set either statically or via DHCP. The same applies to the PSM address and the exporter address. 
Associating a DSC to a PSM cluster requires properly setting the following parameters with the appropriate CLI utility (e.g. `penctl` for Linux and Windows, `esx-pencli` for ESXi):
<div class="p-table center"><div></div>

| <div style="text-align:center">**Parameter Name** | **Possible Values/Format** | **Default Values** | **Notes** |
| --- | --- | --- | --- || </div>ID | N/A | N/A | DSC “name”. Typically same as “hostname” |
| ip-address | X.X.X.X/NN | N/A | DSC mgmt IP address and subnet mask if Static.If DHCP, then “” |
| network-mode | INBAND or OOB | OOB | Use INBAND for single-wire management |
| Controllers | [ X.X.X.X, Y.Y.Y.Y, Z.Z.Z.Z ] | N/A | Array of IP addresses for PSM VMs |

</div>
<div style="text-align:center"><font size='2'>*Table 3. DSC parameters necessary for associationwith its assigned PSM cluster*
</font>

</div>The following command is used to statically assign a management address to a DSC for in-band management and provide the address(es) of the PSM:


```
# penctl update dsc -i <DSC hostname> -o network -k inband -m <IP Address/netmask> -g <ip gateway> -c <cluster IP addresses separated by ,> -b <exporter IP address>
  
  

```

The `-o network` option in the example above is used to specify that the DSC should be managed by the PSM, i.e., through the network.
If an IP address and default gateway are not specified, as in the following example where the 1Gb/s management port of the DSC is used for out-of-band management, the DSC will use DHCP to obtain them:


```
# penctl update dsc -i DSC-A -o network -k oob -c 10.1.1.1,10.1.1.2,10.1.1.3 -b 192.168.10.3
  
  

```

In the example above, the -k option indicates whether the DSC management address is assigned on the data uplinks thus implementing inband management (“`inband`”) or on the out-of-band management interface (“`oob`”).  The `-b` option is used to provide the exporter address.
If no information is statically configured, the DSC tries to receive a full configuration (management IP address as well as PSM IP address and exporter address) from a DHCP server through the interface specified with the `-k` option. DHCP Option 43 and Option 242 are used for the assignment of the PSM address(es) and exporter address, respectively. The DHCP configuration process is repeated at each reboot. 
For more information on configuring a DHCP server to provide PSM information, refer to <ins>Appendix D: ISC DHCP Server Example</ins>. 
For information on upgrading a DSC’s firmware and associating it to a PSM in ESXi environments, see <ins>Appendix F</ins>.
For more information on initial installation/configuration of the DSC, please refer to the *DSC User Guide*.
### Admit DSCs Into the PSM Cluster
DSCs that are associated with a PSM are listed in the Distributed Services Cards Overview, shown in Figure 22. The view also displays a few statistics and metrics for admitted cards.
  
![image alt text](/images/PSM/PSM_User_Guide/Bringing_a_DSC_under_PSM_Management/4ccc27757d66e0517456e3c783854525548423c4.png)
<div style="text-align:center"><font size='2'>*Figure 22. Distributed Services Cards Overview screen*
</font>

</div>The PSM admission policy `auto-admit-dscs` controls whether DSCs are admitted automatically or not. It is a cluster-wide attribute that determines whether or not new DSCs are automatically admitted into the PSM cluster once they are connected. The `bootstrap_PSM.py` utility can be used to set the value of `auto-admit-dscs` at cluster creation time.
If set to `true` (the default value), the admission process happens automatically.  If set to `false`, then each DSC must be explicitly admitted into the cluster (via GUI or automated via API). DSCs can be admitted via the PSM GUI by hovering and clicking the right-hand side icon shown in Figure 23.

  
![image alt text](/images/PSM/PSM_User_Guide/Bringing_a_DSC_under_PSM_Management/589c8f9b728c16466ed143ecad65da1102801f28.png)
<div style="text-align:center"><font size='2'>*Figure 23. Admitting a DSC*
</font>

</div>Admitted DSCs can be decommissioned by hovering and clicking the right-hand side icon, as shown in Figure 24.
  
![image alt text](/images/PSM/PSM_User_Guide/Bringing_a_DSC_under_PSM_Management/1bd7eed63d2fb74015d01dd270ea41215d1eb397.png)
<div style="text-align:center"><font size='2'>*Figure 24. Decommissioning a DSC*
</font>


</div>Once a card is decommissioned, it is so indicated, as shown in Figure 25.
  
![image alt text](/images/PSM/PSM_User_Guide/Bringing_a_DSC_under_PSM_Management/e3e2849330478af2f93c395ceb9ca5631f1912a5.png)
<div style="text-align:center"><font size='2'>*Figure 25. DSC is listed as Decommissioned*
</font>

#### </div>
#### Host Management
Host objects are created in one of two ways:

1. Hosts and corresponding DSCs are created implicitly when a PSM is configured to interoperate with vCenter.
1. Hosts are created explicitly and associated to their DSC(s) in the PSM. 
  
A Host can be added by specifying a logical ID or the mac-address of a corresponding DSC, as shown in Figure 26. Note that the mac-address format is “xxxx.yyyy.zzzz”.
  
![image alt text](/images/PSM/PSM_User_Guide/Bringing_a_DSC_under_PSM_Management/feb06b5ccaea328518d46c01a1431876e4b7546b.png)
<div style="text-align:center"><font size='2'>*Figure 26. Select name type for this Host object*
</font>

</div>The PSM will associate the Host object to the appropriate DSC object. As shown in Figure 27, if Workload objects have been created and associated to Hosts, they appear in the Hosts Overview.
  
![image alt text](/images/PSM/PSM_User_Guide/Bringing_a_DSC_under_PSM_Management/c012fd827f9bad937d26a9f329ad536c889a7cfe.png)
<div style="text-align:center"><font size='2'>*Figure 27. Hosts Overview*
</font>

</div>Hosts can be deleted by checking one or more corresponding Hosts and clicking the delete icon, as shown above in Figure 27. Hosts cannot be deleted if they have any associated workloads. When a PSM is configured to interoperate with vCenter, then PSM hosts will be automatically deleted if any ESXi hosts are deleted, as vCenter configuration is reconciled with the PSM.
