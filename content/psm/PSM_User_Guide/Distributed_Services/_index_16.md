---
title: "Distributed Services"
menu:
  docs:
    parent: "PSM Enterprise Edition User Guide"
weight: 17
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
## Distributed Services
All of the distributed services offered by the Pensando platform can be managed through the PSM, as presented in this section. 
### Security 
#### Network Security Policy Management
Network Security Policies consist of one or more Security Rules within a Security Policy. A Security Rule consists of a 5-tuple: protocol type, source IP address, source port number, destination IP address, and destination port number, along with an Action (Permit, Deny, Reject). The source and destination IP address in the 5-tuple can also include a subnet (e.g “ipaddress/mask”), a comma separated list, or a range of IP addresses allowing users to aggregate policies. Both “deny” and “reject” cause packets matching the rule to be dropped, but "deny” will do it silently, while the "reject" action will include a report back to the source, notifying that the destination is unreachable, or close the connection.
Specifically, the behavior of the "reject" action depending on the type of traffic is as follows:

1. For ICMP traffic, no response, such as “ICMP unreachable”, is sent back to the source.
1. For UDP traffic, an “ICMP unreachable” response is sent back to source.
1. For TCP traffic, a TCP RST segment is sent back to source, which closes the TCP connection.
  

  
![image alt text](/images/PSM/PSM_User_Guide/Distributed_Services/388c46d2ef201700c981b527dc967cf7fd17c2cf.png)
<div style="text-align:center"><font size='2'>*Figure 38. Defining a Security Rule*
</font>

</div>
To edit, re-order or update any Rules within a Policy, select the Rule and click the Edit icon.
  
![image alt text](/images/PSM/PSM_User_Guide/Distributed_Services/4ba544d7f623d002349f744fb654980bf0835ae8.png)
<div style="text-align:center"><font size='2'>*Figure 39. Editing a Rule*
</font>

</div>
**NOTE:** when deploying security policies in dual-DSC deployments (refer to the “Dual DSC-25 Deployment Scenarios” section in the *Pensando DSC-25 Distributed Services Card User Guide For Enterprise Edition* for more information about dual-DSC deployment), flows should be pinned to a specific DSC to avoid packets of the same flow being handled by both cards, which would be problematic when enforcing stateful rules. 
#### App Management
An App object allows a user to define commonly-deployed applications’ protocol/ports, allowing the app’s name to be used in policies instead of repeatedly entering the protocol/port information, as shown Figure 40.


  
![image alt text](/images/PSM/PSM_User_Guide/Distributed_Services/a7442b7c0e9ada1b81438f6b1f28e2a1cea9b8d4.png)

  
![image alt text](/images/PSM/PSM_User_Guide/Distributed_Services/4b40e1077dec1ece2cd9cbd008672c004f6120ff.png)
<div style="text-align:center"><font size='2'>*Figure 40. App objects*
</font>

</div> App objects also allow specifying Application Layer Gateway (ALG) configurations that define application-specific firewall behavior. Supported Apps or ALGs include ICMP, DNS, FTP, SUNRPC, and MSRPC. App objects can be defined based on ALGs only, protocols and ports only, or both, as shown in Figure 41.

  
![image alt text](/images/PSM/PSM_User_Guide/Distributed_Services/14bf9d11df207b0526c33c12247de78a932f01ee.png)<div style="text-align:center">
<font size='2'>*Figure 41. App object definition types*
</font>


</div>
#### Firewall Profile Management
The distributed firewall uses user-imposed session limits and timeouts, to guard against brute-force TCP/UDP/ICMP flooding attacks or DDOS attacks. When the open/active session limit is exceeded, a syslog alert is generated, and any subsequent session establishment requests are dropped in the data-plane thus implicitly protecting the workload and host from flooding attacks.
The PSM user can configure the operating parameters of the distributed stateful firewall implemented across the various DSCs. Figure 42 shows the screen used for this purpose.
  
![image alt text](/images/PSM/PSM_User_Guide/Distributed_Services/6e48089c2316eb8d75cec2bd4dd73a4e408d3445.png)
  
![image alt text](/images/PSM/PSM_User_Guide/Distributed_Services/96433a745fb99b20ddabcc6ab73bac73691af1f3.png)
<div style="text-align:center"><font size='2'>*Figure 42. Firewall profile configuration*
</font>

### </div>
### Firewall Operating Parameters
<div class="p-table center"><div></div>

