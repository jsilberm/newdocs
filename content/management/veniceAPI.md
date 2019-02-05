---
title: Venice REST API Getting Started Guide
description: Venice REST API Getting Started Guide
menu:
  docs:
    parent: "management"
    weight: 2
quicklinks:
weight: 2
draft: false
toc: true
---
![image alt text](/images/venice/image_0.png)



# Venice REST API Getting Started Guide

Version 0.1



# Table Of Contents

[[TOC]]

# Document Revision History

# Document Overview

This document covers the Pensando Venice REST API.  It is intended as a quick start guide, and assumes basic knowledge of REST based API's.The Pensando Representational State Transfer Application Programing Interface (REST API) is a comprehensive interface that allows an application to programmatically interact with Venice. Venice CLI and GUI utilize the very same REST API to interact with Venice API Cluster, which means that all features that are available in the GUI and the CLI are also available via the REST API.

The API is a RESTful web service that is based on HTTP messages and JavaScript Object Notation (JSON) in the payload. Requests are made to a resource’s Uniform Resource Identifier (URI), and a response in JSON format is returned based on the request made. The HTTP message specifies the action (i.e. "Create").  The URI refers to an object-instance that is exposed at the API endpoint.  The payload contains the attributes that should be applied to the object when created.

# Venice Overview

Pensando’s Venice platform provides a programmable, secure microservice based infrastructure to manage and protect services, such as Compute, Storage, Network and Security services.  The Venice platform consists of 3 or 5 quorum controller nodes (additional non-quorum nodes can be added for scalability) that can provide consistent services to thousands of physical devices utilizing Pensando’s infrastructure called Naples. Below is an architectural diagram of the Venice platform.

![image alt text](/images/venice/image_1.png)

 **Microservices architecture** 

* Scales out linearly  
* Initial target 1000 Naples, built for 10,000+  
* Intent-based object model with multi-tenancy  
* Federation for multiple Venice clusters (Phase 2)  


 **Leverages mature Open Source** 

* Kubernetes, etcd, gRPC, Elastic, Influxdb, Go, Swagger  
* Automated documentation, code and test case generation etc.  


 **Fault tolerant** 

* Recovers from node, process failures, network partitions  
* No impact to production traffic if Venice is offline  


 **Built-in troubleshooting** 

* Collects logs/events/metrics/fw logs  
* Indexes for easier search  
* APIs to access data  


# Naples vs. Venice REST API

This document focus on Venice as the controller.  Each Naples adapter is solely controlled by Venice.  However, Naples also has its own REST API (Very similar to the Venice REST API) and can be controlled by a 3rd party controller, such as a custom controller.  In the case where Venice is not present, the 3rd party controller would be the central manager and connect directly to each Naples card using Naples REST API or Naples gRPC interfaces.  Naples REST API and gRPC is out of scope of this document, and the illustration in the image is only here for informational purpose and will not be discussed further in the document.

![image alt text](/images/venice/image_2.png)

# Venice REST Architecture and Overview

Venice is a distributed software that consists of distributed microservices, the services are scheduled and controlled by Kubernetes (K8s).  Venice uses "node majority" as a quorum type.  The numbers of Venice nodes are therefore 3 (N+1 fault tolerant), or 5 Nodes (N+2 fault tolerant).   More than 5 Venice Nodes can be configured to increase resources for the Venice cluster (for example storage for stats),  however this will not increase the fault tolerance (N+1 vs N+2).   Venice Nodes can run on bare metal or on VM’s.  However it is important that the Nodes run’s on separate H/W. The Key Value (KV) store is based on **etcd** and is distributed across the 3 or 5 Nodes.  Maintaining low latency between the Nodes is critical to cluster performance, therefore all nodes need to be located and in same Data Center.  All Venice components use gRPC to communicate with other Venice nodes. Logs are stored in ElasticSearch.   Statistics are stored in a distributed implementation of InfluxDB.

![image alt text](/images/venice/image_3.png)

In Venice the API,  gateways are distributed and run on all Venice Nodes.  There is currently one instance of the API Server running.  Like all the other services, this service is redundant and will be restarted elsewhere by K8s in case of a node failure.  All cluster services like Network, Storage, and Controllers including the API Server are distributed on the Venice Nodes, and are all managed and scheduled by the K8s Controller.

Since the Venice API Gateways runs on all nodes, the REST Client can send its request to any of the Venice Nodes IP address or FQDN.  If a single FQDN or IP Address is preferred, DNS load balancing is recommended.   This enables the REST Client’s to send the requests to a single FQDN or IP address and still benefit from the distributed nature of Venice.

The Venice REST API is asynchronous in nature.  A client will describe a "desired state" (intent) via the API.  Venice the applies the desired state to the components as needed.   The Observed state (actual state) is maintained and updated by Venice and describes the current state of each component.

 **Please note:** 

_Venice will continuously drive Observed state to reflect Desired state._

Below is an example of the flow.   In this example the REST client makes a request that will affect the network settings on one or more Naples.

![image alt text](/images/venice/image_4.png)

1. An API Gateway receives the REST call, process Authorization/RBAC  
2. It sends it to the API server which validates the intent of the request  
3. The API Server writes the request in the form of an object to the KV Store.  
4. The API Server writes the response back to the REST Client (4a) and at the same time, based on the nature of the request, a controller (e.g., Network Service) takes the intent (4b) from from KV store  
5. The Controller sends the request to the agent on one or more Naples nodes  
6. The Agent on the Naples Node uses the HAL (Hardware Abstraction Layer) to transform the generic request to Naples specific calls  
7. The result of the request is reported back to the API server via the Network Controller  


 **Please note:** 

_The request response (4a) is a confirmation of the intent (Desired state), not the actual result of the change, the actual change on the Naples happens at a later time (6), and the Naples state is updated in KV store (7) (Observed State). The REST client can issue a new REST request and query for the Observed state of the Naples if needed._

# Venice API Design

The design goals and internal requirements for the API was to create a modern, simple programmatic interface that is capable of evolving over time as needed. The design was inspired by Kubernetes for being modern, scalable, efficient, flexible, and includes the following:

