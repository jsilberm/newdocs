---
title: Naples REST API Getting Started Guide
linktitle: Naples REST API Getting Started
description: Naples REST API Getting Started
menu:
  docs:
    parent: "Management"
    weight: 1
weight: 1
draft: false
toc: false
---

![Pensando Logo](images/Management/Pensando_Logo.png)


NAPLES REST API Reference Guide
===============================

Version 0.1.0


Legal Stuff
-----------

Document Revision History
-------------------------

Known limitations and features not yet implemented:
===================================================

**Please note:**

*The NAPLES REST API is currently in an early stage of development (ALPHA), features that has not been implemented yet are not covered in this documentation. This document is subject to change.*

-   Not full CRUD support, only POST and GET
-   API Versioning is not implemented in URI
-   Authentication and Session Cookies, currently calls are
    accepted
-   HTTP only, HTTPS is not currently implemented
-   References to a single Object-instance (For example, you can list
    all objects of a certain kind, but you can not reference a specific
    object as an end-point one from the list) is currently not
    implemented
-   Granular error codes are not implemented. Successful response
    returns a 200 and Bad requests and any errors return 500 with a
    meaningful error message set

Pensando REST Overview
======================
The Pensando Representational State Transfer Application Programing Interface (REST API) is a comprehensive interface that allows applications to programmatically interact with NAPLES. 


The API is a RESTful web service that is based on HTTP messages and JavaScript Object Notation(JSON) in the payload. Requests are made to the web service via a Uniform Resource Identifier ,and a response in JSON format is returned based on the request made. The HTTP message specifies the action (I.e. “Create”), the URI refers to an object-instance that is exposed at the API endpoint and the payload contains the attributes that should be applied to the object when created.


NAPLES vs. Venice REST API
==========================

Venice is a Pensando centralized management software that is designed to manage and monitoring of 10'000 of NAPLES.

Venice is a separate software and is not coverd in this document. When Venice is present it is the “single source of truth” and controls all NAPLES functions, the NAPLES REST API (Described in this document) is disabled and cannot be used.

The REST Clients should instead send their REST requests to the
Venice management system. 

![Naples vs Venice](images/Management/Naples_vs_Venice.png)


Please note that the Venice REST API is similar to NAPLES REST API, but they are not identical, please read the
Venice REST API documentation for further details on the Venice REST API.

NAPLES REST Architecture and Overview
=====================================

NAPLES REST API is synchronous in nature, the Observed state (actual state) is returned in the response of the request.

When it comes to the REST API, the main component inside NAPLES is the Agent, it runs on one of the ARM cores inside NAPLES. The Agent provides the REST API web-service for the external management and is the interface that external REST clients communicates with, such as Newman, Postman, Curl etc.

The Agent is written in Go language as a micro-service, the Agent is responsible for serving the REST API (and gRPC to and from Pensando Venice controller) requests to and from external REST clients, maintaining the object model and object relationships as well as communicate and manage the different hardware components via Hardware Abstraction Layer (HAL). The Objects are persistefied in an embedded BoltDB based database.

![Naples vs Venice](images/Management/Naples_Agent_Overview.png)

NAPLES REST API Design and Goals
================================

Our design goals for the API was to create a modern, simple programmatic interface that is capable of evolve over time as needed. Our design is inspired by Kubernetes, it’s modern, scalable, efficient and flexible. Below is a high level overview of the REST API:

-   REST Semantics
-   HTTP
-   Default TCP port: 9007\*
-   HTTP operations POST, GET
-   JSON object structure in payload
-   Multi-tenant enabled
-   Uniformed object definition
-   API is declarative and operations are idempotent

**Please note:**

*The 9007 is the default TCP port for the simulator.*

HTTP Messages and Operations
============================

HyperText Transfer Protocol (HTTP) is the underlying protocol used by the REST API, this protocol defines how messages are formatted, transmitted and received. HTTP is a stateless protocol and each command is executed independently. Each HTTP call includes a Uniformed Resource Identifier (URI) which describes the end-point object.


URI Structure
----------------------

The URI structure describes a hierarchical structure and could contain the following information (depending of the object):

**\<Protocol\>://\<NAPLES IP Address\>:\<Port\>/api/\<Object-Kind\>/**


| Component             | Example        | Description                                                           |
|-----------------------|----------------|-----------------------------------------------------------------------|
| Protocol              | HTTP           | HTTP                                                                  |
| Naples                | mycard         | Domain name or IP address of one of the NAPLES Node                   |
| Port                  | 9007           | NAPLES Agent management port                                          |
| api                   | api            | This is a constant                                                    |
| Object-Kind           | Networks       | The object type string defines the type of object we are referring to |



For example, URI: https://mycard:9007/api/networks/


Supported HTTP Methods (CRUD)
-----------------------------

The Pensando REST API uses the following HTTP methods to perform Create, Read operations:

| HTTP Method           | Operation      | Description                 |
|-----------------------|----------------|-----------------------------|
| POST                  | Create         | Create a new object         |
| GET                   | Read           | Returns one or more objects |



HTTP Response Messages
----------------------

Each call receives a response message that indicates the success of the call, below are the response status-codes that NAPLES will use to indicate the high level result of the operation.


**Please note:**

*The NAPLES API Agent sends back a JSON structured payload in which includes the details of the response. It is a good practice to first check the HTTP response code, and then parse the JSON data to get the details.*

| Status-Code                | Description / Status Key in JSON |
|----------------------------|----------------------------------|
| 200                        | OK\*                             |
| 500                        | Internal Server Error            |
| 404                        | URI not found                    |

