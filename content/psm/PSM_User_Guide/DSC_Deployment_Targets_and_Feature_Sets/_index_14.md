---
title: "DSC Deployment Targets and Feature Sets"
menu:
  docs:
    parent: "PSM Enterprise Edition User Guide"
weight: 15
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
## DSC Deployment Targets and Feature Sets
The PSM allows users to turn DSC features on incrementally.  This is controlled by two parameters associated with each DSC: its *Deployment Target*, and its *Feature Set*.  The combination of these two parameters is assigned to DSCs via *DSC Profiles*.
### Deployment Targets
The Deployment Target defines the kind of traffic the DSC will be processing: communication between VMs even if running on the same host (*Virtualized*), or only traffic between different hosts (*Host*).
The services implemented by a DSC configured with the Host Deployment Target are applied to the traffic entering and exiting the host, from the standpoint of physical hosts and interfaces.
The services implemented by a DSC configured with the Virtualized Deployment Target are applied to the traffic generated and received by each individual VM on the host.  The DSC provides flow-aware telemetry based on fine-grained individual flows, as well as fine-grained micro-segmentation security between VMs on the host.
### Feature Sets
A DSC’s Feature Set determines which features are enabled on the DSCs.  In this release, there are three available Feature Sets; the features associated with them are shown in Table 4.
<div class="p-table center"><div></div>

| <div style="text-align:center"><font size='2'>**Feature**<br></font> | <font size='2'>**SmartNIC**<br></font> | <font size='2'>**Flow Aware**<br></font> | <font size='2'>**Flow AwareWith Firewall**<br></font> |
| --- | --- | --- | --- || </div><font size='2'>Interface-based ERSPAN<br></font> | <div style="text-align:center"><font size='2'>  ✅<br></font> | <font size='2'> ✅<br></font> | <font size='2'> ✅<br></font> |
| </div><font size='2'>Flow-based ERSPAN<br></font> | <div style="text-align:center"><font size='2'><br></font> | <font size='2'> ✅<br></font> | <font size='2'> ✅<br></font> |
| </div><font size='2'>NetFlow/IPFIX<br></font> | <div style="text-align:center"><font size='2'><br></font> | <font size='2'> ✅<br></font> | <font size='2'> ✅<br></font> |
| </div><font size='2'>Security Policy Enforcement<br></font> | <div style="text-align:center"><font size='2'><br></font> |  | <font size='2'> ✅<br></font> |
| </div><font size='2'>Micro-segmentation<br></font> | <div style="text-align:center"><font size='2'><br></font> |  | <font size='2'> ✅<br></font> |

</div>
<font size='2'>*Table 4.  Features available with each Feature Set*
</font>

</div>
#### SmartNIC
The SmartNIC Feature Set, available in this release with the Host Deployment Target, provides standard, basic network services with the highest performance characteristics. It includes telemetry and visibility functions, including bi-directional traffic mirroring with ERSPAN and a rich set of metrics.
Although other Feature Sets include a wider range of services, the SmartNIC Feature Set does not have any limits in terms of connections per second that can be established through the card. This feature set is recommended when other services are not needed and traffic is expected to have a large number of new flows per second, such as in HPC (high performance computing) clusters or when conducting host performance testing.
#### Flow Aware
The Flow Aware Feature Set, available in this release with the Host Deployment Target, provides network flow-based telemetry, such as bi-directional flow mirroring (ERSPAN), flow statistics, and NetFlow/IPFIX. These features are key in gaining visibility of the network and learning communication patterns within the enterprise data center, which can then be used as a basis to create appropriate firewall policies.
#### Flow Aware with Firewall
The Flow Aware with Firewall Feature Set, available in this release with the Virtualized Deployment Target, includes, in addition to all the features listed <ins>above</ins> for the Flow Aware Feature Set, the capability of enforcing security policies, where a security policy can specify which flows’ packets should be forwarded or dropped by DSCs. This Feature Set selected with the Virtualized Deployment Target operates on traffic among single workloads (e.g, VMs) even if they execute on the same host, allowing it to be used to provide visibility and enforcement at VM-level granularity. A typical use case is an East-West stateful firewall, providing micro-segmentation within a data center.  If it’s desired to monitor all flows between VMs, administrators can create an “any-to-any” firewall policy, allowing all traffic to pass, while learning all flows for app dependency mapping.
### DSC Profiles
For ease of administration, the PSM uses *DSC Profiles* to assign a Deployment Target and Feature Set to each DSC. Users can create a DSC Profile for each use scenario in their enterprise; they can then assign each DSC one of the defined Profiles.  Each DSC is assigned exactly one DSC Profile at any time.
The combination of the Deployment Target and Feature Set selected in a DSC Profile controls the capabilities of all the cards that are assigned that DSC Profile.
By grouping DSCs by DSC Profiles, it is easy to change the behavior of a set of DSCs by changing their DSC Profile. Alternatively, the behavior of a DSC can be changed by reassigning it a different DSC Profile.
In either case, the affected DSCs will automatically inherit support of the set of features associated with their changed or newly-assigned DSC profile.
### Creating a DSC Profile
Figure 28 illustrates the decision path for an administrator creating a DSC Profile for a particular type of DSC use case.
  
