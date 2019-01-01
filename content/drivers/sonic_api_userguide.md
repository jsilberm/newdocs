---
title: SONIC API Userguide
description: SONIC API Userguide
menu:
  docs:
    parent: "sonic"
    weight: 2
quicklinks:
weight: 1
draft: false
toc: true
---
![image alt text](/images/drivers/sonic/image_0.png)

# SONIC API User Guide

Version 0.2.0

Dec 30, 2018

 **Table of Contents** 

[[TOC]]

# Legal

All information in this document is provided on a non-disclosure basis.   Anyone reading this document implicitly agrees to be bound by Pensando Systems’ non-disclosure terms.

# Document Revision History

| Revision | Author | Date | Status and Description |
|----------|--------|------|------------------------|
| 0.1 | Roger | 2018-04-16 | Initial Version |
| 0.2 | Jeff | 2018-11-19 | Target for 11/30/18 deliverables. |
| 0.2.1 | Jeff | 2019-01-01 | Target for 1/2/19 deliverables |

# NAPLES Offload Engine Overview

## Introduction

Pensando NAPLES is a SmartNIC capable of handling both network traffic as well as providing hardware and CPU offload for Encryption/Decryption, Compression/Decompression, hash and checksum calculations, also known as accelerator services.  To access these hardware accelerator services Pensando has developed the SONIC kernel driver that provides APIs for interaction with the offload services on NAPLES. "offload services" are defined as service requests that interact with the offload engines.

This document is intended for software engineers who need an understanding of the Pensando SONIC kernel driver and API for writing software that interacts with the offload services. This document contains the information needed to get started using and interacting with the SONIC kernel driver and the different accelerator services.

## Prerequisites

If running on a FreeBSD-based kernel, this driver assumes that the kernel is compiled with COMPAT_LINUXKPI.  Instructions are included in **Appendix A** .

The SONIC driver also requires that PCI ARI is disabled in the running kernel.

To verify:



```
# sysctl -a | grep hw.pci.enable_ari
hw.pci.enable_ari: 0
```

If enable_ari is not set to zero, then please run the command below and reboot:



```
# Disable PCI ARI
echo hw.pci.enable_ari="0" >> /boot/loader.conf
```

## Offload Engines and Algorithms

The NAPLES adapter provides multiple offload engines and algorithms, as described by the block diagram and table below.   The block diagram shows all the offload engines connected to the Network-on-chip (NOC) switch.  Each accelerator engine supports data transfer bandwidth up to 100 Gbps.

These offload services can be chained and batched together as atomic operations, with all operations performed at wire speed.

### Block Diagram of the NAPLES Adapter, including all offload engines

![image alt text](/images/drivers/sonic/image_1.png)

### ![image alt text](/images/drivers/sonic/image_2.png)

### Table of Offload Engine Algorithms, supported by the current SONIC driver

| Offload  | Algorithm | Block Size | Info |
|----------|-----------|------------|------|
| Data<br>Compression | LZRW1A | up to 64K | Insertion of an 8-Byte Compression Header<br>(32-bit Checksum, 16-bit Length, 16-bit Version) |
| Data <br>Decompression | LZRW1A | up to 64K | Removal of the 8-Byte compression Header |
| Data<br>Encryption | XTS<br>256-bit | up to 4M<br>and multiple of 16 Bytes | IV = LBA # |
| Data<br>Decryption | XTS<br>256-bit | up to 4M<br>and multiple of 16 Bytes | IV = LBA # |
| Deduplication | SHA-256/512  | up to 4M |  |
| Checksum | M-Adler-32 |  |  |

 **Please note** : The NAPLES SONIC driver currently under development.   As a result, this document may describe features that have not currently been implemented.   As of 11/30/18, the NAPLES SONIC driver supports only Data Compression/Decompression offload services.

 **Please note:** The NAPLES adapter has additional offload engines that can be used by various networking protocols, that are currently not available in the SONIC driver.

# SONIC Driver Overview

## About the SONIC Driver

The Pensando SONIC Driver is a kernel device driver that supports all the necessary API’s needed to interact with the offload services.  As with any kernel module or device driver, the Pensando device driver can be loaded and unloaded to and from kernel at any time.  [  Ex:  kldload/kldunload (FreeBSD) or insmod/rmmod (Centos). ]

### Driver initialization

The SONIC driver needs to be loaded into the kernel with root privileges. Below are the commands,  depending on the specific OS:

| OS | Command |
|----|---------|
| FreeBSD | kldload sonic.ko |
| Linux | insmod sonic.ko |

### FreeBSD SONIC Driver Configuration

The SONIC Driver has the following tunable configuration variables that can set via " **kenv** ":

*  **compat.linuxkpi.sonic\_log\_level** ="N"  


Specifies the logging level for the SONIC Driver.   The standard Linux logging levels are used (See "Logging")

*  **compat.linuxkpi.sonic\_core\_count** ="N”  


