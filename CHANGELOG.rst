==============================
zaepho.ZohoBooks Release Notes
==============================

.. contents:: Topics

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
