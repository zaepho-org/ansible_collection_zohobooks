# zaepho\.ZohoBooks Release Notes

**Topics**

- <a href="#v0-1-0">v0\.1\.0</a>
    - <a href="#release-summary">Release Summary</a>
    - <a href="#major-changes">Major Changes</a>
    - <a href="#minor-changes">Minor Changes</a>

<a id="v0-1-0"></a>
## v0\.1\.0

<a id="release-summary"></a>
### Release Summary

This is the initial release of the zaepho\.zohobooks collection for Ansible\.
This collection provides modules to interact with the Zoho Books API\, enabling
automation of accounting and financial management tasks\.

<a id="major-changes"></a>
### Major Changes

* Added zohobooks\_account module for managing Zoho Books chart of accounts with support for create\, update\, and delete operations\.
* Implemented authentication via environment variables \(ZOHO\_ORGANIZATION\_ID\, ZOHO\_ACCESS\_TOKEN\, ZOHO\_API\_DOMAIN\) and module parameters\.
* Initial release of the zaepho\.zohobooks collection \([https\://github\.com/zaepho/ansible\_collection\_zohobooks](https\://github\.com/zaepho/ansible\_collection\_zohobooks)\)\.

<a id="minor-changes"></a>
### Minor Changes

* Added check mode support for all modules\.
* Added item\_info module skeleton for retrieving item information from Zoho Books \(in development\)\.
* Support for idempotent operations in zohobooks\_account module\.
