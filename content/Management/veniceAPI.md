---
title: Venice REST API Getting Started Guide
linktitle: Venice REST API Getting Started
description: Venice REST API Getting Started
menu:
  docs:
    parent: "management"
    weight: 1
weight: 1
draft: false
toc: true
---


![](/images/Pensando.png)


Version 0.1.0


Legal Stuff
-----------

Document Revision History
-------------------------


Document Overview
=================

This doucment convers the Pansando REST API, it is intended as a quick
start guide, and assumes basic knowledge of REST based API's.

The Pensando Representational State Transfer Application Programing
Interface (REST API) is a comprehensive interface that allows an
application to programmatically interact with Venice. Venice CLI and GUI
utilize the very same REST API to interact with Venice API Server, which
means that all features that are available in the GUI and the CLI are
also available via the API.

The API is a RESTful web service that is based on HTTP messages and
JavaScript Object Notation(JSON) in the payload. Requests are made to a
resource’s Uniform Resource Identifier (URI), and a response in JSON
format is returned based on the request made. The HTTP message specifies
the action (I.e. “Create”), the URI refers to an object-instance that is
exposed at the API endpoint and the payload contains the attributes that
should be applied to the object when created.

Venice Overview
===============

TEXT HERE...

Venice REST Architecture and Overview
=====================================

Venice is a distributed software that consists of distributed
microservices, the services are scheduled and controlled by Kubernetes
(K8s). Venice uses node majority as a quorum type, the numbers of Venice
nodes are 3 (N+1 fault tolerant), or 5 Nodes (N+2 fault tolerant). More
than 5 Venice Nodes can be configured to increase resources for the
Venice cluster (for example storage for stats), it will however not
increase the fault tolerance (N+1 vs N+2). Venice Nodes can run on bare
metal or on VM’s, however it is important that the Nodes run’s on
separate H/W. The Key Value (KV) store is based on etcd and is
distributed across the 3 or 5 Nodes, maintaining low latency between the
Nodes is critical to cluster performance, therefore they need to be
located and in same Data Center. All Venice components uses gRPC to
communicate with each others. Logs are stored in elastic, statistics are
stored in a distributed implementation of influxdb.

In venice the API gateways are distributed and runs on all Venice Nodes,
there is currently one instance of the API Server running. All cluster
services like Network, storage, starts Controllers including the API
Server etc are distributed on the Venice Nodes, they are managed and
scheduled by the K8s Controller.

Since the Venice Gateways runs on all nodes, the REST Client can send
its request to any of the Venice Nodes IP address or FQDN, if a single
FQDN or IP Address is preferred, DNS load balancing is recommended, this
enables the REST Client’s to send the requests to a single FQDN or IP
address and still benefit from the distributed nature of Venice.

Venice REST API is asynchronous in nature and client’s describes a
Desired state (intent) via the API, Venice applies the desired state to
the components as needed and when possible, the Observed state (actual
state) is maintained and updated by Venice, and it describes the current
state of each component.

**Please note:**

*Venice will continuously drive Observed state to reflect Desired
state.*

Below is an example of the flow, in this example the REST client makes a
request that will affect the network settings on one or more Naples.

![](/images/REST_API_Flow.png)

1.  An API Gateway receives the REST call, process Authorization/RBAC
2.  It sends it to the API server which validates the intent of the
    request
3.  The API Server writes the request in form of an object to the KV
    Store.
4.  The API Server write the response back to the REST Client (4a) and
    at the same time, based on the nature of the request, a controller
    (For example, Network Service) takes the intent (4b) from from KV
    store
5.  The Controller send the request to the agent on one or more Naples
    nodes
6.  The Agent on the Naples Node uses the HAL (Hardware Abstraction
    Layer) to transform the generic request to Naples specific calls
7.  The result of the request is reported back to the API server via the
    Network Controller

**Please note:**

*The request response (4a) is a confirmation of the intent (Desired
state), not the actual result of the change, the actual change on the
Naples happens at a later time (6), and the Naples state is updated in
KV store (7) (Observed State). The REST client can issue a new REST
request and query for the Observed state of the Naples if needed.*

Venice API Design
=================