| <div style="text-align:center"><font size='1'>**Option**<br></font> | <font size='1'>**Description**<br></font> |
| --- | --- || </div>`session-idle-timeout | `Removes/deletes the session/flow if there is inactivity; this value is superseded by any value specified in an App object. Should be a valid time duration between 30s and 48h0m0s. |
| `tcp-connection-setup-timeout | `The period a TCP session is kept to see the response of a SYN. Should be a valid time duration between 1s and 1m0s. |
| `tcp-close-timeout | `The time for which a TCP session is kept after a FIN is seen. Should be a valid time duration between 1s and 5m0s. |
| `tcp-half-closed-timeout | `The time for which a TCP session is kept when connection is half closed i.e. FIN sent but FIN&#95;ACK not received. Should be a valid time duration between 1s and 48h0m0s. |
| `tcp-drop-timeout | `The period for which a drop entry is installed for a denied TCP flow. Should be a valid time duration between 1s and 5m0s. |
| `udp-drop-timeout | `The period for which a drop entry is installed for a denied UDP flow. Should be a valid time duration between 1s and 48h0m0s. |
| `icmp-drop-timeout | `The period for which a drop entry is installed for a denied ICMP flow. Should be a valid time duration between 1s and 5m0s. |

</div>
<div style="text-align:center"><font size='2'>*Table 5.  Firewall operating parameters (part 1/2)*
</font>

</div>

<div class="p-table center"><div></div>

| <div style="text-align:center"><font size='1'>**Option**<br></font> | <font size='1'>**Description**<br></font> |
| --- | --- || </div>`drop-timeout | `The period for which a drop entry is installed for a denied non tcp/udp/icmp flow. Should be a valid time duration between 1s and 5m0s. |
| `tcp-timeout | `The period for which a TCP session is kept alive during inactivity. Should be a valid time duration between 1s and 48h0m0s. |
| `udp-timeout | `UDP Timeout is the period for which a UDP session is kept alive during inactivity. Should be a valid time duration between 1s and 48h0m0s. |
| `icmp-timeout | `The period for which an ICMP session is kept alive during inactivity. Should be a valid time duration between 1s and 48h0m0s. |
| `tcp-half-open-session-limit | `Config after which new open requests will be dropped. Value should be between 0 and 32768. |
| `udp-active-session-limit | `Config after which new requests will be dropped. Value should be between 0 and 32768. |
| `icmp-active-session-limit | `Config after which new requests will be dropped. Value should be between 0 and 32768. |

</div>
<div style="text-align:center"><font size='2'>*Table 5.  Firewall operating parameters (part 2/2)*
</font>

</div>

### Observability
Policies can be created around monitoring and auditing, as outlined below. 
#### Alerts and Events
Creating an Alert Policy involves first creating a destination for the alert, followed by the Event Alert Policy itself. 
  
![image alt text](/images/PSM/PSM_User_Guide/Distributed_Services/058c18642fd6e6f66e664ed921dfebde8e790446.png)
<div style="text-align:center"><font size='2'>*Figure 43. Listing existing alert destinations*
</font>

</div>
First, select the “Destinations” tab and click “Add Destination” to configure the syslog collector that should receive the Alerts and Events.
Next, select the “Event Alert Policies” tab and click “Add Alert Policy” to provide details. In the example below, an event is sent to the destination for any of the DSC actions. Event alert conditions can be combined into a single Alert Policy, (“+AND”) or be created as individual Alert Policies.

  
![image alt text](/images/PSM/PSM_User_Guide/Distributed_Services/b161b3d3d6fb11265c240891d13a5a28477e2f95.png)<div style="text-align:center">
<font size='2'>*Figure 44. Adding an Alert Policy*
</font>

</div>
#### Metrics
Metrics can be charted by selecting the Metrics menu item.
On the Metrics window, click CREATE CHART:

  
![image alt text](/images/PSM/PSM_User_Guide/Distributed_Services/5aa415ccbc22da5fb3aa3cd631c5c92110805f71.png)
<div style="text-align:center"><font size='2'>*Figure 45. Creating a chart*
</font>


</div>Provide a name for the chart, select the Measurement, in this example “Session Summary Statistics”, then select the fields to be displayed. Once selection is done, click the SAVE CHART button to save the selection.
   
![image alt text](/images/PSM/PSM_User_Guide/Distributed_Services/71a676171c5109895eb93b3be990aefdd2c4e9cb.png)
<div style="text-align:center"><font size='2'>*Figure 46. A finished chart in the chart overview*
</font>

</div>
The chart is now saved and can be viewed at any time. 
#### Audit Events
The GUI currently supports exporting Audit Logs as a CSV or JSON file.  Users can filter audit logs using the search tool, as shown in Figure 47:
  
![image alt text](/images/PSM/PSM_User_Guide/Distributed_Services/ab80d3786b3478a65b775bd55298849075223837.png)
<div style="text-align:center"><font size='2'>*Figure 47. Audit Events view*
</font>

