---
title: "Installing the PSM"
menu:
  docs:
    parent: "PSM Enterprise Edition User Guide"
weight: 10
categories: [psm]
toc: true
---
## Installing the PSM
***Note****:  Before installation, refer to the Release Notes for the minimum resource requirements needed to operate the PSM.*
### Install and Configure the PSM (ESXi Cluster)
The PSM installs as a virtual appliance (OVA or QCOW2 format file), deployed through VMware Virtual Center (vCenter). The PSM deployment depends on vApp and requires vCenter for installation.
***Note:*** *While it is recommended that vCenter or OVFtool* *be* *used to deploy the PSM OVA, more* *experienced* *users can use native ESXi tools.*
See the *PSM for Enterprise Edition Design Best Practices* document for details on hardware and software requirements for PSM installation. Please plan for 60 minutes as an upper-bound limit to install a 3-node PSM cluster.
A PSM instance is deployed as a high-availability quorum-based cluster. To ensure the highest availability, the PSM should be installed on three VMs[^kix.d4eualpq40uf], each on a separate host that is part of a VMware HA cluster[^kix.wtyixwbt1ao].   

- Log in to vCenter. Locate the ESXi host you want to install a PSM node on and select “Deploy OVF Template” from the Action button.   
- Specify the URI or Local File name of the PSM OVA file `psm.ova`.
- Specify the PSM VM name.
- Under the storage section, select Thick Provision. 
- Specify the OVA properties: hostname, IP address, etc.
       - If using DHCP, leave the IPaddress blank, and configure a static MAC address-to-IP binding (reservation) for this host in the DHCP server. 
       - Note that changing PSM cluster node IP addresses after bootstrapping is not supported. 
       - It is strongly suggested that static IP is used. 
       - Under Password, specify the SSH/console password.
- Review details. Click “Next” to accept the warnings about advanced configuration and lack of Publisher certificate[^kix.fqfckeknj8li]. 

- Start the VM in vCenter once the OVA deployment status shows “Completed”. The boot process will untar and install the PSM distribution from a read-only partition.
- When the VM comes up, validate that the hostname has changed to what was specified in the OVA properties above and is not “localhost”. If “localhost” appears, then contact Technical Support, as this indicates that the initialization did not complete successfully.
- Login to the PSM as user `root`, with the password specified in the OVA properties above (if one was not defined in the OVA properties, the default password is `centos`). If a non-default root password is configured, it may take 1-2 mins for the password to take effect after the login prompt becomes available. If this is a concern, make sure network access to the VM is disabled until the password has been reset.
- Initialize the cluster, as described in the section <ins>Bootstrap the PSM Cluster</ins>.
  
NOTE: Deploying a 3-node cluster involves importing the `psm.ova` file once for each VM instance. The number of imports can be reduced by cloning the first VM as a template, and then deploying subsequent VMs from the template. If taking this approach, follow these steps:

- Create the first VM from the `psm.ova` file
- In vCenter, choose “Clone as Template to Library” to save the VM as a Template (.vmtx) file.  Be sure to give the VM a unique name.
- Select the new VM in vCenter. Select the “Configure” Menu item. Expand “Settings” and select “vApp Options”. Scroll down to “Properties”. Click the radio button for “hostname” and the “Set Value” action to change the hostname to a unique value (typically corresponding to the VM unique name).
- If applicable, apply any network-specific settings that may have been used in deploying the original VM from the `psm.ova` file. 
- Start the new VM and verify that the VM name and network setting are as intended before bootstrapping the cluster as described in the below section <ins>Bootstrap The PSM Cluster</ins>.
  
### Install and Configure the PSM (KVM Cluster)
The PSM is supported on KVM as well as ESXi; this section provides a short summary of the steps required to set up a KVM-based PSM appliance.  For a detailed guide, see <ins>Appendix H</ins>.

- Create three KVM hosts. Server requirements are specified in the document *Enterprise PSM Design Best Practices*. (Pensando recommends that the three PSM cluster nodes should be distributed across multiple servers). 
- Configure the needed network bridges for access to the CentOS server and for the PSM.
- Make sure the VLAN module is loaded for each server.
- Create a bridge interface named `br0` that links interface `eno5`, which is an active interface on the server.
- Restart the network and verify that the CentOS system `server1` is accessible.
- Verify the network interfaces.
- Create the interfaces that will be used for the PSM.
- Create the interface that is linked to the physical interface.
- Restart the network service.
- Repeat the above steps to deploy the second server (`server2`) in the environment (a third one you might have in the setup).
- Install the PSM software:
       - Deploy each PSM node using the `psm.qcow2` image
       - Set networking for the nodes
- Bootstrap the cluster, as described in the next section.
  