Specifies the maximum number of cpu cores that can be used by the SONIC Driver.

WARNING: The value of **compat.linuxkpi.sonic\_core\_count** should generally not be used, except to set it to the actual number of system cores.

Ex:



```
# kenv compat.linuxkpi.sonic_log_level="7”
# kenv compat.linuxkpi.sonic_core_count="16”
```

### FreeBSD SONIC Driver Installation

The SONIC Driver is a binary file that is installed using the "kldload" command.  Ex:



```
# kldload sonic.ko 
```

# SONIC API Overview

## About the SONIC API

The SONIC driver is a kernel driver available in both FreeBSD and LINUX.

Please note that decompression and XTS decryption API has been optimized for low latency and is therefore synchronous in nature.  All other API’s are optimized for high throughput and are therefore asynchronous in nature.

## Architecture of the API

Host API is supported by P4 Programs and P4 DMA acting as an intermediary.

P4+ programs are controlling the Storage Accelerator. See diagram below.

![image alt text](/images/drivers/sonic/image_3.png)

## Service Requests

A service request includes a single data set to be processed by one or more offload engines.  A service request can be sent as a single request (one service) or chained (multiple services). Please see below.

### Single Service Request

A single request is used when a single dataset needs processing by a single service, such as encryption or compression. A single request invokes only a single accelerator service.

### Chaining Service Requests

Chaining is used when the same dataset needs to be processed by multiple services, for example Encryption, Compression and Checksum calculation.  The benefit with chaining is that a request is processed and forwarded among the different offload engines.  A chaining request is processed as a single atomic operation.

## Service Request Overview

Requests can be submitted to the offload engines in one of three different ways:  Synchronous, Asynchronous or Poll.

### Synchronous

Submitting a request synchronously will hold the calling thread until the result is returned.  Please note this could affect the overall performance and might not be the optimal way to submit the requests.   In general, synchronous requests should be avoided, except for data and meta-data updates that require the strictest serialization.

### Asynchronous

Submitting a request asynchronously will execute the request as a separate thread and will not hold the calling thread. Rather than using interrupts, the asynchronous API callback functions will return the result via a callback function provided at the time of submission.  Please note that the callbacks are invoked in the context of the submitting thread, and that the API does not allocate memory/buffers for the callback function.

### Poll

Submitting a request through the Poll function is similar to Asynchronous requests.  The Poll type also uses a callback function, but the user needs to poll to get the status of the request. Once the result is ready, the poll function will invoke the callback function.

Please note that the callbacks are invoked in the context of a polling thread, and that the API is not handling the creation and scheduling of these polling threads.

## Processing of the Submitted Request

Requests can be processed in Non-Batch or Batch mode.  Non-Bach requests contains one single service request (Single or chained).  Batch mode is used to submit multiple different service requests (Single or chained), to be processed in a single call.

### Non-Batch

Non-Batch is used to submit one dataset for processing, using one or more services (Single or Chained).

### Batch

Batching is way to submit multiple requests with different service requests (Single or Chained) all to be processed in a single call.  When submitting the request as a batch request, each service request is processed in parallel and atomicly, but the result is not returned until all processing of all data sets is completed.

# Service Request Types

## Non-Batched, Single Service Request

Below shows a single service compression request.

![image alt text](/images/drivers/sonic/image_4.png)

## Non-Batched, Chained Service Request

Below shows a chained request on a single data set that includes multiple different services (Compression, Hash and Encryption).

![image alt text](/images/drivers/sonic/image_5.png)

## Batched, Multiple Service Requests

Below shows three chained service requests that use multiple different offload services (Compression, Hash and Encryption) in various combinations. The batched request is considered complete once all processing of all service requests are completed.

![image alt text](/images/drivers/sonic/image_6.png)

## Submitting and Processing the Request

There are three different ways which service requests can be submitted, depending on the desired  interaction with the offload services and the processing of the results.  Requests can be submitted by one of three methods:  Synchronous, Asynchronous or Poll. The three different methods will determine how the request is submitted and how the caller is notified upon completion.   The different methods are described below.

### Synchronous (Non-Batched)

The **‘pnso\_submit\_request’** function will complete the request and return with the result.  The calling thread will wait synchronously for completion of the request. This request requires pointers to the request (\*req) and response (\*res) buffers.

![image alt text](/images/drivers/sonic/image_7.png)

![image alt text](/images/drivers/sonic/image_8.png)

| Type | API Function Call | Description |
|------|-------------------|-------------|
| Request + Flush | pnso\_submit\_request | Submit and process one request atomically.<br>(Chained or Non-Chained)<br><br>Note: Caller thread is blocked until the response is returned. |

### Synchronous (Batched)

The **‘pnso\_add\_to\_batch’** and **‘pnso\_flush\_batch’** functions will complete multiple batched requests and return with the batched result.  The calling thread will be waiting synchronously for the completion of all requests in the batch. Synchronous requests require pointers to the request (\*req) and response (\*res) buffers.