* REST Semantics  
* HTTP or HTTPS  
* Default TCP port: 10001  
* CRUD operations (POST, GET, PUT, DELETE)  
* JSON object structure in payload  
* Cookie based authentication  
* LDAP, RADIUS or Local  
* Multi-tenant enabled  
* RBAC for individual objects  
* Uniform object definition  
* Stats & Usage, Errors, Auditing, Authentication etc.  
* API is declarative and operations are idempotent  
* User specifies the intent, Status describes the actual state  
* Ability to search by object labels, names or attributes  
* Built-in Diagnostics (API call tracing)  


## Object Structure and Definition

The Venice object model is inspired by K8s where user a user specifies the intent, operations are idempotent, and status describes the actual state.

 **Kind:** type of the object **Version:** object version (optional) **Meta:** object metadata (common to all objects, all fields are optional) **Name:** string name of the object (user provided unique string for this kind of object) **Tenant:** tenant name of the object (optional) **Labels:** arbitrary tags associated with an object

…

Spec: Object Specific Schema

…

Status: Object Specific Status Schema

…

Example:

![image alt text](/images/venice/image_5.png)

## Object Relationships

There are three ways object can express relationships in the model: by Named Reference, Label Selectors or Field Selectors

### Named Reference

![image alt text](/images/venice/image_6.png)

Object "corp-network-208" references object “esx-host-lab22-mgmt1” by its name “esx-host-lab22-mgmt1”

### Label Selectors

![image alt text](/images/venice/image_7.png)

Object "prod-db-security-group" references object “dc11-lab54-vm243” by its labels “tier:db” and “env:prod”

### Field Selectors

![image alt text](/images/venice/image_8.png)

Object "storage-admin" references object “dc11-lab54-vm243-vol1” by its “kind” (“Volume”)

### Object Model and Dependencies

Below is an image describing the relationship between top-level objects in the object model.

![image alt text](/images/venice/image_9.png)

# HTTP Messages and Operations

HyperText Transfer Protocol (HTTP) is the underlying protocol used by the REST API.  This protocol defines how messages are formatted, transmitted and received.  HTTP is a stateless protocol and each command is executed independently.  Each HTTP call includes a Uniformed Resource Identifier (URI) which describes the end-point object.

## Object Scope

There are two kinds of objects, Cluster wide objects and Tenant wide objects.  Cluster wide objects are global to the cluster while tenant wide objects are unique to each tenant. Some examples of Cluster wide objects are Cluster, Node and AuthenticationPolicy. Tenant wide objects include Network, SecurityGroup etc.  Please see the API reference for more details on individual objects.

## URI structure for a Cluster wide object

The URI structure describes a hierarchical structure and contains the information:



```
<Protocol>://<Venice-Node>:<Port>/<category>/<api-group>/<Version>/<Object Kind>/<Object-Instance>
```

| What | Example | Description |
|------|---------|-------------|
| Protocol | HTTPS | Protocol can be HTTPS or HTTP |
| Venice-Node | Venice-node | Domain name or IP address of a Venice Node |
| Port | 10001 | Venice Management port (API Gateway), default is 10001 (Available on all Venice Nodes) |
| Category | configs | API category like configs, metrics, events etc. |
| Api-group | cluster | API-Group groups related Objects like cluster, security, network etc. |
| Version | v1 | API version, this assure backwards compatibility with older integrations and customizations |
| Object Kind | cluster | The object type string, defines the type of object we are referring to |
| Object-Instance | cluster | Name or UUID of the Object key |

