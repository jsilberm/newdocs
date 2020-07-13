---
title: "PSM Platform Management"
menu:
  docs:
    parent: "PSM Enterprise Edition User Guide"
weight: 18
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
## PSM Platform Management
### Platform Monitoring
The GUI offers a Cluster Overview that displays the health and status of the PSM cluster itself and the various admitted DSCs. Platform-wide Events and Alerts are also displayed and managed at the bottom of this page.
Events are displayed for the past day by default. Click on “Past day” to change to a different time scope, as shown in Figure 53.
  
![image alt text](/images/PSM/PSM_User_Guide/PSM_Platform_Management/40aeb856f6066f6a9424e674d5db4272a074efc4.png)
<div style="text-align:center"><font size='2'>*Figure 53. Changing time scope for event display*
</font>

</div>
Alerts can be in an *acknowledged* or *resolved* state. The acknowledged state indicates that the user has seen the alert and is aware of it, but still considers the alert to be active. If the same condition occurs again, no new alert will be created. Alerts in an acknowledged state remain indefinitely.
The resolved state indicates that the user believes that the issue that generated the alert is fixed. If the same condition occurs again, a new alert will be created. Alerts in a resolved state are automatically deleted after 24 hours.
To acknowledge an alert, hover and click the icon on the right-hand side of the alert item, as shown in Figure 54. Users can also click multiple checkboxes to resolve multiple alerts at once.
  
![image alt text](/images/PSM/PSM_User_Guide/PSM_Platform_Management/4dc8e13d5ea117aca5c0c27e49e9fcfa2abeed7c.png)
<div style="text-align:center"><font size='2'>*Figure 54.  Accessing the alert acknowledgement icon*
</font>

</div>
#### Archive Logs
Events and Audit events can be archived to be downloaded from the PSM and analyzed with other tools or browsed at a later time.
Archiving is possible by clicking the corresponding export button in the Events and Audit Events screens shown in Figure 55.
  
![image alt text](/images/PSM/PSM_User_Guide/PSM_Platform_Management/e9b466b1da82d41ea9d74218047ab507ed94ecc4.png)

  
![image alt text](/images/PSM/PSM_User_Guide/PSM_Platform_Management/2504df7d3fb1a02e7415cb949d8061d8c9717b2a.png)
<div style="text-align:center"><font size='2'>*Figure 55. Exporting Events and Audit Events*
</font>

</div>
The user will be able to specify a name for the archive and optionally a time range for the logs to be exported, as shown in Figure 56.
  
![image alt text](/images/PSM/PSM_User_Guide/PSM_Platform_Management/c72f1b7dc735c5201d0645d1bbc2285488ba5cb0.png) 
<div style="text-align:center"><font size='2'>*Figure 56.  Naming the archive containing exported events*
</font>

</div>
The resulting archive will be available for download in the Archive Log Requests view (shown in Figure 57) accessible through the Archive Logs menu.

  
![image alt text](/images/PSM/PSM_User_Guide/PSM_Platform_Management/8e3e1942d5ecd8155bd9841fbb44e1944fd74d9c.png)
<div style="text-align:center"><font size='2'>
</font>

<font size='2'>*Figure 57. Archive Log Requests list*
</font>

</div>
### System Upgrade (Rollout)
System upgrades of both the PSM nodes and DSC firmware are available via the Admin Menu.
The System Upgrade view allows the platform to be upgraded to a new software release. The process is broken into two tasks: 

1. Upgrading the PSM cluster itself takes approximately 10 minutes per cluster node. 
1. Upgrading each DSC in turn takes approximately 3 minutes.   
  
The total DSC upgrade time will depend on the specified “Strategy” and “Max DSCs” as documented below.
First, a software bundle must be uploaded into the PSM repository via the ROLLOUT IMAGES button:
  
![image alt text](/images/PSM/PSM_User_Guide/PSM_Platform_Management/b50d17323d59158b0f4871e39113e9924a59f0a8.png)<div style="text-align:center">
<font size='2'>*Figure 58. Uploading and viewing Rollout Images*
</font>

</div>Then click on Upload Image File, select the image file to be uploaded, and click Upload:
  
![image alt text](/images/PSM/PSM_User_Guide/PSM_Platform_Management/01cfe69ca605a160b2dcc34f87edf9a67470b52c.png)<div style="text-align:center">
<font size='2'>*Figure 59. Choosing an image to upload*
</font>


  
![image alt text](/images/PSM/PSM_User_Guide/PSM_Platform_Management/10a6dc548ba2abd30851f0ff832fa1b5702dca42.png)
<font size='2'>*Figure 60. Newly uploaded image is available*
</font>

</div>Once uploaded, the new bundle will show in the Images Repository (as shown in Figure 61 above), and will now be available to be included in a rollout configuration, created by clicking CREATE ROLLOUT:

  
![image alt text](/images/PSM/PSM_User_Guide/PSM_Platform_Management/9015c7f321939c29f601dd298ed0c041beada5f7.png)<div style="text-align:center">
<font size='2'>*Figure 61. The CREATE ROLLOUT button*
</font>