![image alt text](/images/drivers/sonic/image_9.png)

![image alt text](/images/drivers/sonic/image_10.png)

| Type | API Function Call | Description |
|------|-------------------|-------------|
| Request | pnso\_add\_to\_batch | Adds a request to batch buffer.<br>(Chained or Non-Chained) |
| Flush | pnso\_flush\_batch | Processes all of the requests in the batch buffer atomically. Responses are available once all requests has been processed.<br><br>Note: Caller thread is blocked until the response is returned. |

### Asynchronous (Non-Batched)

The **‘pnso\_submit\_request’** function returns immediately, and completes the request in the background before invoking a caller-provided callback function. In this request, pointers are provided for the request (\*req) and response (\*res) buffers, the callback function (cb\_func) and callback context (\*cb\_ctx).  Once the request has been completed, the callback function will be invoked, indicating that the result is ready for processing.

![image alt text](/images/drivers/sonic/image_11.png)

![image alt text](/images/drivers/sonic/image_12.png)

| Type | API Function Call | Description |
|------|-------------------|-------------|
| Request + Flush | pnso\_submit\_request | Submit and process one request atomically.<br>(Chained or Non-Chained)<br><br>Note: Caller thread continues to execute.  The response is returned by a caller-provided callback function. |

### Asynchronous (Batched)

The **‘pnso\_add\_to\_batch’** and **‘pnso\_flush\_batch’** functions return immediately. In this request,  pointers are provided for the requests (\*req) and response (\*res) buffers, the callback function (cb\_func) and callback context (\*cb\_ctx).  Once all the requests have been completed, the callback function will be invoked, indicating that the results are ready for processing.

![image alt text](/images/drivers/sonic/image_13.png)

![image alt text](/images/drivers/sonic/image_14.png)

| Type | API Function Call | Description |
|------|-------------------|-------------|
| Request | pnso\_add\_to\_batch | Adds a request to batch buffer.<br>(Chained or Non-Chained) |
| Flush | pnso\_flush\_batch | Processes all of the requests in the batch buffer atomically. Responses are available once all requests has been processed.<br><br>Note: Caller thread continues to execute.  The responses are returned by a caller-provided callback function. |

### Poll (Non-Batch)

The **‘pnso\_submit\_request’** function returns immediately.  The request is completed in the background before invoking a caller-provided callback function. In this request, pointers are  provided for the request (\*req) and response (\*res) buffers, and poll function (\*poll\_func) and opaque poll context (\*\*poll\_ctx).  Competition status is polled for, indicating that the result is ready for processing.  The poll is done through the API-provided **‘pnso\_poll\_fn’** polling function pointer, in combination with the API-provided **‘pnso\_poll\_ctx’** for the polling function.   The API provides both the polling function and the polling function context to use when calling the polling function.    The caller has the responsibility for maintaining the corresponding polling context for each outstanding poll request.

 **_Please note: The callback function is called AFTER a successful poll check call, please see below:_**


![image alt text](/images/drivers/sonic/image_15.png)

![image alt text](/images/drivers/sonic/image_16.png)

| Type | API Function Call | Description |
|------|-------------------|-------------|
| Request + Flush | pnso\_submit\_request | Submit and process one request atomically.<br>(Chained or Non-Chained)<br><br>Note: Caller thread continues to execute.  The response is returned by a caller-provided callback function AFTER the caller thread performs a poll check and the result is available. |
| Poll Check | pnso\_poll\_fn | Polling function to check for completion.  Context is provided by ‘pnso\_poll\_ctx’.<br> |

### Poll (Batched)

The **‘pnso\_add\_to\_batch’** and **‘pnso\_flush\_batch’** functions return immediately. In this request, pointers are provided for the request (\*req) and response (\*res) buffers, and poll function (\*poll\_func) and poll function context (\*\*poll\_ctx).   Both the (\*poll\_func) and the (\*\*poll\_ctx) are returned/provided by the API driver.  Completion status is polled for, indicating that  the result is ready for processing. The poll is done through the **‘pnso\_poll\_fn’** polling function pointer, in combination with the API-provided **‘pnso\_poll\_ctx’** for the polling function. The API provides both the polling function and the polling function context to use when calling the polling function.    The caller has the responsibility for maintaining the corresponding polling context for each outstanding poll request.

 **_Please note: The callback function is called AFTER a successful poll check call.  Please see below:_**


![image alt text](/images/drivers/sonic/image_17.png)

![image alt text](/images/drivers/sonic/image_18.png)