</div>
The contents that are exported can be filtered to limit the amount of information, as shown below:

  
![image alt text](/images/PSM/PSM_User_Guide/Distributed_Services/821a271bdb6270f53135b4405ea63f0f77d9da85.png)<div style="text-align:center">
<font size='2'>*Figure 48. Filtering events for export*
</font>

</div>
#### Firewall Logs Export
Firewall logs are gathered from all DSCs and stored centrally within the PSM by default whenever a Security Policy has been configured. The Firewall Logs can be inspected under “Monitoring->Firewall Logs” in the GUI. The Firewall Logs can be exported at any point in time from the GUI, or a “Firewall Log Export Policy” can be configured to continuously stream firewall log records from the DSCs to an external collector. The storage needed for external firewall log collection depends roughly on the following formula:



```
Total Bytes = 300 bytes/log-record * CPS rate * 
              86,400 seconds/day * #days

```

Firewall Log Policies allow logs to be shipped to an external destination:

  
![image alt text](/images/PSM/PSM_User_Guide/Distributed_Services/7283f0987f6c871e894b70cc3d9ba816f9b5531a.png)
<div style="text-align:center"><font size='2'>*Figure 49. Specifying a syslog collector to receive exported firewall logs*
</font>

</div>
They can be selectively configured for export:
  
![image alt text](/images/PSM/PSM_User_Guide/Distributed_Services/f6cdf639fc60a29a5224c5de9753fd0693a39e1f.png)
                          <font size='2'>*Figure 50. Choosing which firewall logs to export*
</font>

In this release, syslog is the only supported firewall log exporting format and collector. 
#### Flow Export
Flow Export (e.g. NetFlow/IPFIX) can be found under the “Troubleshoot” menu.
Flow Export policies can be configured to allow sending information collected for one or more flows matching each rule from DSCs directly to a corresponding receiver. Rules are defined in terms of source and destination IP address and transport port, as well as transport protocol (i.e., 5-tuple). IPFIX is supported as the Flow Export format. The Interval value dictates how often the flow information will be exported. The information provided in the export contains all the current active flows and any new flows matching the rule export definitions.
  
![image alt text](/images/PSM/PSM_User_Guide/Distributed_Services/8930c30cb045e1247900e5727ec107e0a925735c.png)
<div style="text-align:center"><font size='2'>*Figure 51. Defining a Flow Export Policy*
</font>

</div>
**Note:** flow information is always exported through a DSC data interface (uplink).  For in-band management configurations, the management IP address is used as the source address for IPFIX traffic. For OOB management configurations, an exporter address specifically configured on a logical interface of the DSC, mapped to one of the uplink ports, is used as the source address for IPFIX traffic. Please refer to the *DSC-25 Distributed Services Card User Guide* for details on how to configure this address through the `penctl` tool or DHCP (option 242).
**Note:** *When using OOB management, Flow Export cannot be activated unless the exporter address has been configured.*
**Note:** The Target Destination IP address configuration has the following restrictions:

- The destination IP address for the collector cannot be a PSM managed/registered endpoint.
- The destination IP address must be reachable from the in-band management address or the exporter address if OOB management is used.
- Only IPv4 addresses are supported collectors.
  
#### Mirror Sessions
Mirror sessions can be configured for exporting packets through ERSPAN sessions directly from one or more DSCs to an ERSPAN collector. As shown in Figure 52, ERSPAN Type II and Type III are supported and one or more ERSPAN collectors can be configured. Mirror sessions can be configured for flows matching rules specifying IP addresses, transport protocol, and ports (not shown in Figure 52), or for all traffic going through an interface. Labels associated to interfaces or to DSCs can be used to identify interfaces from which traffic should be mirrored. 
  
![image alt text](/images/PSM/PSM_User_Guide/Distributed_Services/eda6b60beb180be6bf03d35d6ec887925f4ba6bf.png)
<div style="text-align:center"><font size='2'>*Figure 52. Configuring Mirror Sessions*
</font>

</div>
**Note:** Mirrored packets are always exported through the data interface. For in-band management configurations, the management IP address is used as the source address for ERSPAN traffic. For OOB management configurations, an exporter address specifically configured on a logical interface of the DSC, mapped to one of the uplink ports, is used as the source address for ERSPAN traffic. Please refer to the *DSC-25 Distributed Services Card User Guide* for details on how to configure such address through the `penctl` tool or DHCP (option 242). **When using OOB management, Mirror Sessions cannot be activated unless the exporter address has been configured.**
**Note:** The Target Destination IP address configuration has the following restrictions:

- The destination IP address for the collector cannot be a PSM managed/registered endpoint.
- The destination IP address must be reachable from the in-band management address or the exporter address if OOB management is used.
- Only IPv4 addresses are supported collectors.