### Bootstrap the PSM Cluster
Before the PSM cluster can be administered, it must be initialized via the `bootstrap_PSM.py` utility.  Below are some usage examples. The command `bootstrap_PSM.py -h` will show all parameters that can be specified.
Determine the IP address assigned to each PSM VM that has been deployed. In ESXi deployments this can be obtained from vCenter, or from within a CentOS VM with `ip addr`. This address is required when launching the `bootstrap_PSM.py` utility and is provided through the `-v` option.
***NOTE:*** *a PSM VM should have a single L3 interface that it uses to communicate to other PSM VMs as well as its DSCs. The IP address of this interface should be used in bootstrapping the cluster. The default IP route should point to this interface.*

**Example:** If the PSM is being installed on a single VM (for testing only):


```
# bootstrap_PSM.py -v 192.168.68.49

2019-09-26 11:48:05.405149: * start PSM bootstrapping process
2019-09-26 11:48:05.405195: * - list of PSM ips: ['192.168.68.49']
2019-09-26 11:48:05.405214: * - list of ntp servers: ['0.us.pool.ntp.org', '1.us.pool.ntp.org']
2019-09-26 11:48:05.405228: * - using domain name: pensando.io
2019-09-26 11:48:05.405240: * - auto-admit dsc: True
2019-09-26 11:48:05.405252: * checking for reachability
2019-09-26 11:48:09.415351: * connectivity check to 192.168.68.49 passed
2019-09-26 11:48:09.415436: * creating PSM cluster
2019-09-26 11:48:09.416110: * sending: POST http://localhost:9001/api/v1/cluster
2019-09-26 11:48:09.416144: {"api-version": "v1", "kind": "Cluster", "meta

--snip--
  
  

```

**Example:** To bootstrap a 3-node PSM cluster for production, specify all three IP addresses. Before executing this command, make sure that all three PSM VMs are already running. The PSM VMs can be deployed using the same OVA, but must have unique IP addresses. The bootstrap script only needs to be executed on one of the nodes.


```
# bootstrap_PSM.py -v 192.168.68.49 192.168.68.50 192.168.68.51
  
  

```

If everything completes successfully, the message below can be seen in the log:


```
--snip--

2019-09-26 18:52:13.693626: * PSM cluster created successfully


2019-09-26 18:52:13.693656: * you may access PSM at https://192.168.68.49
  
  

```

The PSM browser GUI and REST API should now be available at any of the PSM addresses. Note that there is no virtual IP address for the 3 node cluster. A load balancer should be installed in front of the cluster to enable such functionality.
If a password is not specified when bootstrapping the PSM cluster, the default is `Pensando0$`.   
The `bootstrap_PSM.py` utility can be used to provide configuration information to the PSM. The following example provides a cluster name, a domain name, and the address of an NTP server, and activates automatic DSC admission:


```
# bootstrap_PSM.py -clustername Pod02 -domain training.local -ntpservers 10.29.5.5 -autoadmit True 10.29.12.11 10.29.12.12 10.29.12.13
  
  

```

To change the PSM cluster root password once the cluster is operational, see <ins>Appendix C</ins>.
### Save the DSC Security Token
The PSM uses an authorization credential known as the *DSC Security Token* to validate all requests it makes to each DSC; a DSC under PSM control cannot be accessed without this credential.
It is strongly recommended to save a copy of this credential immediately after creating a cluster, and store it in a safe place outside of the PSM, in case it is necessary to access DSCs during a PSM cluster outage or loss of connectivity between DSCs and the PSM. For further information on how to use this token during an outage, refer to the “Penctl CLI utility” section of the *Pensando Distributed Services Card User Guide*.
Use the following two commands to download a security token using the PSM API. In each example, `$PSMaddr` is assumed to be set to the PSM cluster address.

1. Create a session cookie; this is the login authorization necessary to make API calls to the PSM.
  
The following login command uses a POST request to create a session cookie and store it in a local file named `PSM-cookie-jar.txt`.  (This command normally returns a JSON payload; this is suppressed in this example by “`grep HTTPSTATUS`”, which can be removed for a more verbose response.)


```
$ curl -sS -k -j -c ./PSM-cookie-jar.txt -X POST -H 'Content-Type: application/json' --write-out "HTTPSTATUS: %{http_code}" -d  '{"username":"admin","password":"Pensando0$","tenant": "default"}' https://$PSMaddr/v1/login | grep HTTPSTATUS
HTTPSTATUS: 200
  
  

```

1.  Request the token, and save it in a file called `my_cert.crt`:
  


```
$ curl -b ./PSM-cookie-jar.txt -s -k "https://$PSMaddr/tokenauth/v1/node?Audience=*" | cut -d "\"" -f 4 | awk '{gsub(/\\n/,"\n")}1' > my_cert.crt
  
  

```
