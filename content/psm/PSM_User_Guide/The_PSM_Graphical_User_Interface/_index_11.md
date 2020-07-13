---
title: "The PSM Graphical User Interface"
menu:
  docs:
    parent: "PSM Enterprise Edition User Guide"
weight: 12
categories: [psm]
toc: true
---
## The PSM Graphical User Interface
The PSM Graphical User Interface (GUI) is accessible via a web browser at `https://PSMaddr`, where `PSMaddr` corresponds to the IP address of any of the PSM cluster nodes. Figure 6 shows a configurable dashboard that offers an overview of the status of the Pensando Distributed Services Platform; the main menu on the left side provides access to the configuration of all supported features.
  
![image alt text](/images/PSM/PSM_User_Guide/The_PSM_Graphical_User_Interface/f0da5c86680b4e0e810bf5d815aa41f6c59d70bf.png)
<div style="text-align:center"><font size='2'>*Figure 6. Pensando PSM dashboard*
</font>

</div>
### Online Help
Detailed and comprehensive online help is offered in a context-sensitive manner for each page in the PSM GUI, accessible through the help icon in the upper right-hand corner:
<div style="text-align:center">The help icon is context sensitive, showing information related to the currently displayed GUI elements. For example, clicking the help icon while in the Workload overview will display descriptive help and examples on how to create a Workload object, as shown in Figure 7.  Similarly, clicking the help icon while in the Monitoring -> Alerts and Events view will show help on configuring Alert Policies.
</div>
  
![image alt text](/images/PSM/PSM_User_Guide/The_PSM_Graphical_User_Interface/a391be1fee3639945ebd8c7245d97894544153a9.png)
<div style="text-align:center"><font size='2'>*Figure 7. Example of PSM help*
</font> 

</div>Online Help windows can be easily undocked, redocked, resized, or closed.
Online Help has its own presentation context, so it does not need to be closed prior to subsequent operations; selecting different items from the left-hand-side Navigation pane will automatically display the corresponding Online Help information.
### Searching
The easy-to-use search facility is accessed from the search bar at the top of the screen.
  
![image alt text](/images/PSM/PSM_User_Guide/The_PSM_Graphical_User_Interface/0c817f466d532b910771389c3daab4701faf2935.png)<div style="text-align:center">
<font size='2'>*Figure 8. PSM search facility*
</font>

</div>In the example in Figure 8 above, doing a free form text search for the string “ae-s7” shows a summary of the various objects where that string appears, along with a count of the number of occurrences for each object type.
  
![image alt text](/images/PSM/PSM_User_Guide/The_PSM_Graphical_User_Interface/0c0c898bff294494f89bb75d83a7a4de1e186e6a.png)<div style="text-align:center">
*Figure 9.* *Accessing Advanced Search*
</div>Clicking on the downward arrow on the right hand side of the text box (shown in Figure 9 above) gives access to the Advanced Search capability shown in Figure 10, where users can search based on object Category, Kind or Tag (arbitrary labels associated to objects):
  
![image alt text](/images/PSM/PSM_User_Guide/The_PSM_Graphical_User_Interface/cc9ef840cc05e16825c2a127225e2880b24075b6.png)
<div style="text-align:center"><font size='2'>*Figure 10. Advanced Search*
</font>


</div>All the keywords used in Advanced Search can also be typed directly into the search bar to avoid having to bring up the Advanced Search tab.
### Global Icons
The GUI makes use of common/global icons for many actions, regardless of context, such as “Edit” or “Delete”, which can be used to edit fields, add labels, or delete objects such as “Host”, “DSC”, and “Network Interface”, as shown in Figure 11 :
  
![image alt text](/images/PSM/PSM_User_Guide/The_PSM_Graphical_User_Interface/712d177b09f9d571ea25d0235cff49d2cfb1a961.png)<div style="text-align:center"><font size='2'>
</font>

  
![image alt text](/images/PSM/PSM_User_Guide/The_PSM_Graphical_User_Interface/03017ea8c278ee0b6210812d41a947509f1f0d03.png)</div>
<div style="text-align:center"><font size='2'>*Figure 11. Edit and Delete icons*
</font>

</div>Many of the tables displayed in the GUI can be exported as CSV or JSON text files, as shown in Figure 12:
  
![image alt text](/images/PSM/PSM_User_Guide/The_PSM_Graphical_User_Interface/4310a830292dba3f8182bac18de8517dbccdd6a5.png)
  
![image alt text](/images/PSM/PSM_User_Guide/The_PSM_Graphical_User_Interface/6012cea6be19bedcdb5639ee8bfae97d284661e1.png)
<div style="text-align:center"><font size='2'>*Figure 12. Example of how a table can be exported in CSV or JSON format*
</font>

</div>
#### Server Certificate
By default, a self-signed certificate is created by the PSM during installation, and is used to authenticate connections to the browser-based GUI or REST clients. Users may instead provide a custom key and certificate to the PSM, to be used instead of the default self-signed one. If the root Certification Authority (CA) of the signer of such certificate is included in either the browser or the client hosts’ trusted root CA certificate list, warning messages related to the certificate validity will no longer be shown when accessing the PSM cluster login page.
The two supported encoded key formats are RSA and ECDSA. To change the PSM certificate, click "Admin" --> "Server Certificate". On the top right hand side, click  "UPDATE". Enter the key and certificate in Privacy Enhanced Mail (PEM) format and then click "Upload" to apply the change, as shown in Figure 13.
***Note:*** *this action will not disrupt existing connections, even if they were established with the previous certificate.*

  
![image alt text](/images/PSM/PSM_User_Guide/The_PSM_Graphical_User_Interface/3c02459f0645874e12653e673ecdd8fd63544a6c.png)<div style="text-align:center">
<font size='2'>*Figure*
</font>
 <font size='2'>*13. Changing the PSM server certificate*
</font>

</div>
#### API Capture
Users of the PSM’s REST API for external integration can take advantage of the fact that the PSM GUI itself uses this API, to see examples of it in use. REST API calls sent from the GUI to the PSM as it implements the configurations created by the user can be displayed using the API Capture feature.
When the API Capture menu item is selected, a view as shown in Figure 14 appears. Use this screen to browse sample API calls (in the API Capture tab) or a live capture of APIs generated while navigating the GUI (in the Live API Capture tab).
The live capture tool is per GUI session; large responses are trimmed down to two records to present the look and feel of the response, rather than the entire response.

<div style="text-align:center"><font size='2'>
</font>

  
![image alt text](/images/PSM/PSM_User_Guide/The_PSM_Graphical_User_Interface/6d25e59f746c98d981bd52f35c9e0d3a1cb7aa78.png)
<font size='2'>*Figure 14. Examples of captured REST API calls*
</font>

</div>
### Online Documentation
The PSM Reference guide is provided in online format, and included within the PSM itself. The online documentation can be accessed at `https://PSMaddr/docs` , where `PSMaddr` corresponds to the PSM cluster address.
