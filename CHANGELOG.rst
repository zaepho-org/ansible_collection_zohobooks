==============================
zaepho.ZohoBooks Release Notes
==============================

.. contents:: Topics

v0.2.0
======

Release Summary
---------------

Version 0.2.0 introduces the zohobooks_account_info module for querying account information,
removes Python 2.7 support, and modernizes the codebase with Python 3.6+ best practices.

Major Changes
-------------

- Added zohobooks_account_info module for retrieving chart of accounts information with support for filtering by name or ID.
- Added zohobooks_item module for managing Zoho Books items with support for create, update, delete, activate, and deactivate operations.
- Added zohobooks_item_info module for retrieving item information with support for filtering by name, ID, SKU, or status.
- Added zohobooks_vendor module for managing Zoho Books vendors with support for create, update, delete, activate, and deactivate operations.
- Added zohobooks_vendor_info module for retrieving vendor information with support for filtering by name, ID, or status.
- Dropped Python 2.7 support - minimum Python version is now 3.6.
- Item modules support inventory tracking with initial stock, reorder levels, and stock rate configuration.
- Refactored all modules to use modern Python f-strings instead of .format() for improved readability and performance.
- Updated minimum Ansible requirement to 2.16 or higher.
- Vendor modules support comprehensive contact information including billing addresses, payment terms, and custom fields.

Minor Changes
-------------

- Added Makefile with convenient targets for building, testing, and documentation tasks.
- Added TESTING.md guide with detailed instructions for running tests locally.
- Added comprehensive integration tests for vendor modules in tests/integration/targets/.
- Added comprehensive test.sh script that mirrors GitHub Actions CI workflow for local testing.
- Both item modules follow the same authentication and environment variable patterns as account modules.
- Both modules now consistently use f-strings for all string formatting operations.
- Both vendor modules follow the same authentication and environment variable patterns as other collection modules.
- Enhanced error handling in zohobooks_account module with better exception specificity (replaced bare except with Exception).
- Improved code quality with modern Python 3.6+ idioms and best practices.
- Item modules support mutually exclusive parameters for different query methods (name, item_id, sku).
- Updated README.md with quick testing commands and reference to testing guide.
- Updated documentation to clarify Python version requirements.
- Vendor modules support mutually exclusive parameters for different query methods (contact_name, contact_id).
- zohobooks_account_info module supports mutually exclusive parameters (account_name and account_id).
- zohobooks_item module provides comprehensive field support including rates, SKU, tax configuration, and account assignments.
- zohobooks_item module supports goods, services, and digital service product types.
- zohobooks_item_info module supports filtering items by status (Active, Inactive, All).
- zohobooks_vendor module provides support for payment terms configuration with customizable labels.
- zohobooks_vendor module supports both individual and business vendor types via vendor_sub_type parameter.
- zohobooks_vendor_info module supports filtering vendors by status (Active, Inactive, All).

Bugfixes
--------

- Fixed PEP8 E722 violation by replacing bare except clause with specific Exception type in zohobooks_account module.
- zohobooks_item_info - Fixed return value key from 'items' to 'zohobooks_items' to avoid conflict with Python dict method and enable dot notation access in Jinja templates.

New Modules
-----------

- zaepho.zohobooks.zohobooks_account_info - Retrieve ZohoBooks chart of accounts information.

v0.1.0
======

Release Summary
---------------

This is the initial release of the zaepho.zohobooks collection for Ansible.
This collection provides modules to interact with the Zoho Books API, enabling
automation of accounting and financial management tasks.

Major Changes
-------------

- Added zohobooks_account module for managing Zoho Books chart of accounts with support for create, update, and delete operations.
- Implemented authentication via environment variables (ZOHO_ORGANIZATION_ID, ZOHO_ACCESS_TOKEN, ZOHO_API_DOMAIN) and module parameters.
- Initial release of the zaepho.zohobooks collection (https://github.com/zaepho/ansible_collection_zohobooks).

Minor Changes
-------------

- Added check mode support for all modules.
- Added item_info module skeleton for retrieving item information from Zoho Books (in development).
- Support for idempotent operations in zohobooks_account module.