Our goals and internal requirements for the API was to create a modern,
simple programmatic interface that is capable of evolve over time as
needed. Our design is inspired by Kubernetes, it’s modern, scalable,
efficient and flexible.

-   REST Semantics
-   HTTP or HTTPS
-   Default TCP port: 10001
-   CRUD operations (POST, GET, PUT, DELETE)
-   JSON object structure in payload
-   Cookie based authentication
-   LDAP, RADIUS or Local
-   Multi-tenant enabled
-   RBAC for individual objects
-   Uniform object definition
-   Stats & Usage, Errors, Auditing, Authentication etc.
-   API is declarative and operations are idempotent
-   User specifies the intent, Status describes what is real
-   Search by Object labels, Names or attributes
-   Built-in Diagnostics (API call tracing)

Object Structure and Definition
===============================

The Venice object model is inspired by K8s where user a user specifies
the intent, operations are idempotent, status describes what is real

**Kind:** aka type of the object

**Version:** object version (optional)

**Meta:** object metadata (common to all objects, all fields are
optional)

**Name:** string name of the object (user provided unique string for
this kind of object)

**Tenant:** tenant name of the object (optional)

**Labels:** arbitrary tags associated with an object

…

Spec: Object Specific Schema

…

Status: Object Specific Status Schema

…

![](/images/Single_Object_Yaml.png)

Object Relationships
--------------------

There are three ways object can express relationships in the model, by
Named Reference, Label Selectors or Field Selectors

### Named Reference

![](/images/Object_Named_Reference.png)

Object “corp-network-208” references object “esx-host-lab22-mgmt1” by
its name “esx-host-lab22-mgmt1”

### Label Selectors

![](/images/Object_Label_Selectors.png)


Object “prod-db-security-group” references object “dc11-lab54-vm243” by
its labels “tier:db” and “env:prod”

### Field Selectors

![](/images/Object_Field_Selectors.png)


Object “storage-admin” references object “dc11-lab54-vm243-vol1” by its
“kind” (“Volume”)

HTTP Messages and Operations
============================

HyperText Transfer Protocol (HTTP) is the underlying protocol used by
the REST API, this protocol defines how messages are formatted,
transmitted and received. HTTP is a stateless protocol and each command
is executed independently. Each HTTP call includes a Uniformed Resource
Identifier (URI) which describes the end-point object.

Object Scope
------------

There are two kinds of objects, Cluster wide objects and Tenant wide
objects. Cluster wide objects are global to the cluster while tenant
wide objects are unique to each tenant. Some examples of Cluster wide
objects are Cluster, Node and AuthenticationPolicy. Tenant wide objects
include Network, SecurityGroup etc. Please see the API reference for
more details on individual objects.

URI structure for a Cluster wide object
---------------------------------------

The URI structure describes a hierarchical structure and contains
information:

`<Protocol>://<Venice-Master>:<Port>/<category>/<api-group>/<Version>/<Object Kind\>/<Object-Instance>`

| What            | Example       |    Description                                                                              |
|-----------------|---------------|---------------------------------------------------------------------------------------------|
| Protocol        | HTTPS         | Protocol can be HTTPS or HTTP                                                               |
| Venice-Master   | Venice-master | Domain name or IP address of Venice Master                                                  |
| Port            | 10001         | Venice Management port, default is 10001                                                    |
| Category        | configs       | API category like configs, metrics, evets etc.                                              |
| Api-group       | cluster       | API-Group groups related Objects like cluster, security, network etc.                       |         
| Version         | v1            | API version, this assure backwards compatibility with older integrations and customizations |
| Object Kind     | cluster       | The object type string, defines the type of object we are referring to                      |
| Object-Instance | cluster       | Name or UUID of the Object key                                                              |

For example, URI:
<https://venice-master:10001/configs/cluster/v1/nodes/node-1>

URI structure for a Tenant wide object
--------------------------------------

The URI structure describes a hierarchical structure and contains
information:

`<Protocol>://<Venice-Master>:<Port>/<category>/<api-group>/<Version>/tenant/<tenant-name>/<Object Kind\>/<Object-Instance>`