![image alt text](/images/PSM/PSM_User_Guide/DSC_Deployment_Targets_and_Feature_Sets/d80d9092463630b4e69e20c6bb8f97b043b5ba8e.png)<div style="text-align:center"><font size='1'>
</font>

<font size='2'>*Figure 28. Choosing a DSC Deployment Target and Feature Set*
</font>


</div>The first consideration is whether for this use case the host is using VMware ESXi for virtualization. If not (either because it’s running a non-virtualized OS, or is running a non-VMware hypervisor), choose the Host Deployment Target.
If the host is running ESXi, the administrator must decide whether the use case involves intra-host traffic processing or applying security policies.  If either of these are true, the DSCs in this case will need to be aware of traffic between VMs on their host; choose the Virtualized Deployment Target. If neither is true, choose the Host Deployment Target.
If the Host Deployment Target has been chosen, the next decision is whether flow-level visibility is required. If not, select the SmartNIC Feature Set; otherwise, select the Flow Aware Feature Set.
If the Virtualized Deployment Target has been chosen, use the Flow Aware With Firewall Feature Set.
Figure 29 shows an example of the overview provided by the PSM GUI of currently-configured DSC profiles. To define a new profile, click the “Add DSC Profile” button.
  
![image alt text](/images/PSM/PSM_User_Guide/DSC_Deployment_Targets_and_Feature_Sets/8e9249dcda0471f2a448984385864f856392810e.png)
<div style="text-align:center"><font size='2'>*Figure 29. DSC Profiles Overview*
</font>

</div>

Figure 30 shows the first steps in creating a new DSC profile; assigning it a unique name, and selecting the chosen Deployment Target.
If the Host Deployment Target is selected, two Feature Sets are available to select: SmartNIC or Flow Aware.
  
![image alt text](/images/PSM/PSM_User_Guide/DSC_Deployment_Targets_and_Feature_Sets/01830cab7dccd912f978e89d5e54a12ff4b207b7.png)<div style="text-align:center">
<font size='2'>*Figure 30. Deployment Target selection*
</font>

</div>

If the Virtualized Deployment Target is selected, as shown in Figure 31, only the Flow Aware with Firewall Feature Set is available to select.
  
![image alt text](/images/PSM/PSM_User_Guide/DSC_Deployment_Targets_and_Feature_Sets/cbbf1e943a0d74cba4e0f12135f19fe040b2ecda.png)<div style="text-align:center">
<font size='2'>*Figure 31. Feature Set selection for Virtualized Deployment Target*
</font>

</div>***Reminder****: As mentioned above, a DSC installed on an ESXi host is not required to be configured with a Virtualized Deployment Target. If visibility of traffic among VMs running within the host is not required, the Host Deployment Target can be used, which gives access to its corresponding Feature Sets.*
### Assigning a DSC Profile to a DSC
The PSM has a pre-defined DSC Profile, named “default”, that at the time the PSM is installed is associated with the Host Deployment Target and the SmartNIC Feature Set. When a DSC is first admitted to a PSM, it is assigned the “default” profile; this means that by default all DSCs initially activate the SmartNIC feature set **with no administrator action required**.
If the preferred behavior is for DSCs to activate a different feature set when first admitted to the PSM, change the “default” profile (as described <ins>below</ins>) so it is associated with the desired feature set.
To change what profile a DSC is assigned, go to the Distributed Service Cards Overview, select the card or cards to be assigned a new profile, and click the “Assign DSC Profile” button (  
![image alt text](/images/PSM/PSM_User_Guide/DSC_Deployment_Targets_and_Feature_Sets/c587163d4300822f6bd1792a0d915c5e714e2512.png)) that appears above the DSC list. Pick the new profile to assign, and click “Save”.
### Changing a DSC Profile
To change the definition of an existing DSC Profile, go to the DSC Profiles Overview, hover over the profile, and click the Edit button that appears on the right side of the screen.  Make the desired changes, and click “Save”.
