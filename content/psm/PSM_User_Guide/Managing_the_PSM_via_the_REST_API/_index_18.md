---
title: "Managing the PSM via the REST API"
menu:
  docs:
    parent: "PSM Enterprise Edition User Guide"
weight: 19
categories: [psm]
toc: true
---
## Managing the PSM via the REST API
The PSM can be accessed programmatically through its REST API, which can be used by dedicated REST tools such as Postman, or via more basic utilities such as `curl`.
Full documentation for the PSM API is available online as part of the PSM installation at `https://PSMaddr/docs` and is also included in the release in the file `PSM_apidoc.pdf`.
Sample Postman Collections are provided within the PSM; the link can be found at the top of the PSM API documentation.
The PSM API facility supports the standard REST GET/POST/PUT/DELETE methods.
Note that when modifying an object with PUT, users *must always* follow a read-modify-write process, i.e. they must GET the entire object, change the fields that they want to modify, and PUT the updated object. Failure to do so may result in errors. The PSM API does not support the REST PATCH method: if object attributes aren’t provided, then they are not set in the object.
The examples in this section will use the `curl` utility, which is included or can be installed on most Linux distributions, to send REST requests.  The `jq` utility is used to format the JSON payloads returned by the commands.  Curl and jq are not available on ESXi hosts, but these examples can be run from any Linux host with network connectivity to the PSM.
### API Login Sessions into the PSM
Login is required for PSM API access, which creates a session cookie to be used for subsequent API calls.
The following login command uses a POST request to create a session cookie and store it in a local file named  “PSM-cookie-jar.txt”.  This command normally returns a JSON payload; this is suppressed in this example by piping it through “`grep HTTPSTATUS`”, which can be removed for a more verbose response.  Replace the username and password with those of an administrative user on the PSM[^kix.ir2uxzv8uqo4]. Always verify the success (200) of the HTTP response status code.


```
$ curl -sS -k -j -c ./PSM-cookie-jar.txt -X POST -H 'Content-Type: application/json' --write-out "HTTPSTATUS: %{http_code}" -d  '{"username":"admin","password":"Pensando0$","tenant": "default"}' https://$PSMaddr/v1/login | grep HTTPSTATUS
HTTPSTATUS: 200
  
  

```

### Interpreting Status Payloads
In response to a request to create or query an objects (i.e. “Workloads”, “NetworkSecurityPolicies”), the PSM will return a status payload in a format similar to this example:


```
"status": {
               "propagation-status": {
                   "generation-id": "1",
                   "updated": 0,
                   "pending": 2,
                   "min-version": "",
                   "status": "Propagation pending on: 
                              00ae.cd00.0008, 00ae.cd00.10c8",
                   "pending-dscs": [
                       "00ae.cd00.0008",
                       "00ae.cd00.10c8"
                   ]
               }
           }
  
  

```
The status attributes are:
`generation-id`:  A monotonically increasing version number, maintained by the PSM and incremented each time a given object is changed (i.e. a create/update operation).
`updated`: The number of DSCs, to which a given policy or object has been pushed or updated with respect to `generation-id`. 
`pending`: The number of DSCs to which a given policy or object has not yet been pushed or updated with respect to `generation-id`.
`min-version`:  The absolute minimum `generation-id` that might exist anywhere in the cluster, assuming a non-zero value of `pending`. If `pending` is 0, then `min-version` is null (i.e “”).
### Example: Network Security Policy Configuration
The section <ins>VMware vCenter Integration</ins> described how to use the PSM GUI to configure the PSM to point to one or more VMware vCenter systems; this can also be done via the API.
The REST request type would be POST, and the endpoint it should be sent to in this would be `https://$PSMaddr/configs/orchestration/v1/orchestrator .` The data that was entered into the GUI would formatted into a JSON request body:


```
{
    "meta": {
      "name": "DC-1-vCenter"
    },
    "spec": {
      "type" : "vcenter",
      "uri" : "dc-1-vcenter.local",
      "credentials": {
        "auth-type": "username-password",
        "username": "admin",
        "password": "xyz!",
      }
      "manage-namespaces": [
        "All_namespaces”
      ]
    }
}
  
  

```

The below example uses the `curl` utility, with the cookie obtained above for authorization, to send a JSON request.


```
$ curl -sS  -k -j -b ./PSM-cookie-jar.txt -X POST   \
    -H "Content-Type: application/json"             \
    -d '{ "meta": {"name": "DC-1-vCenter" }, "spec": { "type": "vcenter", "uri":  "dc-1-vcenter.local", "credentials": { "auth-type": "username-password", "username": "admin", "password": "xyz!"}, "manage-namespaces": [ "all_namespaces" ] } }' https://$PSMaddr/configs/orchestration/v1/orchestrator
  
  

```

Note that since the PSM GUI itself uses REST to communicate with the PSM, the <ins>API Capture</ins> facility can be very useful to observe how valid REST requests are made.
The “Orchestrator” section of the PSM GUI should now show that the request was successful.
For more details and examples of using the API, see the *Policy and Services Manager (PSM) REST API Getting Started Guide*.

