---
title: Misc
linktitle: Misc
menu:
  docs:
    parent: "naples"
    weight: 6
weight: 6
draft: false
toc: true
---

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

![Postman GUI](/images/management/Naples/Postman_GUI.png)


To get more details and information about the postman/Newman, please read the official documentation:
[https://www.getpostman.com/docs/v6/](https://www.getpostman.com/docs/v6/)


Troubleshooting
===============

