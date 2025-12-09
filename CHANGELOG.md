# zaepho\.ZohoBooks Release Notes

**Topics**

- <a href="#v0-2-1">v0\.2\.1</a>
    - <a href="#release-summary">Release Summary</a>
    - <a href="#minor-changes">Minor Changes</a>
- <a href="#v0-2-0">v0\.2\.0</a>
    - <a href="#release-summary-1">Release Summary</a>
    - <a href="#major-changes">Major Changes</a>
    - <a href="#minor-changes-1">Minor Changes</a>
    - <a href="#bugfixes">Bugfixes</a>
    - <a href="#new-modules">New Modules</a>
- <a href="#v0-1-0">v0\.1\.0</a>
    - <a href="#release-summary-2">Release Summary</a>
    - <a href="#major-changes-1">Major Changes</a>
    - <a href="#minor-changes-2">Minor Changes</a>

<a id="v0-2-1"></a>
## v0\.2\.1

<a id="release-summary"></a>
### Release Summary

Automated publishing to Galaxy

<a id="minor-changes"></a>
### Minor Changes

* Implemented a Github CI/CD release pipeline to publish to Galaxy

<a id="v0-2-0"></a>
## v0\.2\.0

<a id="release-summary-1"></a>
### Release Summary

Version 0\.2\.0 introduces the zohobooks\_account\_info module for querying account information\,
removes Python 2\.7 support\, and modernizes the codebase with Python 3\.6\+ best practices\.

<a id="major-changes"></a>
### Major Changes

* Added zohobooks\_account\_info module for retrieving chart of accounts information with support for filtering by name or ID\.
* Added zohobooks\_item module for managing Zoho Books items with support for create\, update\, delete\, activate\, and deactivate operations\.
* Added zohobooks\_item\_info module for retrieving item information with support for filtering by name\, ID\, SKU\, or status\.
* Added zohobooks\_vendor module for managing Zoho Books vendors with support for create\, update\, delete\, activate\, and deactivate operations\.
* Added zohobooks\_vendor\_info module for retrieving vendor information with support for filtering by name\, ID\, or status\.
* Dropped Python 2\.7 support \- minimum Python version is now 3\.6\.
* Item modules support inventory tracking with initial stock\, reorder levels\, and stock rate configuration\.
* Refactored all modules to use modern Python f\-strings instead of \.format\(\) for improved readability and performance\.
* Updated minimum Ansible requirement to 2\.16 or higher\.
* Vendor modules support comprehensive contact information including billing addresses\, payment terms\, and custom fields\.

<a id="minor-changes-1"></a>
### Minor Changes

* Added Makefile with convenient targets for building\, testing\, and documentation tasks\.
* Added TESTING\.md guide with detailed instructions for running tests locally\.
* Added comprehensive integration tests for vendor modules in tests/integration/targets/\.
* Added comprehensive test\.sh script that mirrors GitHub Actions CI workflow for local testing\.
* Both item modules follow the same authentication and environment variable patterns as account modules\.
* Both modules now consistently use f\-strings for all string formatting operations\.
* Both vendor modules follow the same authentication and environment variable patterns as other collection modules\.
* Enhanced error handling in zohobooks\_account module with better exception specificity \(replaced bare except with Exception\)\.
* Improved code quality with modern Python 3\.6\+ idioms and best practices\.
* Item modules support mutually exclusive parameters for different query methods \(name\, item\_id\, sku\)\.
* Updated README\.md with quick testing commands and reference to testing guide\.
* Updated documentation to clarify Python version requirements\.
* Vendor modules support mutually exclusive parameters for different query methods \(contact\_name\, contact\_id\)\.
* zohobooks\_account\_info module supports mutually exclusive parameters \(account\_name and account\_id\)\.
* zohobooks\_item module provides comprehensive field support including rates\, SKU\, tax configuration\, and account assignments\.
* zohobooks\_item module supports goods\, services\, and digital service product types\.
* zohobooks\_item\_info module supports filtering items by status \(Active\, Inactive\, All\)\.
* zohobooks\_vendor module provides support for payment terms configuration with customizable labels\.
* zohobooks\_vendor module supports both individual and business vendor types via vendor\_sub\_type parameter\.
* zohobooks\_vendor\_info module supports filtering vendors by status \(Active\, Inactive\, All\)\.

<a id="bugfixes"></a>
### Bugfixes

* Fixed PEP8 E722 violation by replacing bare except clause with specific Exception type in zohobooks\_account module\.
* zohobooks\_item\_info \- Fixed return value key from \'items\' to \'zohobooks\_items\' to avoid conflict with Python dict method and enable dot notation access in Jinja templates\.

<a id="new-modules"></a>
### New Modules

* zaepho\.zohobooks\.zohobooks\_account\_info \- Retrieve ZohoBooks chart of accounts information\.

<a id="v0-1-0"></a>
## v0\.1\.0

<a id="release-summary-2"></a>
### Release Summary

This is the initial release of the zaepho\.zohobooks collection for Ansible\.
This collection provides modules to interact with the Zoho Books API\, enabling
automation of accounting and financial management tasks\.

<a id="major-changes-1"></a>
### Major Changes

* Added zohobooks\_account module for managing Zoho Books chart of accounts with support for create\, update\, and delete operations\.
* Implemented authentication via environment variables \(ZOHO\_ORGANIZATION\_ID\, ZOHO\_ACCESS\_TOKEN\, ZOHO\_API\_DOMAIN\) and module parameters\.
* Initial release of the zaepho\.zohobooks collection \([https\://github\.com/zaepho/ansible\_collection\_zohobooks](https\://github\.com/zaepho/ansible\_collection\_zohobooks)\)\.

<a id="minor-changes-2"></a>
### Minor Changes

* Added check mode support for all modules\.
* Added item\_info module skeleton for retrieving item information from Zoho Books \(in development\)\.
* Support for idempotent operations in zohobooks\_account module\.
