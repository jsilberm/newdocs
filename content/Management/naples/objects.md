---
title: Naples Objects
linktitle: Naples Objects
description: Naples Objects
menu:
  docs:
    parent: "naples"
    weight: 3
weight: 3
draft: false
toc: true
---


![Postman GUI](/images/Management/Naples/Naples_ObjectModel.png)


Object Structure and Definition
===============================

The NAPLES object model is an user specified intent, operations are idempotent, status describes what is
real.

	kind:          Aka type of the object 
	meta:          Object metadata (common to all objects, all fields are optional) 
		name:      String name of the object (user provided unique string for this kind of object) 
		tenant:    Tenant name of the object (optional) 
		namespace: Namespance within a Tennant, works like a virtual routing and forwarding (VRF) technology
	... 
	Spec:          Object Specific Schema 
	...
	Status:        Object Specific Status Schema 
	... 

For Example:

	kind: Network
	meta:
		name: corp-network-208
		tenant: default
		namespace: copr-network-208
	Spec:
		ipv4-subnet: 10.1.1.208/24
		ipv4-gateway: 10.1.1.1
		vlan-id: 208


Object Relationships
--------------------

Objects can express relationships in the model, by Named Reference, below is an example of a named reference.

**Named Reference:**


![Named Reference](/images/Management/Naples/Named_Reference.png )

Object “public-router” references a Network object by its name “public”
