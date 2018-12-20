---
title: Naples Overview
linktitle: Naples Overview
description: Naples Overview
menu:
  docs:
    parent: "naples"
    weight: 1
weight: 1
draft: false
toc: true
---

![Pensando Logo](/images/management/naples/Pensando_Logo.png)


Legal Stuff
-----------

Document Revision History
-------------------------

Known limitations and features not yet implemented:
===================================================

**Please note:**

*The NAPLES REST API is currently in an early stage of development (ALPHA), features that has not been implemented yet are not covered in this documentation. This document is subject to change.*

-   API Versioning is not implemented in URI
-   Authentication and Session Cookies, currently calls are
    accepted
-   HTTP only, HTTPS is not currently implemented
-   References to a single Object-instance (For example, you can list
    all objects of a certain kind, but you can not reference a specific
    object as an end-point one from the list) is currently not
    implemented


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

![Naples vs Venice](/images/management/naples/Naples_vs_Venice.png)


Please note that the Venice REST API is similar to NAPLES REST API, but they are not identical, please read the
Venice REST API documentation for further details on the Venice REST API.

NAPLES REST Architecture and Overview
=====================================

NAPLES REST API is synchronous in nature, the Observed state (actual state) is returned in the response of the request.

When it comes to the REST API, the main component inside NAPLES is the Agent, it runs on one of the ARM cores inside NAPLES. The Agent provides the REST API web-service for the external management and is the interface that external REST clients communicates with, such as Newman, Postman, Curl etc.

The Agent is written in Go language as a micro-service, the Agent is responsible for serving the REST API (and gRPC to and from Pensando Venice controller) requests to and from external REST clients, maintaining the object model and object relationships as well as communicate and manage the different hardware components via Hardware Abstraction Layer (HAL). The Objects are persistefied in an embedded BoltDB based database.

![Naples vs Venice](/images/management/Naples_Agent_Overview.png)

NAPLES REST API Design and Goals
================================

Our design goals for the API was to create a modern, simple programmatic interface that is capable of evolve over time as needed. Our design is inspired by Kubernetes, it’s modern, scalable, efficient and flexible. Below is a high level overview of the REST API:

-   REST Semantics
-   HTTP
-   Default TCP port: 9007\*
-   HTTP operations POST, PUT, GET and Delete
-   JSON object structure in payload
-   Multi-tenant enabled
-   Multi-namespace enabled
-   Uniformed object definition
-   API is declarative and operations are idempotent

**Please note:**

*The 9007 is the default TCP port for the simulator.*