| Type | API Function Call | Description |
|------|-------------------|-------------|
| Request | pnso\_add\_to\_batch | Adds a request to batch buffer<br>(Chained or Non-Chained) |
| Flush | pnso\_flush\_batch | Processes all of the requests in the batch buffer atomically.  Responses are available once all requests have been processed.<br><br>Note: Caller thread continues to execute.  The response is returned by a caller-provided callback function AFTER the caller thread performs a poll check and the result is available. |
| Poll Check | pnso\_poll\_fn | Polling function to check for completion.  Context is provided by ‘pnso\_poll\_ctx’. |

# Using the Storage API

## Include Files

Callers of the SONIC API must include the following files:



```
#include "pnso_api.h"
```

## Memory Allocation and Ownership

Please note that all host memory needs to allocated outside the API.  The API assumes that the calling functions **must** provide pointers to allocated host memory.   The API does not allocate memory.

## Buffers and Lists

All buffers and buffer lists are passed using physical addresses to avoid virtual to physical address translation costs.

### Flat Buffer

The smallest unit of buffer is **‘pnso\_flat\_buffer’** , containing **‘len’** which is the length of the buffer in bytes, and **‘buf’** which is a pointer to a physical address where the data (buffer) resides.



```
struct pnso_flat_buffer {
    uint32_t len;
    uint64_t buf;
};
```

### Scatter Gather List (SGL)

The **‘pnso\_buffer\_list’** defines a scatter/gather buffer list.   This structure is used to represent a collection of physical memory buffers that are not contiguous. The **‘count’** specifies the numbers of buffers in the list and **‘buffers’** specifies an unbounded array of flat buffers as defined by **‘count** ’. The buffers are used for offload engine data requests and results.



```
struct pnso_buffer_list {
    uint32_t count;
    struct pnso_flat_buffer buffers[0];
};
```

### Flat Buffers and SGL Relationship

Below is a visualization of the **‘flat\_buffer’** and **‘buffer\_list’** relationship:

![image alt text](/images/drivers/sonic/image_19.png)

The image below is an example of a buffer\_list with 3 x flat\_buffer’s pointing to 3 different physical memory addresses where the buffers (data) reside.

![image alt text](/images/drivers/sonic/image_20.png)

## Initialization and Service Descriptors

Before any of the offload services can be invoked, certain initialization is required, depending on which accelerator is invoked.  Please see below:

* Driver Initialization  
* API Initialization  
* Offload service Initialization  
* Offload service description  
* Submit offload service request  
* Access and process the result  


### API initialization

API initialization is required before the offload services can be invoked. Initialization is done by invoking the **‘pnso\_init’** function.

The **‘pnso\_init’** expect to be passed initialization parameters for the offload services.  This is done through the struct **‘pnso\_init\_params’** .  The **‘pnso\_init’** function will return **‘PNSO\_OK’** indicating success, or **‘-EINVAL’** if invalid parameters where passed.

The function **‘pnso\_init’** is defined as follows:

 **pnso\_error\_t pnso\_init(struct pnso\_init\_params \*init\_params);** 

 **_Please note:_**
_Caller is responsible for allocation and deallocation of memory for input parameters._

The **‘** **_pnso\_init\_params_**
**’** represents the initialization parameters for Pensando offload services. It is a struct and is defined as follow:

* per\_core\_qdepth: Specifies the maximum number of parallel outstanding requests per host CPU core.  
* core\_count:  Specifies the number of CPU cores    
* block\_size: Specifies the native filesystem block size in bytes.  


```
struct pnso_init_params {
        uint16_t per_core_qdepth;
        uint16_t core_count;
        uint32_t block_size;
};
```



Setting the " **per\_core\_qdepth** " should aim to balance request concurrency with system memory use.  Setting the value too low may result in service request not being accepted by the API.   Setting the value too high may consume memory unnecessarily.

### Offload Service Initialization

#### Crypto Engine Initialization

The crypto accelerator service requires first registering the crypto key descriptor index, and Initialization Vector (IV).

XTS (XEX-based tweaked-codebook mode with ciphertext stealing) is a symmetric algorithm and requires a key, and a key index definition in the key index descriptor table.

The initialization is done by calling the **‘pnso\_set\_key\_dec\_idx’** function and set the key for data encryption and a key for the descriptor index, please see below:

*  **key1** : Specifies the key that will be used to encrypt the data  
*  **key2** : Specifies the key that will be used to encrypt initialization vector  
* key\_size: Specifies the size of the key in bytes -- 16 and 32 bytes for AES128 and AES256 respectively.  
*  **key\_idx** : Specifies the key index in the descriptor table.  


Return Value:

* PNSO\_OK - on success  
* -EINVAL - on invalid input parameters  


```
pnso_error_t pnso_set_key_desc_idx(const void *key1,
             	  const void *key2,
             	  uint32_t key_size, uint32_t key_idx);
```



 **_Please note:_**
_The caller is responsible for allocation/deallocation of memory for input parameters._

#### Compression Engine Initialization