</div>
This will display the Rollout configuration screen:
  
![image alt text](/images/PSM/PSM_User_Guide/PSM_Platform_Management/c6ca6e68c79132a60a1a8cea912aaddb0e00407a.png)<div style="text-align:center">
<font size='2'>*Figure 62. Rollout configuration screen*
</font>

</div>To create a rollout policy, first select if the update will involve DSC only, PSM Only, or Both DSC and PSM (Default), then fill out the form:

<div class="p-table center"><div></div>

| <div style="text-align:center">**Field** | **Description** |
| --- | --- || </div>Name | The name of the rollout policy |
| Version | The version to be used from the repository |
| Start Time | Either a date and time (local time, not UTC), or select Schedule Now |
| End Time | (Optional) The default is for the PSM to upgrade all nodes, regardless of reachability. A maximum rollout duration can be specified: If reached and all DSCs have not been upgraded, then the PSM will post an error. |
| Strategy | **Linear:** Use the same number of parallel DSC upgrades<br>**Exponential:** Increase the number of parallel DSC as the update progresses successfully |
| Upgrade Type | **Graceful**: Update the DSCs in real time<br>**OnNextHostReboot:** Update will be performed the next time a host reboots |
| Max DSCs to upgrade | Maximum number of concurrent DSC upgrades |
| Max DSC Failures Allowed | Stop upgrade if the number of DSCs failing the upgrade reaches this number.<br>This number does not include DSCs that may have encountered upgrade pre-check failures. PSM can retry upgrading DSCs multiple times within an upgrade time window. (Example: an upgrade is scheduled for 3 hours to upgrade 10 DSCs. If there are DSCs that failed to upgrade at the first attempt, due to host reboots/powered off, cable issues etc, the PSM will retry upgrading those DSCs within that 3 hour window.) |
| Upgrade DSCs by label | The PSM also supports the concept of labels for DSCs, which can be used to specify a group of DSCs to upgrade; for example, by application, location or department. |

</div>
<div style="text-align:center"><font size='2'>*Table 6. Rollout parameters*
</font>

</div>***NOTE:*** *PSM nodes should be upgraded before DSCs.*

Once the form is filled out, select SAVE ROLLOUT; the upgrade will begin at the time chosen in the “Schedule” field.
  
![image alt text](/images/PSM/PSM_User_Guide/PSM_Platform_Management/ff72706123197c795e8d6759ed27303c71951b41.png)
<div style="text-align:center"><font size='2'>*Figure 63. View of pending rollout*
</font>

</div>
The system will first perform a pre-check to make sure all components are ready for update.
  
![image alt text](/images/PSM/PSM_User_Guide/PSM_Platform_Management/2cbbe7a0bc215164ea8ba8105225d26f702205a1.png)
<div style="text-align:center"><font size='2'>*Figure 64. Rollout status screen*
</font>

</div>

The CONTROLLER NODES, CONTROLLER SERVICES, and DSC tabs will show the progress of the upgrade.
Once the pre-check is completed, the system is upgraded.
Depending on the browser being used, a “Refresh” may be required to view the current upgrade status, due to the fact that the GUI itself is upgraded as a part of the PSM upgrade.
### Tech Support
The Tech Support feature collects various logs and troubleshooting information needed by technical support teams in case of an issue. Individual PSM Controller Nodes and DSCs can be selected.  Technical Support will provide information on what components of the system (including selecting specific DSCs) may need to be collected.   
Tech Support Requests can be created in the view shown below.

  
![image alt text](/images/PSM/PSM_User_Guide/PSM_Platform_Management/3b7713e684bfa06290b243575b1d1e956a376616.png)
<div style="text-align:center"><font size='2'>*Figure 65. Tech Support Requests screen*
</font>

</div>
### Configuration Snapshots
The PSM configuration can be saved and later restored via “Snapshots”.  A PSM configuration Snapshot can be created in the view shown in Figure 66.

  
![image alt text](/images/PSM/PSM_User_Guide/PSM_Platform_Management/31f3ca49e64b94ef06242a4eb2dbb51f056d1016.png)
<div style="text-align:center"><font size='2'>*Figure 66. Configuration Snapshots screen*
</font>

</div>To restore the state of the PSM to an earlier configuration, click the “Restore config” icon corresponding to the snapshot, as shown in Figure 67.
  
![image alt text](/images/PSM/PSM_User_Guide/PSM_Platform_Management/dc68c9e24e2cc8a44f7662ea94dbdc015659a134.png)
<div style="text-align:center"><font size='2'>*Figure 67. Accessing the Restore config icon*
</font>

</div>The PSM will be unavailable during the configuration restore process.
Configuration backups are backward compatible: a configuration snapshot taken with an older version of the PSM software can be restored on a later version of the PSM. Features that were not supported when the snapshot was taken will not be configured upon restore. When a configuration is restored, some time might be required to reconcile external entities; for example, if a workload included in the configuration was changed in the vCenter configuration, the PSM must retrieve the relevant information and update the corresponding object.
