---
title: Security Groups
linktitle: Security Groups
menu:
  docs:
    parent: "naples"
    weight: 5
weight: 5
draft: false
toc: true
---

In this example there will be 2 servers (Server1 IP: 11.0.0.10, and Server2 IP: 11.0.0.20) connected to the VLAN (200).
The example assumes **'memtun'** is running, and **'tun0'** is present and available on **'1.0.0.1'** and that Naples management interface has been configured on **'1.0.0.2'**, on both Server1 and Server2.

![Postman GUI](/images/Management/Naples/2Servers_Microsegmentation.png)

Example Scenario:
-----------------

We want to open a one way TCP port(22) from server1 to Server2, to do this we need to have do some  configuration on each server:

**Server1 and Server2:**  
- Define an L2 Segment, VLAN 200)  
- Define an interface endpoint for server1  
- Define an interface endpoint for server2  
- Define a Security Group Policy (SGPolicy) to allow all outgoing traffic to any server*

**\*Please note:**  
_In this exampe we will configure the Naples on the servers to allow all outgoing traffic to any server, but for more secure environmnets you should create polices to specifically specify which port's and to which server's, and traffic direction allowed._


**Server2:**  
- Define a Security Group Policy (to allow incoming TCP connects on port 22)  

Creating the VLAN 200 L2 Segment:
---------------------------------
To create the network we will send the **'Network'** policy to Naples:

	kind: Network
	meta:
		name: corp-network-200
		tenant: default
		namespace: lab
	Spec:
		vlan-id: 200

**Run the following command on both Server1 and Server2:**

\# curl -d '\{ "kind": "Network", "meta": \{ "name": "corp-network-200", "tenant": "default", "namespace": "lab"\}, "spec": \{ "vlan\-id": 200 }}' \-X POST \-H "Content-Type:application/json" http://1.0.0.2:9007/api/networks/

Define an interface endpoint for Server1:
-----------------------------------------

To create server1 endpoint, we need to create the **'Endpoint'** policy: 

	kind: Endpoint
	meta:
		name: srv1-interface1
		tenant: default
		namespace: lab
	Spec:
		network-name: corp-network-200
		ipv-address: 11.0.0.10/24
		mac-address: 00:ae:cd:00:10
		useg-vlan: 1000

**Run the following command on both Server1 and Server2:**

\# curl -d '{ "kind": "Endpoint", "meta": { "name": "srv1-interface1", "tenant": "default", "namespace": "lab"}, "spec": { "network-name": "corp-network-200", "ipv4-address": "11.0.0.10/32", "mac-address": "00:ae:cd:00:10", "useg-vlan": 1000}}' -X POST -H "Content-Type:application/json" http://1.0.0.2:9007/api/endpoints/

Define an interface endpoint for Server2:
-----------------------------------------

To create server2 endpoint, we need to create the **'Endpoint'** policy: 

	kind: Endpoint
	meta:
		name: srv2-interface1
		tenant: default
		namespace: lab
	Spec:
		network-name: corp-network-200
		ipv-address: 11.0.0.20/24
		mac-address: 00:ae:cd:00:20
		useg-vlan: 1001

**Run the following command on both Server1 and Server2:**

\# curl -d '{ "kind": "Endpoint", "meta": { "name": "srv2-interface1", "tenant": "default", "namespace": "lab"}, "spec": { "network-name": "corp-network-200", "ipv4-address": "11.0.0.20/32", "mac-address": "00:ae:cd:00:20", "useg-vlan": 1001}}' -X POST -H "Content-Type:application/json" http://1.0.0.2:9007/api/endpoints/

Define a SGPolicy on Server1 and Server2 to allow all outgoing traffic:
---------------------------------------------------------------------------
# NEED HELP WITH THIS!!!
# NEED HELP WITH THIS!!!
# NEED HELP WITH THIS!!!

To allow all out going traffic, we need to create an **'SGPolicy'** policy:

	kind: SGPolicy
	meta:
		name: allow-tcp-22
		tenant: default
		namespace: lab
	Spec:
		network-name: corp-network-200


**Run the following command on Server2:**

curl -d '{"kind": "SGPolicy", "meta": {"name": "allow-tcp-22", "tenant": "default", "namespace": "lab"}, "spec": {"attach-tenant": true, "policy-rules": [{"action": "PERMIT", "destination": {"addresses": ["11.0.0.10"], "app-configs": [{"protocol": "tcp", "port": "22"}]}}]}}' -X POST -H "Content-Type:application/json" http://1.0.0.2:9007/api/security/policies/

Define a Security Group Policy on Server2:
------------------------------------------

To open the TCP port, we need to create the **'SGPolicy'** policy:

	kind: SGPolicy
	meta:
		name: allow-tcp-22
		tenant: default
		namespace: lab
	Spec:
		network-name: corp-network-200


**Run the following command on Server2:**

curl -d '{"kind": "SGPolicy", "meta": {"name": "allow-tcp-22", "tenant": "default", "namespace": "lab"}, "spec": {"attach-tenant": true, "policy-rules": [{"action": "PERMIT", "destination": {"addresses": ["11.0.0.10"], "app-configs": [{"protocol": "tcp", "port": "22"}]}}]}}' -X POST -H "Content-Type:application/json" http://1.0.0.2:9007/api/security/policies/

The configuration is now complete, and Server1 can now access Server2 via TCP on port 22


Misc
====

H/W inventory
-------------

Faults, states and Status
-------------------------

Image Update/Downgrade


A simple ways to test NAPLES REST API
=====================================

**Please note:**

*There are many different tools available on the market, Pensando are not promoting any specific tools over others, the tools mention below are just a few examples available for REST API testing etc.*

**Using the cURL tool:**

You can use the curl tool to send and receive REST calls from the CLI of a client:
(You may have to manually install the curl tool onto your client)

**Create a Namespace object example (POST):**

(Don’t forget to change the IP Address, in the “default” tenant)

**$ curl -X POST -H "Content-Type: application/json" -d '{"kind":"Namespace","meta":{"name":"**myName**","tenant":"**default**"}}' http://**10.10.10.10**:9007{.c9}/api/namespaces/**

Above example creates a Namespace object with the name “myName” 

List all defined Namespace objects example (GET):

(Don’t forget to change the IP Address)

**$ curl -H "Content-Type: application/json" http://**10.10.10.10**:9007/api/namespaces/**

To get more information about curl, please use the manpages:

**$ man curl**


Using the Postman/Newman tool:
------------------------------

Please note the Newman is a command line Collection Runner for Postman, the two tools are in feature parity. An easy way to think of it is that Postman application is the GUI version, and Newman is the CLI version.

The tools have many features, one of them allows you to define a collection of multiple REST calls in a single json file and then execute these against a REST service (The Agent running inside NAPLES in our case) 

**Newman CLI example:**

**$ newman run mycollection.json**


Postman GUI, View:

![Postman GUI](/images/Management/Naples/Postman_GUI.png)


To get more details and information about the postman/Newman, please read the official documentation:
[https://www.getpostman.com/docs/v6/](https://www.getpostman.com/docs/v6/)


Troubleshooting
===============