For example, URI: [https://venice-node:10001/configs/cluster/v1/nodes/node-1](https://venice-node:10001/configs/cluster/v1/nodes/node-1)

## URI structure for a Tenant wide object

The URI structure describes a hierarchical structure and contains the information:



```
<Protocol>://<Venice-Node>:<Port>/<category>/<api-group>/<Version>/tenant/<tenant-name>/<Object Kind>/<Object-Instance>
```

| What | Example | Description |
|------|---------|-------------|
| Protocol | HTTPS | Protocol can be HTTPS or HTTP |
| Venice-Node | Venice-node | Domain name or IP address of a Venice Node |
| Port | 10001 | Venice Management port (API Gateway), default is 10001 (Available on all Venice Nodes) |
| Category | configs | API category like configs, metrics, events etc. |
| Api-group | cluster | API-Group groups related Objects like cluster, security, network etc. |
| Version | v1 | API version, this assure backwards compatibility with older integrations and customizations |
| Tenant | tenant | Indicates that URI is pointing to a specific tenant (Optional) |
| Tenant-name | MyOrg | Tenant name |
| Object Kind | Networks | The object type string, defines the type of object we are referring to |
| Object-Instance | Corp-204-net | Name or UUID of the Object key |

For example, URI: [https://venice-node:10001/configs/network/v1/tenant/default/networks/corp-204-net](https://venice-node:10001/configs/network/v1/tenant/default/networks/corp-204-net)

## HTTP Methods (CRUD) supported

The Pensando REST API uses the following HTTP methods to perform Create, Read, Update and Delete (CRUD) operations:

| HTTP Method | Operation | Description |
|-------------|-----------|-------------|
| POST | Create | Create a new object |
| GET | Read | Returns one or more objects |
| PUT | Update | Update an existing object |
| DELETE | Delete | Delete an existing object |

## HTTP Response Messages

Each CRUD call receives a response message that indicates the return status of the call.  It is recommended to use the HTTP response code as the primary indicator success or failure of the operation. The JSON Payload response will also contain return status and details. Below are the response status-codes that Venice will use to indicate the high level result of the operation.

 **Please note:** 

_The Venice API Gateway sends back a JSON structured payload in which includes the details of the response. \__
Best_
_practice is to first check the HTTP response code, and then parse the JSON data to get the details._

| Status-Code | Description |
|-------------|-------------|
| 200 | OK\* |
| 400 | Bad request parameters |
| 401 | Unauthorized request |
| 409 | Conflict while processing request |
| 412 | Pre-condition failed |
| 500 | Internal Server Error |
| 501 | Request not implemented |

\*Please note this is an empty response and means OK.

## JSON Payload (PUT and POST Operations)

Below is an example of a POST payload to create a user object "myuser", with local authentication.



```
{
    "kind": "User",
    "api-version": "v1",
    "meta": {
      "tenant": "default",
      "name": "myuser"
    },
    "spec": {
      "fullname" : "My Username",
      "password" : "mypass",
      "type": "Local",
      "email": "myemail@pensando.io"
    }
}
```

In this example, the HTTP method would be POST operation, and the URI would be

[http://10.10.10.10:10001/configs/auth/v1/tenant/default/users](http://10.10.10.10:10001/configs/auth/v1/tenant/default/users)

(Example uses Venice IP address: 10.10.10.10 and port: 10001)

## JSON Response payload

Below is an example of a payload to create a user object with two labels and a role.

Please note that Venice will always send back the complete object after a create (POST) or update (PUT) operation.

### Example of a Successful response



```
{
	"kind": "User",
	"api-version": "v1",
	"meta": {
	"name": "myuser",
		"tenant": "default",
		"resource-version": "2262",
		"uuid": "16d38a54-d798-496a-93d9-02d4aa1b5b46",
		"creation-time": "2018-07-25T22:06:24.67126146Z",
		"mod-time": "2018-07-25T22:06:24.67127234Z",
		"self-link": "/configs/auth/v1/tenant/default/users/myuser"
	},
		"spec": {
		"fullname": "My Username",
		"email": "myemail@pensando.io",
		"type": "Local"
	},
	"status": {}
}
```

### Example of a Failure (Error) response



```
{
	"kind": "Status",
	"result": {
		"Str": "Object store error"
	},
	"message": [
   		"Object create failed: Key already exists"
	],
	"code": 409,
	"object-ref": {
   		"tenant": "default",
   		"kind": "User",
   		"name": "myuser"
	}
}
```

# About the API

## Sessions

To access and execute API calls against a Venice cluster, the client must first authenticate itself. This done via the login API endpoint.  Once the client has made a successful login,  it will receive a cookie (Session ID) in the header "Set-Cookie" of the response from the login call.  The header contains the cookie name, “sid”, value, expiry time, and other info.

 **Please note:** 

_Venice does not have any local_
_predefined_
_user/admin accounts_
_.  I_
_t is not mandatory for Venice to have local accounts defined.  At the time of installation, the installer typically will setup the authentication method.  Venice can be configured to use local and/or remote authentication (_
_e.g._
_AD and RADIUS).  If local authentication is selected,  the installer should also create the very first_
**_admin_**
_account._

The cookie is used to authenticate each API call made to Venice.  The client will need to provide the cookie in the header in all subsequent requests to the Venice.

### Login

To login to Venice via the REST API, the HTTP method would be a POST operation, and the URI would be: [http://10.10.10.10:10001/v1/login](http://10.10.10.10:10001/v1/login)



```
{
	"username": "admin",
	"password": "password",
	"tenant": "default"
}
```

(Example uses Venice IP address: 10.10.10.10 and port: 10001)

### Response Header

The response headers are typically contain nothing more than the status codes.  However, the response header from a successful login will contain the authorization Cookie (sid).   The cookie is used for authorization and must be provided for all consecutive REST API calls. The cookies are generated by the system and returned to the authenticating client (during login).  Each cookie contains all the information needed for the Venice system to validate the request next time it sees the cookie.

 **Please note:** 

_Once a cookie has been generated and issued to a client, the system will not maintain knowledge of that cookie_
_. \__
_T_
_
_he cookie contains all information needed for the system to validate any requests and therefore there is no need to invalidate an issued cookie (Logout) in the system.  However deleting a user or changing RBAC privileges user, will immediately affect any existing valid cookies the user might have.  The default_
_expiration_
_for a cookie is 6 days._

The response header will look similar to:

 **Set-Cookie:** sid=eyJjc3JmIjoiN2E3SGJZZHNJNXBaNGhkak5EU3VrYXBfNU43SjVFY0ozZ2FzeTA3aXdwZz0iLCJleHAiOjE1Mjg4MzcyNzIsImlhdCI6MTUyODMxODg3MiwiaXNzIjoidmVuaWNlIiwicm9sZXMiOm51bGwsInN1YiI6Im15dXNlciIsInRlbmFudCI6ImRlZmF1bHQifQ.AqFY1moQ1QKMOibt52wNvP1O2b4WtsPwc3jy\_Px9LD\_lEmkv\_jtKZ7EOvJsU4ybtUYdyUcYWZg48bLi8AMjWdw; Path=/; Expires=Tue, 12 Jun 2018 21:01:12 GMT; Max-Age=518400; HttpOnly

 **Name of cookie:** sid

 **Date:** Wed, 06 Jun 2018 21:01:12 GMT

(Date cookie was generated)

 **Expires:** Wed, 06 Jun 2018 21:01:12 GMT

(+6 Days from creation)

 **Max-Age:** 518400

(518400 / 24 / 60 / 60 = 6 Days in seconds)

### The Cookie

There is no concept of a cookie refresh.  A cookie is valid for six days.  If the REST client needs access for a longer period, the it shall re-login and get a new cookie prior to the expiration of the current cookie.

### Logout

There is no concept of a logout.  When a REST client doesn't need access any longer it can simply discard the current cookie.

## Staging Buffer

Staging Buffer allows for multiple configurations to be applied in one single call instead of multiple calls.  When staging configuration, individual configuration updates are authorized and validated but are not applied.  These configuration changes are accumulated in a staging buffer. A commit operation on the staging buffer then applies and persists the entire staging buffer in a single call.   The illustration below shows the configuration flow when using configuration staging.

![image alt text](/images/venice/image_10.png)

The staging buffer is represented as an object, and is used for accumulating the configuration changes.    The staging buffer is identified by an ID which could be user provided for named buffers or a system generated ID.  All staging operations will then use this identifier.

There are two categories of actions related to the staging buffer:

* Operations on the staging buffer itself  
* Staged operations on other objects that get staged in the staging buffer  


### Operations on the staging buffer object

All actions on the staging buffer and staging will go through RBAC authorization.  In addition to privileges for CRUD operations for API objects that are staged, the following privileges are associated to a staging buffer object itself :

* Create a staging buffer    
* Update contents of a staging buffer  
* List contents of the buffer   
* Commit the buffer   
* Delete the staging buffer   
* List active staging buffers  




Only operations for which the user has privileges will be allowed on the Staging buffer. The Update, List and Commit Operations have additional considerations with staging buffer.

 **Update:** Updating the staging buffer involves adding API Object CRUD operations to the staging buffer. The CRUD operations themselves are authorized separately.  To update the staging buffer with a an API operation, the user needs to have the update privilege on the staging buffer AND privilege for the CRUD operation being staged.

 **List:** The staging buffer can have updates from multiple users.  Therefore, listing of the staging buffer contents is hence also bound by user privileges on the staged object. A post-call hook in the API gateway for staging endpoint will perform a call for authorizing and filtering contents of the staging buffer in the response.

 **Commit:** The commit operation applies the changes in the staging buffer to the system. The user performing the commit should have commit privileges on the staging buffer and also privileges for the operations in the commit buffer.

### Operations on objects staged in the staging buffer

The staging buffer itself will support creation, listing of changes in the staging buffer, validation, committing, and deleting the staging buffer. The REST API will expose the POST, GET, DELETE and LIST Methods.  In addition to this a Commit Action is also exposed.

 **Create:** Creates a new staging buffer. The identifier can be user-specified or will be a system-generated ID. This identifier is used for all subsequent operations on the staging buffer.

 **Get:** Lists all the contents of the staging buffer. It will also validate the contents. This involves both semantic and syntactic validation at the API server. Each object in the buffer is validated, considering all the other objects in the the staging buffer, plus the current state of the KV store. The Validation result specifies "success" or “failure”,  as well as any objects that failed validation along with failure messages.

 **Clear:** Clears any entries in the staging buffer. The "clear" could be for any operation that is staged (Create/Update/Delete). Elements to be cleared are identified in the request using an URI.

 **Commit:** Commits the contents of the staging buffer to active configuration. The entire staging buffer may be committed or a subset of the buffer may be chosen. This is committed as an all-or-none transaction. If there are any changes from the last time the staging buffer was validated, then the commit could fail. If the commit operation succeeds then those parts of the content that were part of the commit are deleted.

 **Delete:** Deletes the staging buffer and all its contents.

## Tenants

Below is an image describing the objects that are affected by the tenant object, please note that the default tenant is the only tenant currently supported.



# ![image alt text](/images/venice/image_11.png)

# Appendix A

## Using the API, CRUD Examples

Below are examples of all the CRUD operations.  For the complete reference, please see the the Online Reference Guide at http://IP-addr:10001/docs

## Login

Below is an example of a login to a Venice system, and cookie retrieval (Assuming IP Address 10.10.10.10, and the user "myuser" exists etc.).

 **Please note: \_T** he_
_"_
_default" tenant is specified._

POST: [HTTP://10.10.10.10:10001/v1/login](HTTP://10.10.10.10:10001/v1/login)

 **Request** **Header:**

"Content-Type: application/json"

 **Content-Type:** application/json

 **Request** **Body:**



```
{
	"username": "admin",
	"password": "password",
	"tenant": "default"
}
```

Assuming the login was successful, here is an example of the response:

 **HTTP Response code:** 200 OK

 **Note:** 

_If you have access to a Venice system and client with_
_"_
_curl_
_",_
_you can test above examples by running following command  (_
_C_
_hange_
_to an appropriate_
_IP Address):_



```
# curl -j -c Venice-cookie-jar.txt -X POST -H "Content-Type: application/json" -d '{"username":"myuser","password":"mypass","tenant": "default"}' http://10.10.10.10:10001/v1/login
```

 **Please note:** 

_The above example will create a local text file called "Venice-cookie-jar.txt" on your local disk with the cookie_
_(‘-c’ option), the other “curl” samples use ‘-b’ to send the cookie._

 **Response** **Header:**

 **…** 

 **Set-Cookie:** sid=eyJjc3Jm…eiwsjnlthE\_wptPIA; Path=/; Expires=Mon, 11 Jun 2018 01:20:48 GMT; Max-Age=518400; HttpOnly

 **Please note:** 

_The cookie is only returned in the header after a successful call to login endpoint_
_.  A_
_lso the cookie in this example was truncated for easy reading, with the truncated version used in the examples below._

 **Response** **Body:**



```
{
	"kind":"User",
	"api-version":"v1",
	"meta":{
		"name":"myuser",
		"tenant":"default",
		"resource-version":"14944",
		"uuid":"11d5aeff-81f1-487c-a0fe-51e9d3cb949f",
		"creation-time":"2018-06-05T00:55:26.79488816Z",
		"mod-time":"2018-06-05T00:55:26.794899347Z",
		"self-link":"/configs/auth/v1/tenant/default/users/myuser"
	},
	"spec":{
		"fullname":"MyUsername",
		"email":"myemail@pensando.io",
		"type":"LOCAL"
	},
	"status":{}
}
```

Venice returned the the user object in the body.

In the header of the response message from the successful login call (Example above), Venice provided the session cookie to the client.

## Create an Object (Workload)

Example below creates a workload object.

POST: [HTTP://10.10.10.10:10001](HTTP://10.10.10.10:10001/v1/login)/configs/workload/v1/workloads

 **Request Body:** 



```
{
    "api-version": "v1",
    "meta": {
        "name": "gs-vm-1",
        "namespace": "default"
    },
    "spec": {
        "host-name": "naples1-host",
        "interfaces": [
            {
                "mac-address": "00:50:56:00:00:03",
                "micro-seg-vlan": 103,
                "external-vlan": 1003
            },
            {
                "mac-address": "00:50:56:00:00:04",
                "micro-seg-vlan": 104,
                "external-vlan": 1004
            }
        ]
    }
}
```

 **To create the object using curl:** 



```
# curl -j -b Venice-cookie-jar.txt -X POST -H "Content-Type: application/json" -d '{"api-version":"v1","meta":{"name":"gs-vm-1","namespace":"default"},"spec":{"host-name":"naples1-host","interfaces":[{"mac-address":"00:50:56:00:00:03","micro-seg-vlan":103,"external-vlan":1003},{"mac-address":"00:50:56:00:00:04","micro-seg-vlan":104,"external-vlan":1004}]}}' http://10.10.10.10:10001/configs/workload/v1/workloads
```

 **Response Body:** 



```
{
    "kind": "Workload",
    "api-version": "v1",
    "meta": {
        "name": "gs-vm-1",
        "tenant": "default",
        "namespace": "default",
        "generation-id": "1",
        "resource-version": "46339",
        "uuid": "76fafeec-4dd7-47e8-af2f-408771852856",
        "creation-time": "2019-01-25T16:22:15.453949579Z",
        "mod-time": "2019-01-25T16:22:15.453951226Z",
        "self-link": "/configs/workload/v1/tenant/default/workloads/gs-vm-1"
    },
    "spec": {
        "host-name": "naples1-host",
        "interfaces": [
            {
                "mac-address": "00:50:56:00:00:03",
                "micro-seg-vlan": 103,
                "external-vlan": 1003
            },
            {
                "mac-address": "00:50:56:00:00:04",
                "micro-seg-vlan": 104,
                "external-vlan": 1004
            }
        ]
    },
    "status": {}
}
```

## Show a Object (Workload)

Example below shows an existing workload object called "gs-vm-1".

GET: [HTTP://10.10.10.10:10001](HTTP://10.10.10.10:10001/v1/login)/configs/workload/v1/workloads/gs-vm-1

 **To get the object using curl:** 



```
# curl -j -b Venice-cookie-jar.txt -X GET -H "Content-Type: application/json" http://10.10.10.10:10001/configs/workload/v1/workloads/gs-vm-1
```

 **Response Body:** 



```
{
    "kind": "Workload",
    "api-version": "v1",
    "meta": {
        "name": "gs-vm-1",
        "tenant": "default",
        "namespace": "default",
        "generation-id": "1",
        "resource-version": "46339",
        "uuid": "76fafeec-4dd7-47e8-af2f-408771852856",
        "creation-time": "2019-01-25T16:22:15.453949579Z",
        "mod-time": "2019-01-25T16:22:15.453951226Z",
        "self-link": "/configs/workload/v1/tenant/default/workloads/gs-vm-1"
    },
    "spec": {
        "host-name": "naples1-host",
        "interfaces": [
            {
                "mac-address": "00:50:56:00:00:03",
                "micro-seg-vlan": 103,
                "external-vlan": 1003
            },
            {
                "mac-address": "00:50:56:00:00:04",
                "micro-seg-vlan": 104,
                "external-vlan": 1004
            }
        ]
    },
    "status": {}
}
```

## Update an Object (Workload)

Following example shows the modification of an existing workload object called "gs-vm-1".

Assuming that the "gs-vm-1" object was created above, this example will add a label: “Location: us-west-A” and modify one of the interfaces (00:50:56:00:00:04) to use “micro-seg-vlan: 105”, and “external-vlan: 1005”.

PUT: [HTTP://10.10.10.10:10001](HTTP://10.10.10.10:10001/v1/login)/configs/workload/v1/workloads/gs-vm-1

 **Request Body:** 



```
{
    "api-version": "v1",
    "meta": {
        "name": "gs-vm-1",
        "namespace": "default",
        "labels": {
            "Location": "us-west-A"
        }
    },
    "spec": {
        "host-name": "naples1-host",
        "interfaces": [
            {
                "mac-address": "00:50:56:00:00:03",
                "micro-seg-vlan": 103,
                "external-vlan": 1003
            },
            {
                "mac-address": "00:50:56:00:00:04",
                "micro-seg-vlan": 105,
                "external-vlan": 1005
            }
        ]
    }
}
```

 **To update the object using curl:** 



```
# curl -j -b Venice-cookie-jar.txt -X PUT -H "Content-Type: application/json" -d '{"api-version":"v1","meta":{"name":"gs-vm-1","namespace":"default","labels":{"Location":"us-west-A"}},"spec":{"host-name":"naples1-host","interfaces":[{"mac-address":"00:50:56:00:00:03","micro-seg-vlan":103,"external-vlan":1003},{"mac-address":"00:50:56:00:00:04","micro-seg-vlan":105,"external-vlan":1005}]}}' http://10.10.10.10:10001/configs/workload/v1/workloads/gs-vm-1
```

 **Response Body:** 



```
{
    "kind": "Workload",
    "api-version": "v1",
    "meta": {
        "name": "gs-vm-1",
        "tenant": "default",
        "namespace": "default",
        "generation-id": "2",
        "resource-version": "49033",
        "uuid": "76fafeec-4dd7-47e8-af2f-408771852856",
        "labels": {
            "Location": "us-west-A"
        },
        "creation-time": "2019-01-25T16:22:15.453949579Z",
        "mod-time": "2019-01-25T16:47:58.126341517Z",
        "self-link": "/configs/workload/v1/tenant/default/workloads/gs-vm-1"
    },
    "spec": {
        "host-name": "naples1-host",
        "interfaces": [
            {
                "mac-address": "00:50:56:00:00:03",
                "micro-seg-vlan": 103,
                "external-vlan": 1003
            },
            {
                "mac-address": "00:50:56:00:00:04",
                "micro-seg-vlan": 105,
                "external-vlan": 1005
            }
        ]
    },
    "status": {}
}
```

## List Object's (Workloads)

Following example lists all existing workload objects.

GET: [HTTP://10.10.10.10:10001](HTTP://10.10.10.10:10001/v1/login)/configs/workload/v1/workloads/gs-vm-1

 **To get the object using curl:** 



```
# curl -j -b Venice-cookie-jar.txt -X GET -H "Content-Type: application/json" http://10.10.10.10:10001/configs/workload/v1/workloads
```

 **Response Body:** 



```
{
    "kind": "WorkloadList",
    "api-version": "v1",
    "list-meta": {},
    "items": [
        {
            "kind": "Workload",
            "api-version": "v1",
            "meta": {
                "name": "gs-vm-1",
                "tenant": "default",
                "namespace": "default",
                "generation-id": "2",
                "resource-version": "49033",
                "uuid": "76fafeec-4dd7-47e8-af2f-408771852856",
                "labels": {
                    "Location": "us-west-A"
                },
                "creation-time": "2019-01-25T16:22:15.453949579Z",
                "mod-time": "2019-01-25T16:47:58.126341517Z",
                "self-link": "/configs/workload/v1/tenant/default/workloads/gs-vm-1"
            },
            "spec": {
                "host-name": "naples1-host",
                "interfaces": [
                    {
                        "mac-address": "00:50:56:00:00:03",
                        "micro-seg-vlan": 103,
                        "external-vlan": 1003
                    },
                    {
                        "mac-address": "00:50:56:00:00:04",
                        "micro-seg-vlan": 105,
                        "external-vlan": 1005
                    }
                ]
            },
            "status": {}
        }
    ]
}
```

## Delete an Object (Workload)

Following example will delete an existing workload object called "gs-vm-1".

DELETE: [HTTP://10.10.10.10:10001](HTTP://10.10.10.10:10001/v1/login)/configs/workload/v1/workloads/gs-vm-1

 **To delete the object using curl:** 



```
# curl -j -b Venice-cookie-jar.txt -X DELETE -H "Content-Type: application/json" http://10.10.10.10:10001/configs/workload/v1/workloads/gs-vm-1
```

 **Response Body:** 



```
{
    "kind": "Workload",
    "api-version": "v1",
    "meta": {
        "name": "gs-vm-1",
        "tenant": "default",
        "namespace": "default",
        "generation-id": "2",
        "resource-version": "50524",
        "uuid": "6cbdd04a-fb27-43f1-926e-2ae8c62980c8",
        "labels": {
            "Location": "us-west-A"
        },
        "creation-time": "2019-01-25T17:02:09.358302981Z",
        "mod-time": "2019-01-25T17:02:12.322308386Z",
        "self-link": "/configs/workload/v1/tenant/default/workloads/gs-vm-1"
    },
    "spec": {
        "host-name": "naples1-host",
        "interfaces": [
            {
                "mac-address": "00:50:56:00:00:03",
                "micro-seg-vlan": 103,
                "external-vlan": 1003
            },
            {
                "mac-address": "00:50:56:00:00:04",
                "micro-seg-vlan": 105,
                "external-vlan": 1005
            }
        ]
    },
    "status": {}
}
```

## Create Multiple Object's Atomically via a staging buffer

Following examples show how to stage two operations in a staging buffer (SGPolicy and App).

The flow in this example is:

* Create the staging buffer  
* Stage a SGPolicy object into the buffer  
* Stage an APP object into the buffer  
* Validate the staging buffer  
* Commit the staging buffer  
* Delete the staging buffer  


 **Please Note:** 

_The buffer is order agnostic, and in this example we will create a SGPolicy (ny-dc01-sg-new) with a rule called "6\_ftp\_21\_21\_2". The rule will be staged after the SGPolicy in the buffer._

### Create the staging buffer

This will create a staging buffer called "TestBuffer"

POST: [HTTP://10.10.10.10:10001](HTTP://10.10.10.10:10001/v1/login)/configs/staging/v1/buffers

 **Request Body:** 



```
{
  "kind": "Buffer",
  "meta": {
    "name": "TestBuffer",
    "tenant": "default",
    "namespace": "default"
  },
  "spec": {}
}
```

 **To create the staging buffer object using curl:** 



```
# curl -j -b Venice-cookie-jar.txt -X POST -H "Content-Type: application/json" -d '{"kind":"Buffer","meta":{"name":"TestBuffer","tenant":"default","namespace":"default"},"spec":{}}' http://10.10.10.10:10001/configs/staging/v1/buffers
```

 **Response Body:** 



```
{
    "kind": "Buffer",
    "api-version": "v1",
    "meta": {
        "name": "TestBuffer",
        "tenant": "default",
        "namespace": "default",
        "generation-id": "1",
        "resource-version": "52199",
        "uuid": "745366e9-adc4-46bb-8169-8fe34414fe20",
        "creation-time": "2019-01-25T17:18:11.538349786Z",
        "mod-time": "2019-01-25T17:18:11.538351363Z",
        "self-link": "/configs/staging/v1/tenant/default/buffers/TestBuffer"
    },
    "spec": {},
    "status": {
        "validation-result": "",
        "errors": null,
        "items": null
    }
}
```

### Stage the SGPolicy into the buffer

This will create a SGPolicy object in the buffer called "TestBuffer", called “ny-dc01-sg-new”.

POST: [HTTP://10.10.10.10:10001](HTTP://10.10.10.10:10001/v1/login)/staging/TestBuffer/security/v1/sgpolicies

 **Request Body:** 



```
{
    "kind": "SGPolicy",
    "meta": {
        "name": "ny-dc01-sg-new",
        "tenant": "default",
        "namespace": "default"
    },
    "spec": {
        "attach-tenant": true,
        "rules": [
            {
                "apps": [
                    "6_ftp_21_21_2"
                ],
                "action": "PERMIT",
                "from-ip-addresses": [
                    "172.0.0.1",
                    "172.0.0.2",
                    "10.0.0.1/30"
                ],
                "to-ip-addresses": [
                    "192.168.1.1/16"
                ]
            },
            {
                "action": "PERMIT",
                "from-ip-addresses": [
                    "10.100.124.239/32"
                ],
                "to-ip-addresses": [
                    "10.103.45.77/32"
                ],
                "proto-ports": [
                    {
                        "protocol": "tcp",
                        "ports": "5439-5440"
                    }
                ]
            }
            
        ]
    }
}
```

 **To create the SGPolicy object in the staging buffer using curl:** 



```
# curl -j -b Venice-cookie-jar.txt -X POST -H "Content-Type: application/json" -d '{"kind":"SGPolicy","meta":{"name":"ny-dc01-sg-new","tenant":"default","namespace":"default"},"spec":{"attach-tenant":true,"rules":[{"apps":["6_ftp_21_21_2"],"action":"PERMIT","from-ip-addresses":["172.0.0.1","172.0.0.2","10.0.0.1/30"],"to-ip-addresses":["192.168.1.1/16"]},{"action":"PERMIT","from-ip-addresses":["10.100.124.239/32"],"to-ip-addresses":["10.103.45.77/32"],"proto-ports":[{"protocol":"tcp","ports":"5439-5440"}]}]}}' http://10.10.10.10:10001/staging/TestBuffer/security/v1/sgpolicies
```

 **Response Body:** 



```
{
    "kind": "SGPolicy",
    "api-version": "v1",
    "meta": {
        "name": "ny-dc01-sg-new",
        "tenant": "default",
        "namespace": "default",
        "generation-id": "",
        "uuid": "7c6dcfde-db56-4e18-b836-119cf464a1fe",
        "creation-time": "2019-01-25T17:48:36.895666726Z",
        "mod-time": "2019-01-25T17:48:36.895668514Z",
        "self-link": "/configs/security/v1/tenant/default/sgpolicies/ny-dc01-sg-new"
    },
    "spec": {
        "attach-tenant": true,
        "rules": [
            {
                "apps": [
                    "6_ftp_21_21_2"
                ],
                "action": "PERMIT",
                "from-ip-addresses": [
                    "172.0.0.1",
                    "172.0.0.2",
                    "10.0.0.1/30"
                ],
                "to-ip-addresses": [
                    "192.168.1.1/16"
                ]
            },
            {
                "proto-ports": [
                    {
                        "protocol": "tcp",
                        "ports": "5439-5440"
                    }
                ],
                "action": "PERMIT",
                "from-ip-addresses": [
                    "10.100.124.239/32"
                ],
                "to-ip-addresses": [
                    "10.103.45.77/32"
                ]
            }
        ]
    },
    "status": {
        "propagation-status": {
            "generation-id": "",
            "updated": 0,
            "pending": 0,
            "min-version": ""
        }
    }
}
```

### Stage the App policy into the buffer

This will create a App object in the buffer called "TestBuffer", called “6_ftp_21_21_2”.

POST: [HTTP://10.10.10.10:10001](HTTP://10.10.10.10:10001/v1/login)/staging/TestBuffer/security/v1/apps

 **Request Body:** 



```
{
    "api-version": "v1",
    "kind": "App",
    "meta": {
        "name": "6_ftp_21_21_2",
        "namespace": "default",
        "tenant": "default"
    },
    "spec": {
        "alg": {
            "Type": "FTP"
        },
        "proto-ports": [
            {
                "ports": "21-21",
                "protocol": "6"
            }
        ]
    }
}
```

 **To create the App object in the staging buffer using curl:** 



```
# curl -j -b Venice-cookie-jar.txt -X POST -H "Content-Type: application/json" -d '{"api-version":"v1","kind":"App","meta":{"name":"6_ftp_21_21_2","namespace":"default","tenant":"default"},"spec":{"alg":{"Type":"FTP"},"proto-ports":[{"ports":"21-21","protocol":"6"}]}}' http://10.10.10.10:10001/staging/TestBuffer/security/v1/apps
```

 **Response Body:** 



```
{
    "kind": "App",
    "api-version": "v1",
    "meta": {
        "name": "6_ftp_21_21_2",
        "tenant": "default",
        "namespace": "default",
        "generation-id": "",
        "uuid": "945263d9-5366-4445-9c32-d6e5b686ccba",
        "creation-time": "2019-01-25T17:52:21.06243185Z",
        "mod-time": "2019-01-25T17:52:21.062433431Z",
        "self-link": "/configs/security/v1/tenant/default/apps/6_ftp_21_21_2"
    },
    "spec": {
        "proto-ports": [
            {
                "protocol": "6",
                "ports": "21-21"
            }
        ],
        "alg": {
            "Type": "FTP"
        }
    },
    "status": {}
}
```

### Validate the staging buffer

Below example will verify the staging buffer called "TestBuffer".

GET: [HTTP://10.10.10.10:10001](HTTP://10.10.10.10:10001/v1/login)/configs/staging/v1/buffers/TestBuffer

 **To get the object using curl:** 



```
# curl -j -b Venice-cookie-jar.txt -X GET -H "Content-Type: application/json" http://10.10.10.10:10001/configs/staging/v1/buffers/TestBuffer
```

 **Response Body:** 



```
{
    "kind": "Buffer",
    "api-version": "v1",
    "meta": {
        "name": "TestBuffer",
        "tenant": "default",
        "namespace": "default",
        "generation-id": "1",
        "resource-version": "52199",
        "uuid": "745366e9-adc4-46bb-8169-8fe34414fe20",
        "creation-time": "2019-01-25T17:18:11.538349786Z",
        "mod-time": "2019-01-25T17:18:11.538351363Z",
        "self-link": "/configs/staging/v1/tenant/default/buffers/TestBuffer"
    },
    "spec": {},
    "status": {
        "validation-result": "SUCCESS",
        "errors": null,
        "items": [
            {
                "uri": "/configs/security/v1/tenant/default/sgpolicies/ny-dc01-sg-new",
                "method": "create",
                "object": {
                    "kind": "SGPolicy",
                    "api-version": "v1",
                    "meta": {
                        "name": "ny-dc01-sg-new",
                        "tenant": "default",
                        "namespace": "default",
                        "generation-id": "",
                        "creation-time": "1970-01-01T00:00:00Z",
                        "mod-time": "1970-01-01T00:00:00Z",
                        "self-link": "/venice/config/security/sgpolicies/default/ny-dc01-sg-new"
                    },
                    "spec": {
                        "attach-tenant": true,
                        "rules": [
                            {
                                "apps": [
                                    "6_ftp_21_21_2"
                                ],
                                "action": "PERMIT",
                                "from-ip-addresses": [
                                    "172.0.0.1",
                                    "172.0.0.2",
                                    "10.0.0.1/30"
                                ],
                                "to-ip-addresses": [
                                    "192.168.1.1/16"
                                ]
                            },
                            {
                                "proto-ports": [
                                    {
                                        "protocol": "tcp",
                                        "ports": "5439-5440"
                                    }
                                ],
                                "action": "PERMIT",
                                "from-ip-addresses": [
                                    "10.100.124.239/32"
                                ],
                                "to-ip-addresses": [
                                    "10.103.45.77/32"
                                ]
                            }
                        ]
                    },
                    "status": {
                        "propagation-status": {
                            "generation-id": "",
                            "updated": 0,
                            "pending": 0,
                            "min-version": ""
                        }
                    }
                }
            },
            {
                "uri": "/configs/security/v1/tenant/default/apps/6_ftp_21_21_2",
                "method": "create",
                "object": {
                    "kind": "App",
                    "api-version": "v1",
                    "meta": {
                        "name": "6_ftp_21_21_2",
                        "tenant": "default",
                        "namespace": "default",
                        "generation-id": "",
                        "creation-time": "1970-01-01T00:00:00Z",
                        "mod-time": "1970-01-01T00:00:00Z",
                        "self-link": "/venice/config/security/apps/default/6_ftp_21_21_2"
                    },
                    "spec": {
                        "proto-ports": [
                            {
                                "protocol": "6",
                                "ports": "21-21"
                            }
                        ],
                        "alg": {
                            "Type": "FTP"
                        }
                    },
                    "status": {}
                }
            }
        ]
    }
}
```

 **Please Note:** 

_Observe the response "validation-result": "SUCCESS" in the json._

### Commit the staging buffer

This will commit the staging buffer called "TestBuffer"

POST: [HTTP://10.10.10.10:10001](HTTP://10.10.10.10:10001/v1/login)/configs/staging/v1/buffers/TestBuffer/commit

 **Request Body:** 



```
{
  "kind": "CommitAction",
  "meta": {
    "name": "TestBuffer",
    "tenant": "default",
    "namespace": "default"
  },
  "spec": {}
}
```

 **To commit the staging buffer using curl:** 



```
# curl -j -b Venice-cookie-jar.txt -X POST -H "Content-Type: application/json" -d '{"kind":"CommitAction","meta":{"name":"TestBuffer","tenant":"default","namespace":"default"},"spec":{}}' http://10.10.10.10:10001/configs/staging/v1/buffers/TestBuffer/commit
```

 **Response Body:** 



```
{
    "kind": "CommitAction",
    "api-version": "v1",
    "meta": {
        "name": "TestBuffer",
        "tenant": "default",
        "namespace": "default",
        "generation-id": "",
        "uuid": "7ed7580d-9e76-4a21-a13e-dbb783120024",
        "creation-time": "2019-01-25T18:04:27.00464403Z",
        "mod-time": "2019-01-25T18:04:27.004645753Z",
        "self-link": "/configs/staging/v1/tenant/default/buffers/TestBuffer"
    },
    "spec": {},
    "status": {
        "status": "SUCCESS",
        "reason": ""
    }
}
```

 **Please Note:** 

_Once a buffer has been committed, it is empty and ready to be used again._

### Delete the staging buffer

This will delete the staging buffer called "TestBuffer"

DELETE: [HTTP://10.10.10.10:10001](HTTP://10.10.10.10:10001/v1/login)/configs/staging/v1/buffers/TestBuffer

 **Request Body:** 



```
{
  "kind": "Buffer",
  "meta": {
    "name": "TestBuffer",
    "tenant": "default",
    "namespace": "default"
  },
  "spec": {}
}
```

 **To delete the staging buffer using curl:** 



```
# curl -j -b Venice-cookie-jar.txt -X DELETE -H "Content-Type: application/json" -d '{"kind":"Buffer","meta":{"name":"TestBuffer","tenant":"default","namespace":"default"},"spec":{}}' http://10.10.10.10:10001/configs/staging/v1/buffers/TestBuffer
```

 **Response Body:** 



```
{
    "kind": "Buffer",
    "api-version": "v1",
    "meta": {
        "name": "TestBuffer",
        "tenant": "default",
        "namespace": "default",
        "generation-id": "1",
        "resource-version": "52199",
        "uuid": "745366e9-adc4-46bb-8169-8fe34414fe20",
        "creation-time": "2019-01-25T17:18:11.538349786Z",
        "mod-time": "2019-01-25T17:18:11.538351363Z",
        "self-link": "/configs/staging/v1/tenant/default/buffers/TestBuffer"
    },
    "spec": {},
    "status": {
        "validation-result": "",
        "errors": null,
        "items": null
    }
}
```

## Logout

Since there is no concept of a logout, simply discard the current cookie.

# Appendix B

## Objects and URIs

| Object | Uri |
|--------|-----|
| Alert | /v1/monitoring/{O.Tenant}/alerts |
| AlertDestination | /v1/monitoring/{O.Tenant}/alertDestinations |
| AlertPolicy | /v1/monitoring/{O.Tenant}/alertPolicies |
| App | /v1/security/apps |
| AppUser | /v1/security/{O.Tenant}/app-users |
| AppUserGrp | /v1/security/{O.Tenant}/app-users-groups |
| AuthenticationPolicy | /v1/auth/auth-policy |
| Certificate | /v1/security/{O.Tenant}/certificates |
| Cluster | /v1/cluster/cluster |
| Endpoint | /v1/workload/{O.Tenant}/endpoints |
| Event | /v1/monitoring/{O.Tenant}/events |
| EventPolicy | /v1/monitoring/{O.Tenant}/eventPolicy |
| FlowExportPolicy | /v1/monitoring/{O.Tenant}/flowExportPolicy |
| FwlogPolicy | /v1/monitoring/{O.Tenant}/fwlogPolicy |
| Host | /v1/cluster/hosts |
| LbPolicy | /v1/network/{O.Tenant}/lb-policy |
| MirrorSession | /v1/monitoring/{O.Tenant}/MirrorSession |
| Network | /v1/network/{O.Tenant}/networks |
| Node | /v1/cluster/nodes |
| Query | /v1/search/query |
| Role | /v1/auth/{O.Tenant}/roles |
| RoleBinding | /v1/auth/{O.Tenant}/role-bindings |
| SecurityGroup | /v1/security/{O.Tenant}/security-groups |
| Service | /v1/network/{O.Tenant}/services |
| Sgpolicy | /v1/security/{O.Tenant}/sgpolicy |
| SmartNIC | /v1/cluster/smartnics |
| StatsPolicy | /v1/monitoring/{O.Tenant}/statsPolicy |
| Tenant | /v1/cluster/tenants |
| TrafficEncryptionPolicy | /v1/security/{O.Tenant}/trafficEncryptionPolicy |
| User | /v1/auth/{O.Tenant}/users |
| Workload | /v1/workload/{O.Tenant}/workloads |

