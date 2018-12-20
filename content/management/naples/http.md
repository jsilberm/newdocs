---
title: Naples HTTP
linktitle: Naples HTTP
description: Naples HTTP
menu:
  docs:
    parent: "naples"
    weight: 2
weight: 2
draft: false
toc: true
---

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
| PUT                   | Update         | Modify an existing object   |
| GET                   | Read           | Returns one or more objects |
| DELETE                | Delete.        | Delete one or more objects  |


HTTP Response Messages
----------------------

Each call receives a response message that indicates the success of the call, below are the response status-codes that NAPLES will use to indicate the high level result of the operation.


**Please note:**

*The NAPLES API Agent sends back a JSON structured payload in which includes the details of the response. It is a good practice to first check the HTTP response code, and then parse the JSON data to get the details.*

| Status-Code                | Description / Status Key in JSON |
|----------------------------|----------------------------------|
| 200                        | OK\*                             |
| 500                        | Error.                           |
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


In this example, the HTTP method would be a POST operation, and the URI would be: http://10.10.10.10:9007/api/tunnels/default/infra  
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

