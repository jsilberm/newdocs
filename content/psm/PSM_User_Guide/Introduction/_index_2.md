---
title: "Introduction"
menu:
  docs:
    parent: "PSM Enterprise Edition User Guide"
weight: 3
categories: [psm]
toc: true
---
## Introduction
This guide describes how to install and operate the Pensando Policy and Services Manager (PSM) and deploy the Distributed Services Card (DSC). Please refer to the Pensando Distributed Services Card (DSC) User Guide for DSC installation and setup instructions.
A DSC is installed in a PCIe slot and provides network and storage services to the host, allowing fully programmable control of all services, including security and visibility features.
The PSM allows for configuration and delivery of network, security, and telemetry policies to Pensando DSCs at scale.  
The PSM can be accessed via the IP address or host name of any of the PSM cluster nodes or, if a load balancer is being used, the IP address or host name presented by the load balancer.  In this document, the PSM address will be referenced as either `$PSMaddr` when used in the context of shell commands or scripts, or as `PSMaddr` in other examples.
The PSM is managed through either its browser-based GUI or its secure RESTful API.  Most examples in this document show the GUI, which is accessible at the URI `https://PSMaddr`. 
The PSM API is introduced in the section <ins>Managing the PSM via the REST API</ins>, and is covered in more detail in the separate document *Policy and Services Manager REST API Getting Started Guide*. The API can be used by posting REST calls in JSON format to the same URI, `https://PSMaddr.`
Parts of this document assume that readers have VMware ESXi or KVM system administration experience.
Users of the PSM and this guide are assumed to be familiar with REST APIs and JSON-based payloads. The term “endpoint”, used in the context of REST API calls and `curl` commands, refers to the URI with respect to the PSM instance `https://PSMaddr` .
Developers and operators are strongly encouraged to use tools such as Postman and Swagger-generated client libraries for API-based development whenever possible. The PSM distribution includes a working Postman collection with sample calls and payloads for multiple common use cases.
Please review the Release Notes for details and information about known issues, fixed bugs, supported servers, cables, and switches.