\*A successful JSON responses do not contain the return code, see below success vs failure responses.


JSON Request Payload
--------------------

**Please note:**

*POST operations has JSON request payloads, meanwhile GET do not.*


Below is an example of a payload to create an VXLAN tunnel (Tunnel object) called “infra\_vxlan\_tunnel” in the tenant called “default” and in the namespace “infra”, you can think of the namespace as a virtual routing and forwarding (VRF) technology. 


{  
 "kind": "Tunnel",  
 "meta": {. 
  "namespace": "infra",  
  "name": "infra\_vxlan\_tunnel",  
  "tenant": "default". 
 },  
 "spec": {  
  "admin-status": "UP",  
  "destination": "192.168.10.11",  
  "type": "VXLAN",  
  "source": "192.168.10.12". 
 }  
}


In this example, the HTTP method would be a POST operation, and the URI would be: 
http://10.10.10.10:9007/api/tunnels/default/infra

(Example assumes NAPLES has IP address of: 10.10.10.10)


JSON Response payload
---------------------

Below is an example of a successful json response to create the
endpoint “public-router” described above.

**Example of a POST Successful response:**

{  
   "status-code": 200,  
   "error": "",  
   "self-link": "/api/tunnels/default/infra/infra\_vxlan\_tunnel"  
}



**Example of a POST Failure (Error) response:**

{  
   "status-code": 500,  
   "error": "tunnel already exists",  
   "self-link": ""  
}

**Example of a GET Failure (Error) of an non existent object query:**

{  
   "status-code": 500,  
   "error": "endpoint not found",  
   "self-link": ""  
}


Object Structure and Definition
===============================

The NAPLES object model is inspired by K8s where user specifies the intent, operations are idempotent, status describes what is
real.

**Kind:** aka type of the object 

**Meta:** object metadata (common to all objects, all fields are optional) 

**Name:** string name of the object (user provided unique string for this kind of object) 

**Tenant:** tenant name of the object (optional) 

... 

**Spec:** Object Specific Schema 

...

**Status:** Object Specific Status Schema 

... 

![Single Object](images/Management/Single_Object.png)


Object Relationships
--------------------

Objects can express relationships in the model, by Named Reference, below is an example of a named reference.

**Named Reference:**

![Named Reference](images/Management/Named_Reference.png)


Object “public-router” references a Network object by its name “public”


Query and objects, Example
==========================


Authentication and Session Handling
-----------------------------------

To query for all defined namespace objects in the NAPLES:


**GET:** HTTP://10.10.10.10:9007/api/namespaces



**Header:**

Content-Type: application/json

Successful response:
--------------------

**HTTP Response code:** 200 OK

**Headers** (Nothing of relevance for the REST API)

**Body:**
[  
    {  
        "kind": "Namespace",  
        "meta": {  
            "name": "infra",  
            "tenant": "default",  
            "creation-time": "2018-06-25T20:15:59.27625614Z",  
            "mod-time": "2018-06-25T20:15:59.27625614Z". 
        },  
        "spec": {. 
            "namespace-type": "INFRA"  
        },  
        "status": {  
            "namespace-id": 3. 
        }  
    },  
    {  
        "kind": "Namespace",  
        "meta": {  
            "name": "kg1",  
            "tenant": "default",  
            "creation-time": "2018-06-25T20:18:55.282017114Z",  
            "mod-time": "2018-06-25T20:18:55.282017114Z"  
        },  
        "spec": {},  
        "status": {  
            "namespace-id": 4  
        }  
    },  
    {  
        "kind": "Namespace",  
        "meta": {  
            "name": "public",  
            "tenant": "default",  
            "creation-time": "2018-06-25T20:18:55.422266812Z",  
            "mod-time": "2018-06-25T20:18:55.422266812Z"  
        },  
        "spec": {},  
        "status": {  
            "namespace-id": 5  
        }  
    },  
    {  
        "kind": "Namespace",  
        "meta": {  
            "name": "default",  
            "tenant": "default",  
            "creation-time": "2018-06-25T20:15:59.191280753Z",  
            "mod-time": "2018-06-25T20:15:59.191280753Z"  
        },  
        "spec": {},  
        "status": {  
            "namespace-id": 2  
        }  
    }  
]  

In this example, NAPLES returned four Namespace objects, “infra”, “kg1”, “public” and “default” in the body.


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

\$ curl -X POST -H "Content-Type: application/json" -d '{"kind":"Namespace","meta":{"name":"**myName**","tenant":"**default**"}}' http://**10.10.10.10**:9007{.c9}/api/namespaces/

Above example creates a Namespace object with the name “myName” 

List all defined Namespace objects example (GET):

(Don’t forget to change the IP Address)

\$ curl -H "Content-Type: application/json" http://**10.10.10.10**:9007/api/namespaces/

To get more information about curl, please use the manpages:

\$ man curl{}


Using the Postman/Newman tool:
------------------------------

Please note the Newman is a command line Collection Runner for Postman, the two tools are in feature parity. An easy way to think of it is that Postman application is the GUI version, and Newman is the CLI version.

The tools have many features, one of them allows you to define a collection of multiple REST calls in a single json file and then execute these against a REST service (The Agent running inside NAPLES in our case) 

**Newman CLI example:**

\$ newman run mycollection.json


**Postman GUI, View:**

![Postman GUI](images/Management/Postman_GUI.png)


To get more details and information about the postman/Newman, please read the official documentation:
[https://www.getpostman.com/docs/v6/](https://www.getpostman.com/docs/v6/)


Troubleshooting
===============

API/Object Model documentation
==============================