| What            | Example       |    Description                                                                              |
|-----------------|---------------|---------------------------------------------------------------------------------------------|
| Protocol        | HTTPS         |  Protocol can be HTTPS or HTTP                                                              |
| Venice-Master   | Venice-master |  Domain name or IP address of Venice Master                                                 |
| Port            | 10001         |  Venice Management port, default is 10001                                                   |
| Category        | configs       |  API category like configs, metrics, events etc.                                            |
| Api-group       | cluster       |  API-Group groups related Objects like cluster, security, network etc.                      |
| Version         | v1            |  API version, this assure backwards compatibility with older integrations and customizations|
| Tenant          | tenant        |  Indicates that URI is pointing to a specific tenant (will be optional in the future)       |
| Tenant-name     | MyOrg         |  Tenant name                                                                                |
| Object Kind     | Networks      |  The object type string, defines the type of object we are referring to                     |
| Object-Instance | Corp-204-net  |  Name or UUID of the Object key                                                             |

For example, URI:
<https://venice-master:10001/configs/network/v1/tenant/default/networks/corp-204-net>

HTTP Methods (CRUD) supported
-----------------------------

The Pensando REST API uses the following HTTP methods to perform Create,
Read, Update and delete (CRUD) operations:

| HTTP Method | Operation | Description                 |
|-------------|-----------|-----------------------------|
| POST        | Create    | Create a new object         |
| GET         | Read      | Returns one or more objects |
| PUT         | Update    | Update an existing object   |
| DELETE      | Delete    | Delete an existing object   |

HTTP Response Messages
----------------------

Each CRUD call receives a response message that indicates the success of
the call, below are the response status-codes that Venice will use to
indicate the high level result of the operation.

**Please note:**

*The Venice API Gateway sends back a JSON structured payload in which
includes the details of the response. It is a good practice to first
check the HTTP response code, and then parse the JSON data to get the
details.*

| Status-Code | Description                       |
|-------------|-----------------------------------|
| 200         | OK\*                              |
| 400         | Bad request parameters            |
| 401         | Unauthorized request              |
| 409         | Conflict while processing request |
| 412         | Pre-condition failed              |
| 500         | Internal Server Error             |
| 501         | Request not implemented           |

\*Please note this is an empty response and means OK.

JSON Payload (PUT and POST Operations)
--------------------------------------

Below is an example of a payload to create a user object “myuser”, with
local authentication and with a role as rbac-admin.

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
          "type": "LOCAL",
          "email": "myemail@pensando.io"
        }
       }

In this example, the HTTP method would be POST operation, and the URI
would be

<http://10.10.10.10:10001/configs/auth/v1/tenant/default/users>

(Example uses Venice IP address: 10.10.10.10 and port: 10001)

JSON Response payload
---------------------

Below is an example of a payload to create a user object with two labels
and a role.

Please note that Venice will always send back the complete object after
a create (POST) or update (PUT) operation.

### Example of a Successful response

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
                "type": "LOCAL"
            },
            "status": {}
        }

### Example of a Failure (Error) response

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

About the API
=============

TEXT HERE

Sessions
--------

To be able to access and execute API calls against a running Venice the
client first need to authenticate itself, this done via the login
endpoint. Once the client have made a successfully login, it will
receive a cookie (Session ID) in the header “Set-Cookie” of the response
from the login call. The header contains the cookie name “sid”, value,
expiry time, and some other info.

The cookie is used to authenticate each API call made to Venice, the
client will need to provide the cookie in the header in all subsequent
request to the Venice.

### Login

TEXT HERE

### Cookies

Cookies are generated by the system to a requesting client that has been
authenticated (During login), each cookie contains all the information
needed for the Venice system to validate the request next time it sees
the cookie.

**Please note:**

*Once a cookie has been generated and issued to a client, the system
will not maintain knowledge of that cookie, the cookie contains all
information needed for the system to validate any requests and therefore
there is no need or concept to invalidate an issued cookie (Logout) in
the system.*

The cookie will expire after 6 days, the layout of a cookie is similar
to:

**Set-Cookie:**
sid=eyJjc3JmIjoiN2E3SGJZZHNJNXBaNGhkak5EU3VrYXBfNU43SjVFY0ozZ2FzeTA3aXdwZz0iLCJleHAiOjE1Mjg4MzcyNzIsImlhdCI6MTUyODMxODg3MiwiaXNzIjoidmVuaWNlIiwicm9sZXMiOm51bGwsInN1YiI6Im15dXNlciIsInRlbmFudCI6ImRlZmF1bHQifQ.AqFY1moQ1QKMOibt52wNvP1O2b4WtsPwc3jy\_Px9LD\_lEmkv\_jtKZ7EOvJsU4ybtUYdyUcYWZg48bLi8AMjWdw;
Path=/; Expires=Tue, 12 Jun 2018 21:01:12 GMT; Max-Age=518400; HttpOnly

Date: Wed, 06 Jun 2018 21:01:12 GMT

Here are a couple of interesting fields in the header:

**Header name:** Set-Cookie

**Name of cookie:** sid

**Date:** Wed, 06 Jun 2018 21:01:12 GMT (Date cookie was generated)

**Expires:** Wed, 06 Jun 2018 21:01:12 GMT (+6 Days from creation)

**Max-Age:** 518400 (518400 / 24 / 60 / 60 = 6 Days in seconds)

### Cookie Refresh

There is no concept of a cookie refresh. A cookie is valid for 6 days,
if the REST client need access for a longer period, it shall re-login
and get a new cookie prior to the expiration of the current cookie.

### Logout

There is no concept of a logout, when a REST client don’t need access
any longer it can simply discard the current cookie.

Executing REST API Requests
---------------------------

TEXT HERE

### Single Request

TEXT HERE

### Buffer Multiple Requests and Execute Atomically

TEXT HERE

### Test Buffered Requests Prior to Execution

TEXT HERE

Using the API, CRUD Examples
============================

TEXT HERE

Login
-----

Below is an example on a login to a Venice system, and cookie retrieval
(Assuming IP Address 10.10.10.10, and the user “myuser” exists etc.).

*Please note that the “default” tenant is specified.*

POST: <HTTP://10.10.10.10:10001/v1/login>

**Header:**

**Content-Type:** application/json

**Body:**

{“username”: “myuser”, “password”: “mypass”, “tenant”: “default”}

Assuming the login was successful, here is an example of the response:

**HTTP Response code:** 200 OK

**Note:**

*If you have access to a Venice system and client with curl and cli you
can test above examples by running following command from the cli (Don’t
forget to change the IP Address):*

`curl -j -c Venice-cookie-jar.txt -X POST -H "Content-Type: application/json" -d '{"username":"myuser","password":"mypass","tenant": "default"}' http://10.10.10.10:10001/v1/login/`

**Please note:**

*The above example will create a local text file called
“Venice-cookie-jar.txt” on your local disk with the cookie.*

**Headers:**

**…**

**Set-Cookie:** sid=eyJjc3Jm…eiwsjnlthE\_wptPIA; Path=/; Expires=Mon, 11
Jun 2018 01:20:48 GMT; Max-Age=518400; HttpOnly

**Please note:**

*The cookie is only returned in the header after a successful call to
login endpoint, also the cookie in this example was truncated for easy
reading, the truncated version is used in the examples below.*

**Body:**

`{"kind":"User","api-version":"v1","meta":{"name":"myuser","tenant":"default","resource-version":"14944","uuid":"11d5aeff-81f1-487c-a0fe-51e9d3cb949f","creation-time":"2018-06-05T00:55:26.79488816Z","mod-time":"2018-06-05T00:55:26.794899347Z","self-link":"/configs/auth/v1/tenant/default/users/myuser"},"spec":{"fullname":"MyUsername","email":"myemail@pensando.io","type":"LOCAL"},"status":{}}`

Venice returned the the user object in the body.

In the header of the response message from the successful login call
(Example above), Venice provided the session cookie to the client.

Create Object
-------------

TEXT HERE

Show Object
-----------

TEXT HERE

Update Object
-------------

TEXT HERE

Create Multiple Object's Atomically
-----------------------------------

TEXT HERE

List Object's
-------------

The following example assumes that you have access to a working curl and
successfully performed the above examples from the first step of Login
to Update Object

curl -b *Venice-cookie-jar.txt* -H “Content-Type: application/json”
<http://10.10.10.10:10001/configs/auth/v1/tenant/default/users>

**Please note:**

*The above example assumes you successfully run the curl command in the
login example above, that would have created the local file
“Venice-cookie-jar.txt”*

