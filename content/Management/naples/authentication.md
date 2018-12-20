---
title: Authentication
linktitle: Authentication
description: Naples Authentication
menu:
  docs:
    parent: "naples"
    weight: 4
weight: 4
draft: false
toc: true
---

Authentication and Session Handling
==============================
Currently the REST API is only available to the host and not on to visibile to any external network, there is therefor no need for authentication.

To query for all defined namespace objects in the NAPLES:

**GET:** HTTP://10.10.10.10:9007/api/namespaces

**Header:**

Content-Type: application/json

**Response Message:**

HTTP Response code: 200 OK

**Headers:**  
(Nothing of relevance for the REST API)

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