Initialization of the compression accelerator requires registering a new header format, and adding a compression algorithm mapping.  The mapping is the Pensando compression algorithm number to the customer’s opaque algorithm identifier in the compression header.   This allows customers to have their own list mapped to potentially different Pensando capabilities.

The registration is done by calling the ‘ **pnso\_register\_compression\_header\_format** ’ function and providing the header format to be embedded at the beginning of the the compressed data.  Please see below:

*  **cp\_hdr\_fmt** : The header format to be embedded  
*  **hdr\_fmt\_idx** : Non-Zero index to uniquely identify the header format  


Return Value:

* PNSO\_OK - on success  
* -EINVAL - on invalid input parameters  


```
pnso_error_t pnso_register_compression_header_format(
        struct pnso_compression_header_format *cp_hdr_fmt,
        uint16_t hdr_fmt_idx);
```



Algorithm mapping is done by calling the **‘pnso\_add\_compression\_algo\_mapping** ’ function and providing the compression algorithm number (Please see the API reference for a complete list of algorithms supported), and the compression header algorithm number.  Please see below:

*  **pnso\_algo** : The compression algorithm number  
*  **header\_algo** : The compression header algorithm number  


Return Value:

* PNSO\_OK - on success  
* -EINVAL - on invalid input parameters  


```
pnso_error_t pnso_add_compression_algo_mapping(
        enum pnso_compression_type pnso_algo,
        uint32_t header_algo);
```



 **_Please Note:_**
_Caller is responsible for managing the hdr\_fmt\_idx space and allocation/deallocation of memory for input parameters_

### Offload Service Descriptors

Offload service requests require configuration of the service details.    This configuration is done through service descriptors " **pnso\_service\_request** “.   As mentioned earlier, it is possible to chain multiple accelerator requests through service chaining.   Chaining is done through a “svc[]" array.

A location must be provided for the result set through the " **pnso\_service\_result** " parameter.

Details for the different accelerator engines are provided below.

#### Crypto Engine

The crypto service is defined using the **‘pnso\_service’** .  Please note that it is a ‘union’, and for the crypto accelerator the **‘pnso\_crypto\_desc’** is used. The **‘pnso\_service’** is defined as follows:

*  **svc\_type** : specifies one of the enumerated values for the accelerator service type (for crypto, use the **pnso\_crypto\_desc** ).  
*  **rsvd** : specifies a 'reserved' field meant to be used by Pensando.  
*  **crypto\_desc** : struct that specifies the descriptor for encryption/decryption service.  


The other services in this struct are described together with the corresponding accelerator service in this document.



```
struct pnso_service {
    uint16_t svc_type;
    uint16_t rsvd;
    union {
        struct pnso_crypto_desc crypto_desc;
        struct pnso_compression_desc cp_desc;
        struct pnso_decompression_desc dc_desc;
        struct pnso_hash_desc hash_desc;
        struct pnso_checksum_desc chksum_desc;
        struct pnso_decompaction_desc decompact_desc;
    } u;
};
```

The **‘pnso\_crypto\_desc’** is the descriptor for encryption or decryption operation, it is a struct and is defined as follow:

*  **algo\_type** :  Specifies one of the enumerated values of the crypto type (i.e. the enum **pnso\_crypto\_type** .  See below).  
*  **rsvd** : Specifies a 'reserved' field meant to be used by Pensando.  
*  **key\_desc\_idx** : Specifies the key index in the descriptor table.  
*  **iv\_addr** : Specifies the physical address of the initialization vector.  


```
struct pnso_crypto_desc {
    uint16_t algo_type;
    uint16_t rsvd;
    uint32_t key_desc_idx;
    uint64_t iv_addr;
};
```



The **‘pnso\_crypto\_type’** is an enum and is defined as follow:



```
enum pnso_crypto_type {
    PNSO_CRYPTO_TYPE_NONE = 0,
    PNSO_CRYPTO_TYPE_XTS = 1,
    PNSO_CRYPTO_TYPE_MAX
};
```

This list allows capabilities to be extended with additional crypto types in future releases.   For a complete list, please refer to the API Reference Guide.   Currently, XTS is the only crypto service supported.

#### Compression/Decompression Engine

The compression service is defined using the **‘pnso\_service’** .  Please note that it is a ‘union’, and for the compression accelerator the **‘** **_pnso\_compression\_desc_**
**’** or ‘ **_pnso\_decompression\_desc_**
**’** are used. The **‘pnso\_service’** is defined as follows:

*  **svc\_type** : specifies one of the enumerated values for the accelerator service type (for compression/decompression it would be defined as either ‘pnso\_compression\_desc’ or ‘pnso\_decompression\_desc’).  
*  **rsvd** : specifies a 'reserved' field meant to be used by Pensando.  
*  **_cp\_desc/dc\_desc_**
: struct that specifies the descriptor for compression/decompression services.  


The other services in this struct are described together with the corresponding accelerator service in this document.



