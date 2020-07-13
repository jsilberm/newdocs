---
title: "Appendix B: PSM Operational Network Ports"
menu:
  docs:
    parent: "PSM Enterprise Edition User Guide"
weight: 21
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
## Appendix B: PSM Operational Network Ports
These ports must be opened in each direction in order for the PSM cluster to function correctly.
<div class="p-table center"><div></div>

| <div style="text-align:center">**TCP Port** | **Service** |
| --- | --- || </div>**From user station to PSM node** |  |
| <font size='2'>22<br></font> | <font size='2'>sshd (for node management)<br></font> |
| <font size='2'>80<br></font> | <font size='2'>redirects to 443<br></font> |
| <font size='2'>443<br></font> | <font size='2'>ApiGw HTTPS<br></font> |
| <font size='2'>9001<br></font> | <font size='2'>Initial POST for cluster bootstrap<br></font> |
| **From PSM node to PSM node** |  |
| <font size='2'>5001<br></font> | <font size='2'>etcd (peer)<br></font> |
| <font size='2'>5002<br></font> | <font size='2'>etcd (client)<br></font> |
| <font size='2'>6443<br></font> | <font size='2'>Kubernetes APIServer<br></font> |
| <font size='2'>7000<br></font> | <font size='2'>Citadel<br></font> |
| <font size='2'>7087<br></font> | <font size='2'>Citadel Query<br></font> |
| <font size='2'>9002<br></font> | <font size='2'>Cluster management<br></font> |
| <font size='2'>9003<br></font> | <font size='2'>ApiServer<br></font> |
| <font size='2'>9004<br></font> | <font size='2'>Orchestrator Hub<br></font> |
| <font size='2'>9009<br></font> | <font size='2'>Resolver<br></font> |

</div>
<div style="text-align:center"><font size='2'>*Table 7.  Required port availability (part 1/3)*
</font>

</div>


<div class="p-table center"><div></div>

| <div style="text-align:center">**TCP Port** | **Service** |
| --- | --- || </div>**From PSM node to PSM node (cont’d)** |  |
| <font size='2'>9010<br></font> | <font size='2'>EventsManager<br></font> |
| <font size='2'>9011<br></font> | <font size='2'>Spyglass<br></font> |
| <font size='2'>9012<br></font> | <font size='2'>EventsProxy<br></font> |
| <font size='2'>9014<br></font> | <font size='2'>CMD Leader Services<br></font> |
| <font size='2'>9015<br></font> | <font size='2'>Rollout<br></font> |
| <font size='2'>9020<br></font> | <font size='2'>TPM<br></font> |
| <font size='2'>9030<br></font> | <font size='2'>TSM<br></font> |
| <font size='2'>9051<br></font> | <font size='2'>VOS<br></font> |
| <font size='2'>9200<br></font> | <font size='2'>Elastic (client)<br></font> |
| <font size='2'>9300<br></font> | <font size='2'>Elastic (peer)<br></font> |
| <font size='2'>10250<br></font> | <font size='2'>Kubelet<br></font> |
| <font size='2'>10257<br></font> | <font size='2'>Kubernetes Controller Manager<br></font> |
| <font size='2'>10259<br></font> | <font size='2'>Kubernete Scheduler<br></font> |
| <font size='2'>10777<br></font> | <font size='2'>Citadel Collector<br></font> |
| <font size='2'>19001<br></font> | <font size='2'>Minio<br></font> |
| **From PSM to DSC and from management station to PSM** |  |
| <font size='2'>8888<br></font> | <font size='2'>agent reverse proxy for<br></font> <br>`penctl`<font size='2'> and diagnostics<br></font> |

</div>
<div style="text-align:center"><font size='2'>*Table 7.  Required port availability (part 2/3)*
</font>

</div>

<div class="p-table center"><div></div>

| <div style="text-align:center">**TCP Port** | **Service** |
| --- | --- || </div>**From DSC to PSM** |  |
| <font size='2'>9005<br></font> | <font size='2'>NPM<br></font> |
| <font size='2'>9009<br></font> | <font size='2'>Resolver<br></font> |
| <font size='2'>9010<br></font> | <font size='2'>EventsManager<br></font> |
| <font size='2'>9012<br></font> | <font size='2'>EventsProxy<br></font> |
| <font size='2'>9014<br></font> | <font size='2'>CMD Health Updates<br></font> |
| <font size='2'>9015<br></font> | <font size='2'>Rollout<br></font> |
| <font size='2'>9019<br></font> | <font size='2'>NIC Registration<br></font> |
| <font size='2'>9020<br></font> | <font size='2'>TPM<br></font> |
| <font size='2'>9030<br></font> | <font size='2'>TSM<br></font> |
| <font size='2'>9051<br></font> | <font size='2'>VOS<br></font> |
| <font size='2'>10777<br></font> | <font size='2'>Citadel Collector<br></font> |

</div>
<div style="text-align:center"><font size='2'>*Table*
</font> 
<font size='2'>*7*
</font>
<font size='2'>*. Required port*
</font>
 <font size='2'>*availability (part 3/3)*
</font>

</div>