**Headers (**Nothing of interest for this discussion)

**Body:**

`{"T":{"kind":""},"ListMeta":{},"Items":[{"kind":"User","api-version":"v1","meta":{"name":"myuser","tenant":"default","resource-version":"462","uuid":"ff0fabc4-86b1-4004-b0de-331442ea6813","creation-time":"2018-06-05T18:33:24.872810795Z","mod-time":"2018-06-05T18:33:24.872812701Z","self-link":"/configs/auth/v1/tenant/default/users/myuser"},"spec":{"fullname":"My Username","email":"myemail@pensando.io","password":"$2a$12$r5GbwcVN4Al32jm1cwWPt.bmTJzhTMRIsxQ2k7Kd1Ut5Nvq4IHw0e","type":"LOCAL"},"status":{}},{"kind":"User","api-version":"v1","meta":{"name":"myuser2","tenant":"default","resource-version":"16794","uuid":"fbeb2e4c-db44-47d5-a8cb-a4bd65cd755f","creation-time":"2018-06-05T21:40:07.50790088Z","mod-time":"2018-06-05T21:40:07.507902424Z","self-link":"/configs/auth/v1/tenant/default/users/myuser2"},"spec":{"fullname":"MyUsername2","email":"myemail@pensando.io","password":"$2a$12$MZsxRSXFnQm0/MicXzJoje5UZpAY6Lzq5ftEjbVWetvjKBhXPeYsS","type":"LOCAL"},"status":{}}]}`

Venice returned two user objects, “myuser” and “myuser2” in the body.

Delete Object
-------------

TEXT HERE

Logout
------

Since thre is no concept of a logout, simply discard the current cookie.

Coding Guidelines
-----------------

Use buffers, testruns etc...

Troubleshooting
---------------

TEXT HERE

Appendix
--------

**Objects and URIs**

| Object                  | Uri                                             |
|-------------------------|-------------------------------------------------|
| Alert                   | /v1/monitoring/{O.Tenant}/alerts                |
| AlertDestination        | /v1/monitoring/{O.Tenant}/alertDestinations     |
| AlertPolicy             | /v1/monitoring/{O.Tenant}/alertPolicies         |
| App                     | /v1/security/apps                               |
| AppUser                 | /v1/security/{O.Tenant}/app-users               |
| AppUserGrp              | /v1/security/{O.Tenant}/app-users-groups        |
| AuthenticationPolicy    | /v1/auth/authn-policy                           |
| Certificate             | /v1/security/{O.Tenant}/certificates            |
| Cluster                 | /v1/cluster/cluster                             |
| Endpoint                | /v1/workload/{O.Tenant}/endpoints               |
| Event                   | /v1/monitoring/{O.Tenant}/events                |
| EventPolicy             | /v1/monitoring/{O.Tenant}/eventPolicy           |
| FlowExportPolicy        | /v1/monitoring/{O.Tenant}/flowExportPolicy      |
| FwlogPolicy             | /v1/monitoring/{O.Tenant}/fwlogPolicy           |
| Host                    | /v1/cluster/hosts                               |
| LbPolicy                | /v1/network/{O.Tenant}/lb-policy                |
| MirrorSession           | /v1/monitoring/{O.Tenant}/MirrorSession         |
| Network                 | /v1/network/{O.Tenant}/networks                 |
| Node                    | /v1/cluster/nodes                               |
| Query                   | /v1/search/query                                |
| Role                    | /v1/auth/{O.Tenant}/roles                       |
| RoleBinding             | /v1/auth/{O.Tenant}/role-bindings               |
| SecurityGroup           | /v1/security/{O.Tenant}/security-groups         |
| Service                 | /v1/network/{O.Tenant}/services                 |
| Sgpolicy                | /v1/security/{O.Tenant}/sgpolicy                |
| SmartNIC                | /v1/cluster/smartnics                           |
| StatsPolicy             | /v1/monitoring/{O.Tenant}/statsPolicy           |
| Tenant                  | /v1/cluster/tenants                             |
| TrafficEncryptionPolicy | /v1/security/{O.Tenant}/trafficEncryptionPolicy |
| User                    | /v1/auth/{O.Tenant}/users                       |
| Workload                | /v1/workload/{O.Tenant}/workloads               |