```
struct pnso_service {
    uint16_t svc_type;
    uint16_t rsvd;
    union {
        struct pnso_crypto_desc crypto_desc;
        struct pnso_compression_desc cp_desc;
        struct pnso_decompression_desc dc_desc;
        struct pnso_hash_desc hash_desc;
        struct pnso_checksum_desc chksum_desc;
        struct pnso_decompaction_desc decompact_desc;
    } u;
};
```

The **‘** **_pnso\_compression\_desc_**
**’** is the descriptor for compression operation.  It is a struct and defined as follow:

*  **algo\_type** :  Specifies one of the enumerated values of the compressor algorithm (i.e. **pnso\_compression\_type** ).  
*  **flags** : Specifies the following applicable descriptor flags to compression descriptor:  


| Flags | Description |
|-------|-------------|
| PNSO\_CP\_DFLAG\_ZERO\_PAD | Zero fill the compressed output buffer aligning to block size. |
| PNSO\_CP\_DFLAG\_INSERT\_HEADER<br> | Insert compression header defined by the format supplied in 'struct pnso\_init\_params'. |
| PNSO\_CP\_DFLAG\_BYPASS\_ONFAIL | Use the source buffer as input buffer to hash and/or checksum, services, when compression operation fails. This flag is effective only when compression, hash and/or checksum operation is requested. |

*  **threshold\_len** : specifies the expected compressed buffer length in bytes. (This is to instruct the compression operation, upon its completion, to compress the buffer to a length that must be less than or equal to 'threshold\_len').  
*  **hdr\_fmt\_idx** : specifies the index for the header format in the header format array.  
*  **hdr\_algo** : specifies the value for header field PNSO\_HDR\_FIELD\_TYPE\_ALGO (This is the same value that is registered in ‘ **pnso\_add\_compression\_algo\_mapping’** ).  


```
struct pnso_compression_desc {
    uint16_t algo_type;
    uint16_t flags;
    uint16_t threshold_len;
    uint16_t hdr_fmt_idx;
    uint32_t hdr_algo;
};
```



The **‘** **_pnso\_decompression\_desc_**
**’** is the descriptor for the compression operation.  It is a struct, defined as follows:

*  **algo\_type** : specifies one of the enumerated values of the compressor algorithm (i.e. **pnso\_compression\_type** ) for decompression.  
*  **flags** : specifies the following applicable descriptor flags to decompression descriptor:  


| Flags | Description |
|-------|-------------|
| PNSO\_DC\_DFLAG\_HEADER\_PRESENT | Indicates the compression header is present. |

*  **hdr\_fmt\_idx** : specifies the index for the header format in the header format array.  
*  **rsvd** : specifies a 'reserved' field meant to be used by Pensando.  


```
struct pnso_decompression_desc {
    uint16_t algo_type;
    uint16_t flags;
    uint16_t hdr_fmt_idx;
    uint16_t rsvd;
};
```



The **‘** **_pnso\_compression\_type_**
**’** is an enum and is defined as follows:



```
enum pnso_compression_type {
    PNSO_COMPRESSION_TYPE_NONE = 0,
    PNSO_COMPRESSION_TYPE_LZRW1A = 1,
    PNSO_COMPRESSION_TYPE_MAX
};
```

This list allows capabilities to be extended with additional crypto types in future releases.   For a complete list, please refer to the API Reference Guide.   Currently, LZRW1A is the only compression service supported.

#### Hash Engine

The hash service is defined using the **‘pnso\_service’** .  Please note that it is a ‘union’, and for the compression accelerator the **‘** **_pnso\_hash\_desc_**
**’** is used. The **‘pnso\_service’** is defined as follows:

*  **svc\_type** : specifies one of the enumerated values for the accelerator service type (for hash calculation it would be defined as **‘** **_pnso\_hash\_desc’_**
_._  
*  **rsvd** : specifies a 'reserved' field meant to be used by Pensando.  
*  **_hash\_desc_**
: struct that specifies the descriptor for data deduplication service.  


The other services in this struct are described together with the corresponding accelerator service in this document.



```
struct pnso_service {
    uint16_t svc_type;
    uint16_t rsvd;
    union {
        struct pnso_crypto_desc crypto_desc;
        struct pnso_compression_desc cp_desc;
        struct pnso_decompression_desc dc_desc;
        struct pnso_hash_desc hash_desc;
        struct pnso_checksum_desc chksum_desc;
        struct pnso_decompaction_desc decompact_desc;
    } u;
};
```

The **‘** **pnso\_hash\_desc’** is the descriptor for hash calculation operation.  It is a struct and defined as follow:

*  **algo\_type** :  Specifies one of the enumerated values of the hash algorithm (i.e. pnso\_hash\_type) for data deduplication.  
*  **flags** : specifies the following applicable descriptor flag(s) to hash descriptor:  


| Flags | Description |
|-------|-------------|
| PNSO\_HASH\_DFLAG\_PER\_BLOCK | Indicates to produce one hash per block.<br>When this flag is not specified, hash for the entire buffer will be produced. |



```
struct pnso_hash_desc {
    uint16_t algo_type;
    uint16_t flags;
};
```

The **_pnso\_hash\_type_**
is an enum and is defined as follow:



```
enum pnso_hash_type {
    PNSO_HASH_TYPE_NONE = 0,
    PNSO_HASH_TYPE_SHA2_512 = 1,
    PNSO_HASH_TYPE_SHA2_256 = 2,
    PNSO_HASH_TYPE_MAX
};
```

#### Checksum Engine

The checksum service is defined using the **‘pnso\_service’** .  Please note that it is a ‘union’, and for the checksum accelerator the **‘** **_pnso\_checksum\_desc_**
**’** is used. The **‘pnso\_service’** is defined as follows:

*  **svc\_type** : specifies one of the enumerated values for the accelerator service type (for hash calculation it would be defined as **‘** **_pnso\_checksum\_desc’_**
_._  
*  **rsvd** : specifies a 'reserved' field meant to be used by Pensando.  
*  **_chksum\_desc_**
: struct that specifies the descriptor for the checksum calculation service.  


The other services in this struct are described together with the corresponding accelerator service in this document.



```
struct pnso_service {
    uint16_t svc_type;
    uint16_t rsvd;
    union {
        struct pnso_crypto_desc crypto_desc;
        struct pnso_compression_desc cp_desc;
        struct pnso_decompression_desc dc_desc;
        struct pnso_hash_desc hash_desc;
        struct pnso_checksum_desc chksum_desc;
        struct pnso_decompaction_desc decompact_desc;
    } u;
};
```

The ‘ **_pnso\_checksum\_desc’_**
is the descriptor for checksum calculation operation.  It is a struct and defined as follow:

*  **algo\_type** :  Specifies one of the enumerated values of the checksum algorithm (i.e. **pnso\_chksum\_type** ).  
*  **flags** : Specifies the following applicable descriptor flag(s) to checksum descriptor:  


| Flags | Description |
|-------|-------------|
| PNSO\_CHKSUM\_DFLAG\_PER\_BLOCK | Indicates to produce one checksum per block. When this flag is not specified, a checksum for the entire buffer will be produced. |



```
struct pnso_checksum_desc {
    uint16_t algo_type;
    uint16_t flags;
};
```

### Submitting an Offload Service Request

The table below describes the **‘pnso\_submit\_request’** and the required parameters depending on request function:

| Param | Type | Sync | Async | Poll | Description |
|-------|------|------|-------|------|-------------|
| \*req | struct<br>pnso\_service\_request<br> | in | in | in | The set of service request structures to be used to submit the request |
| \*resp | struct pnso\_service\_result | in/out | in/out | in/out | The set of service result structures to report the status of each service within a request upon its completion<br> |
| cb\_func | typedef completion\_cb\_t<br> | NULL | valid | optional | The caller-supplied completion callback routine |
| \*cb\_ctx | Void \* | NULL | valid | optional | The caller-supplied callback context information |
| \*poll\_func | typedef \*pnso\_poll\_fn\_t<br> | NULL | NULL | valid | The polling function, which the caller will use to poll for completion of the request |
| \*\*poll\_ctx | void \*\* | NULL | NULL | valid | The context to use when calling the polling function |

The **‘cb\_func’** and ‘\* **cb\_ctx’** are both caller-defined.     ‘ **cb\_func’** is the function to call upon request completion, and "\* **cb\_ctx** " can be used as the user-supplied context to identify which outstanding request has completed.

Correspondingly, ‘\* **poll\_func’** and "\*\* **poll\_ctx** " are both API-defined and opaque from the caller perspective.   After submitting a poll request, the caller can poll for completion status by calling the **“\*poll\_func** ” while passing in the **“\*\*poll\_ctx** ” that corresponds to the given outstanding request.

 **_Please note:_**
_The caller is responsible for allocation/deallocation of memory for both input and output parameters.  Caller should keep the memory intact (ex: req/res) until the Pensando accelerator returns the result via completion callback._

### Access the Result

The **‘** **_pnso\_service\_result_**
**’** represents the result of the request upon completion for one or all services.  It is a struct and is defined as follow:

*  **err** : specifies the overall error code of the request. When set to '0', the request processing can be considered successful. Otherwise, one of the services in the request failed, and any output data should be discarded  
*  **num\_services** : specifies the number of services in the request  
*  **svc** : specifies an array of service status structures to report the status of each service within a request upon its completion  


 **_Please note:_**
_When_
**_'err'_**
_is set to_
**_'0'_**
_, the overall request processing can be considered successful.  Otherwise, one of the services in the request is failed, and any output data should be discarded._



```
struct pnso_service_result {
    pnso_error_t err;
    uint32_t num_services;
    struct pnso_service_status svc[0];
};
```

The "pnso\_service\_status" represents the result for an individual element within a “pnso\_service\_result” set.     It is a struct and is defined as follows:

*  **err** : specifies the overall error code of the request. When set to '0', the request processing can be considered successful. Otherwise, one of the services in the request failed, and any output data should be discarded  
*  **svc\_type** :  specifies the service request type, corresponding to one of the " **pnso\_service\_type"** enum values 
*  **rsvd\_1** :  reserved for use by Pensando.  Not to be used by caller.  
*  **u** :  descriptor for output/result locations of the service requests.  For the compression/decompression offload services (PNSO\_SVC\_TYPE\_COMPRESS or PNSO\_SVC\_TYPE\_DECOMPRESS) the **dst** structure will be used, representing a SGL for the service result set.  


 **Please note** :   The caller is responsible for allocating all memory that is referenced by the SGL (" **pnso\_buffer\_list** " and all associated buffers)



```
struct pnso_service_status {	pnso_error_t err;	uint16_t svc_type;	uint16_t rsvd_1;	union {		struct {			uint16_t num_tags;			uint16_t rsvd_2;			struct pnso_hash_tag *tags;		} hash;		struct {			uint16_t num_tags;			uint16_t rsvd_3;			struct pnso_chksum_tag *tags;		} chksum;		struct {			uint32_t data_len;			struct pnso_buffer_list *sgl;		} dst;	} u;}
```

# Coding Guidelines

* Avoid "Synchronous" service requests, except for the most critical meta-data updates that require the strictest serialization.   
* Chain service requests whenever possible, rather than manually creating multiple single service request pipelines in software.  
* Batched versus Non-Batched requests  


    * In general, use of batching and batched requests with larger batch size can increase aggregate throughput.  However, use of batched requests and large batch sizes will result in higher request latency.   The caller must establish guidelines and policies that are in-line with expected service level requirements.

* Synchronous, Asynchronous and Poll Requests  


    * Synchronous requests can be used when the lowest-possible latency is required

    * Asynchronous and Poll can be used when highest-possible throughput is required

* In general, the number of outstanding asynchronous requests per core should not exceed the pnso\_init "per\_core\_qdepth" at any given time  
* Input SGL buffers can be in 1 byte increments  
* Output SGL buffers must be in "block size" increments, where “block size” corresponds to the “block\_size” parameter given in the **_pnso\_init\_params_**
**__**
function (e.g. 4096).  


# Logging

All logging is done through printk() and can be seen through:

* The system console  
* syslog  
* dmesg  


Standard kernel logging levels are provided here for reference:

| Name | String | Description |
|------|--------|-------------|
| KERN\_EMERG | "0" | System is unusable |
| KERN\_ALERT | “1” | Action must be taken immediately |
| KERN\_CRIT | “2” | Critical conditions |
| KERN\_ERR | “3” | Error conditions |
| KERN\_WARNING | “4” | Warning conditions |
| KERN\_NOTICE | “5” | Normal but significant condition |
| KERN\_INFO | “6” | Informational |
| KERN\_DEBUG | “7” | Debug-level messages |

# Appendix A  :  Compiling with COMPAT_LINUXKPI

The SONIC driver requires a FreeBSD-based kernel to be compiled with COMPAT\_LINUXKPI.  Below are the instructions:



```
# Install git and vim
env ASSUME_ALWAYS_YES=YES pkg install git vim
 
# Clone FreeBSD source.
git clone [http://github.com/freebsd/freebsd](http://github.com/freebsd/freebsd) /usr/src
 
# Checkout 11.2 branch
git checkout releng/11.2
 
# Create User ntpd
echo "test" | pw useradd -n ntpd -m -g wheel -s /sbin/nologin -d /var/lib/ntpd -h –
 
# Create Group ntpd
pw groupadd ntpd
 
# Enable LINUXKPI option
cd /usr/src
echo "options COMPAT_LINUXKPI" >> sys/amd64/conf/GENERIC
 
# Enable OFED for RDMA
echo "options OFED" >> sys/amd64/conf/GENERIC
 
# Optional: Enable Journaling and Debugging Support.
echo "options GEOM_JOURNAL" >> sys/amd64/conf/GENERIC
echo "options KDB_UNATTENDED" >> sys/amd64/conf/GENERIC
echo "options KDB" >> sys/amd64/conf/GENERIC
echo "options DDB" >> sys/amd64/conf/GENERIC
 
# Build and Install the new Kernel
make buildworld buildkernel installworld installkernel
 
# Disable PCI ARI
echo hw.pci.enable_ari="0" >> /boot/loader.conf
 
# Optional: Enable Journaling and Disable background fsck
echo geom_journal_load="YES" >> /etc/rc.conf
echo fsck_y_enable="YES" >> /etc/rc.conf
echo background_fsck="NO" >> /etc/rc.conf
 
# Reboot
reboot
```



