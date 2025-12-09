# zaepho\.ZohoBooks Release Notes

**Topics**

- <a href="#v0-2-0">v0\.2\.0</a>
    - <a href="#release-summary">Release Summary</a>
    - <a href="#major-changes">Major Changes</a>
    - <a href="#minor-changes">Minor Changes</a>
    - <a href="#bugfixes">Bugfixes</a>
    - <a href="#new-modules">New Modules</a>
- <a href="#v0-1-0">v0\.1\.0</a>
    - <a href="#release-summary-1">Release Summary</a>
    - <a href="#major-changes-1">Major Changes</a>
    - <a href="#minor-changes-1">Minor Changes</a>

<a id="v0-2-0"></a>
## v0\.2\.0

<a id="release-summary"></a>
### Release Summary

Version 0\.2\.0 introduces the zohobooks\_account\_info module for querying account information\,
removes Python 2\.7 support\, and modernizes the codebase with Python 3\.6\+ best practices\.

<a id="major-changes"></a>
### Major Changes

* Added zohobooks\_account\_info module for retrieving chart of accounts information with support for filtering by name or ID\.
* Dropped Python 2\.7 support \- minimum Python version is now 3\.6\.
* Refactored all modules to use modern Python f\-strings instead of \.format\(\) for improved readability and performance\.
* Updated minimum Ansible requirement to 2\.16 or higher\.

<a id="minor-changes"></a>
### Minor Changes

* Both modules now consistently use f\-strings for all string formatting operations\.
* Enhanced error handling in zohobooks\_account module with better exception specificity \(replaced bare except with Exception\)\.
* Improved code quality with modern Python 3\.6\+ idioms and best practices\.
* Updated documentation to clarify Python version requirements\.
* zohobooks\_account\_info module supports mutually exclusive parameters \(account\_name and account\_id\)\.

<a id="bugfixes"></a>
### Bugfixes

* Fixed PEP8 E722 violation by replacing bare except clause with specific Exception type in zohobooks\_account module\.

<a id="new-modules"></a>
### New Modules

* zaepho\.zohobooks\.zohobooks\_account\_info \- Retrieve ZohoBooks chart of accounts information\.

<a id="v0-1-0"></a>
## v0\.1\.0

<a id="release-summary-1"></a>
### Release Summary

This is the initial release of the zaepho\.zohobooks collection for Ansible\.
This collection provides modules to interact with the Zoho Books API\, enabling
automation of accounting and financial management tasks\.

<a id="major-changes-1"></a>
### Major Changes

* Added zohobooks\_account module for managing Zoho Books chart of accounts with support for create\, update\, and delete operations\.
* Implemented authentication via environment variables \(ZOHO\_ORGANIZATION\_ID\, ZOHO\_ACCESS\_TOKEN\, ZOHO\_API\_DOMAIN\) and module parameters\.
* Initial release of the zaepho\.zohobooks collection \([https\://github\.com/zaepho/ansible\_collection\_zohobooks](https\://github\.com/zaepho/ansible\_collection\_zohobooks)\)\.

<a id="minor-changes-1"></a>
### Minor Changes

* Added check mode support for all modules\.
* Added item\_info module skeleton for retrieving item information from Zoho Books \(in development\)\.
* Support for idempotent operations in zohobooks\_account module\.
