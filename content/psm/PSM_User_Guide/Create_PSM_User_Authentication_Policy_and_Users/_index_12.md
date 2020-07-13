---
title: "Create PSM User Authentication Policy and Users"
menu:
  docs:
    parent: "PSM Enterprise Edition User Guide"
weight: 13
categories: [psm]
toc: true
---
## Create PSM User Authentication Policy and Users
Each PSM will have one or more users defined. Users are assigned roles granting them privileges depending on the tasks they need to perform; during the installation process, an initial user, named `admin`  with the password `Pensando0$` , is created with full administrator privileges.
A different name for the initial user as well as a custom password can be provided as parameters to the  `bootstrap_PSM.py` utility used to initialize the cluster, as described in the section “<ins>Bootstrap The PSM Cluster</ins>”. 
### User Authentication Policy
The PSM supports Local (i.e., username and password), LDAP and RADIUS Authenticators, as shown in Figure 15. Creation of authenticators should be done early in the system setup process. Once two or more authenticators are created, they can be re-ordered dynamically to specify the priority with which they should be applied.
Please refer to the “PSM LDAP Configuration Guide” for specific configuration details.
  
![image alt text](/images/PSM/PSM_User_Guide/Create_PSM_User_Authentication_Policy_and_Users/771ce66ea65ace4fdbf3990ccd106b7c20ca8728.png)

<div style="text-align:center"><font size='2'>*Figure 15. Managing user authentication policy*
</font>

</div>To create an LDAP Authenticator, click the “CREATE LDAP AUTHENTICATOR” button. Active Directory (AD) and OpenLDAP providers are supported.
Configure *Credentials*, *Scope* (which controls user and group entry search) and *Attribute* mapping (which contains the name of the attributes that should be extracted from the LDAP entry of the user, such as full name and email address) as appropriate, ensuring all required (*) fields are properly filled, as in Figure 16:

  
![image alt text](/images/PSM/PSM_User_Guide/Create_PSM_User_Authentication_Policy_and_Users/4ca518d0f15390010394d327785b3d3969652c11.png)<div style="text-align:center">
<font size='2'>*Figure 16. LDAP configuration*
</font>

</div>
Once saved, the values should be visible, as shown in Figure 17. The order of the various authenticators can be changed (using the small arrows on the right hand side).
  
![image alt text](/images/PSM/PSM_User_Guide/Create_PSM_User_Authentication_Policy_and_Users/28655fdd0bf6ae298d317221d05c74361ad9d669.png)<div style="text-align:center">
<font size='2'>*Figure 17. Changing authentication order*
</font>

  
</div>
### Role Based Access Control (RBAC)
The User Management menu gives access to the RBAC Management screen, shown in Figure 18, which allows management of either users or roles, or the association of users to roles (“rolebinding”) based on the selection made with the drop-down menu on the top right corner of the view. The recommended User Management sequence consists of first creating one or more Roles, followed by one or more Users, and then creating the corresponding associations (rolebinding).
  
![image alt text](/images/PSM/PSM_User_Guide/Create_PSM_User_Authentication_Policy_and_Users/8ae2fe77052e06139f8b7f6476b0983de4b40f7f.png)<div style="text-align:center">
<font size='2'>*Figure 18.*
</font> 
<font size='2'>*RBAC management*
</font>

</div>

#### Roles
*Roles* are created to control access to classes of features by sets of users. Roles can have scope over various objects, which are grouped by the PSM in the categories:

- Auth
- Cluster
- Diagnostics
- Monitoring
- Network
- Objstore
- Rollout
- Security
- Staging
- Workload
  

  
![image alt text](/images/PSM/PSM_User_Guide/Create_PSM_User_Authentication_Policy_and_Users/5ba28d057de4b4b76d3172883e2945553f33347f.png)<div style="text-align:center">
<font size='2'>*Figure 19. RBAC roles*
</font>

</div> 
As shown in Figure 19 above, for a given Group, various kinds of management aspects are available. Once one is selected, access to actions can be added or removed, as shown in Figure 20:

- Create
- Delete
- Read
- Update
  

  
![image alt text](/images/PSM/PSM_User_Guide/Create_PSM_User_Authentication_Policy_and_Users/36ba0ba1cf4376939ab4016a90995337c95bd60c.png)<div style="text-align:center">
<font size='2'>*Figure 20. Assigning actions to a group*
</font>

</div>
#### Role Binding
Once a Role is created, a corresponding rolebinding is automatically created. Rolebindings allow users to be flexibly mapped to various sets of roles. Figure 21 shows the view to modify a “rolebinding” that allows to associate any of the users defined in the system (in the left list titled Available) with the Role specified in the form. Users successfully associated with the Role appear in the right list titled Selected.
The rolebinding can be also specified using the “Group” attribute value configured in the LDAP authenticator “Attribute Mapping” section and retrieved from the LDAP user entry. This is the distinguished name of the LDAP group entry a user belongs to
  
![image alt text](/images/PSM/PSM_User_Guide/Create_PSM_User_Authentication_Policy_and_Users/1eb943a427507f388f3a96fc72c547681e6065ff.png)<div style="text-align:center">
<font size='2'>*Figure 21. Rolebinding*
</font>

</div>
