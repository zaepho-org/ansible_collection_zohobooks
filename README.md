# Zoho Books Collection for Ansible

This Ansible collection provides modules to interact with the Zoho Books API, enabling automation of accounting and financial management tasks.

## Overview

The `zaepho.zohobooks` collection provides a simple and efficient way to automate interactions with Zoho Books, a cloud-based accounting software. This collection enables you to manage your Zoho Books resources through Ansible playbooks, making it easy to integrate accounting workflows into your automation pipelines.

## Code of Conduct

We follow the [Ansible Code of Conduct](https://docs.ansible.com/ansible/devel/community/code_of_conduct.html) in all our interactions within this project.

If you encounter abusive behavior, please refer to the [policy violations](https://docs.ansible.com/ansible/devel/community/code_of_conduct.html#policy-violations) section of the Code for information on how to raise a complaint.

## Features

Currently implemented modules:

- **zohobooks_account**: Manage Zoho Books chart of accounts
  - Create, update, and delete accounts
  - Support for various account types (bank, expense, income, etc.)
  - Idempotent operations
  - Environment variable support for credentials

- **zohobooks_account_info**: Retrieve chart of accounts information
  - Get all accounts or filter by name or ID
  - Read-only operations for account queries
  - Environment variable support for credentials

- **zohobooks_item**: Manage Zoho Books items
  - Create, update, and delete items
  - Support for goods, services, and digital services
  - Inventory tracking capabilities
  - Activate/deactivate items
  - Idempotent operations
  - Environment variable support for credentials

- **zohobooks_item_info**: Retrieve item information from Zoho Books
  - Get all items or filter by name, ID, or SKU
  - Filter items by status (active/inactive)
  - Read-only operations for item queries
  - Environment variable support for credentials

## Contributing to this collection

<!--Describe how the community can contribute to your collection. At a minimum, fill up and include the CONTRIBUTING.md file containing how and where users can create issues to report problems or request features for this collection. List contribution requirements, including preferred workflows and necessary testing, so you can benefit from community PRs. If you are following general Ansible contributor guidelines, you can link to - [Ansible Community Guide](https://docs.ansible.com/ansible/devel/community/index.html). List the current maintainers (contributors with write or higher access to the repository). The following can be included:-->

The content of this collection is made by people like you, a community of individuals collaborating on making the world better through developing automation software.

We are actively accepting new contributors and all types of contributions are very welcome.

Don't know how to start? Refer to the [Ansible community guide](https://docs.ansible.com/ansible/devel/community/index.html)!

Want to submit code changes? Take a look at the [Quick-start development guide](https://docs.ansible.com/ansible/devel/community/create_pr_quick_start.html).

We also use the following guidelines:

* [Collection review checklist](https://docs.ansible.com/ansible/devel/community/collection_contributors/collection_reviewing.html)
* [Ansible development guide](https://docs.ansible.com/ansible/devel/dev_guide/index.html)
* [Ansible collection development guide](https://docs.ansible.com/ansible/devel/dev_guide/developing_collections.html#contributing-to-collections)

## Collection maintenance

The current maintainers are listed in the [MAINTAINERS](MAINTAINERS) file. If you have questions or need help, feel free to mention them in the proposals.

To learn how to maintain/become a maintainer of this collection, refer to the [Maintainer guidelines](https://docs.ansible.com/ansible/devel/community/maintainers.html).

It is necessary for maintainers of this collection to be subscribed to:

* The collection itself (the `Watch` button -> `All Activity` in the upper right corner of the repository's homepage).
* The [news-for-maintainers repository](https://github.com/ansible-collections/news-for-maintainers).

They also should be subscribed to Ansible's [The Bullhorn newsletter](https://docs.ansible.com/ansible/devel/community/communication.html#the-bullhorn).

## Governance

<!--Describe how the collection is governed. Here can be the following text:-->

The process of decision making in this collection is based on discussing and finding consensus among participants.

Every voice is important. If you have something on your mind, create an issue or dedicated discussion and let's discuss it!

## Requirements

- Ansible 2.16 or higher
- Python 3.6 or higher (Python 2.7 is not supported)
- A Zoho Books account with API access
- Zoho Books API credentials:
  - Organization ID
  - Access Token (OAuth token)

## External requirements

This collection requires:
- Access to Zoho Books API (https://books.zoho.com)
- Valid Zoho Books API credentials
- Network connectivity to Zoho Books API endpoints

## Installation

### Installing from source

Currently, this collection is in development and not yet published to Ansible Galaxy. To install from source:

```bash
# Clone the repository
git clone https://github.com/zaepho/ansible_collection_zohobooks.git

# Build the collection
cd ansible_collection_zohobooks
ansible-galaxy collection build

# Install the built collection
ansible-galaxy collection install zaepho-zohobooks-0.1.0.tar.gz
```

### Installing from Ansible Galaxy (when available)

Once published, you'll be able to install with:

```bash
ansible-galaxy collection install zaepho.zohobooks
```

Or include it in a `requirements.yml` file:

```yaml
---
collections:
  - name: zaepho.zohobooks
    version: ">=0.1.0"
```

## Configuration

### Authentication

The collection supports authentication via parameters or environment variables:

**Environment Variables (recommended):**
```bash
export ZOHO_ORGANIZATION_ID="your_organization_id"
export ZOHO_ACCESS_TOKEN="your_access_token"
export ZOHO_API_DOMAIN="https://books.zoho.com"  # Optional, defaults to https://books.zoho.com
```

**Playbook Parameters:**
```yaml
- name: Example task
  zaepho.zohobooks.zohobooks_account:
    organization_id: "your_organization_id"
    access_token: "your_access_token"
    # ... other parameters
```

## Usage Examples

### Managing Chart of Accounts

```yaml
---
- name: Manage Zoho Books Accounts
  hosts: localhost
  tasks:
    - name: Create a bank account
      zaepho.zohobooks.zohobooks_account:
        account_name: "Business Checking"
        account_type: "bank"
        account_code: "1001"
        description: "Primary business checking account"
        state: present
      environment:
        ZOHO_ORGANIZATION_ID: "{{ zoho_org_id }}"
        ZOHO_ACCESS_TOKEN: "{{ zoho_token }}"

    - name: Create an expense account
      zaepho.zohobooks.zohobooks_account:
        account_name: "Office Supplies"
        account_type: "expense"
        account_code: "5001"
        state: present

    - name: Update an account description
      zaepho.zohobooks.zohobooks_account:
        account_name: "Business Checking"
        description: "Updated description for checking account"
        state: present

    - name: Delete an account
      zaepho.zohobooks.zohobooks_account:
        account_name: "Old Account"
        state: absent
```

### Querying Account Information

```yaml
---
- name: Get account information
  hosts: localhost
  tasks:
    - name: Get all accounts
      zaepho.zohobooks.zohobooks_account_info:
      environment:
        ZOHO_ORGANIZATION_ID: "{{ zoho_org_id }}"
        ZOHO_ACCESS_TOKEN: "{{ zoho_token }}"
      register: all_accounts

    - name: Get specific account by name
      zaepho.zohobooks.zohobooks_account_info:
        account_name: "Business Checking"
      environment:
        ZOHO_ORGANIZATION_ID: "{{ zoho_org_id }}"
        ZOHO_ACCESS_TOKEN: "{{ zoho_token }}"
      register: account

    - name: Get specific account by ID
      zaepho.zohobooks.zohobooks_account_info:
        account_id: "987654321"
      environment:
        ZOHO_ORGANIZATION_ID: "{{ zoho_org_id }}"
        ZOHO_ACCESS_TOKEN: "{{ zoho_token }}"
      register: account

    - name: Display account details
      debug:
        msg: "Found {{ account.count }} account(s)"
```

### Managing Items

```yaml
---
- name: Manage Zoho Books Items
  hosts: localhost
  tasks:
    - name: Create a goods item
      zaepho.zohobooks.zohobooks_item:
        name: "Hard Drive"
        rate: 120.00
        description: "500GB Hard Drive"
        sku: "HD-500GB-001"
        product_type: "goods"
        unit: "unit"
        state: present
      environment:
        ZOHO_ORGANIZATION_ID: "{{ zoho_org_id }}"
        ZOHO_ACCESS_TOKEN: "{{ zoho_token }}"

    - name: Create a service item
      zaepho.zohobooks.zohobooks_item:
        name: "Software License"
        rate: 99.99
        description: "Annual software license"
        product_type: "service"
        state: present

    - name: Create inventory item with stock tracking
      zaepho.zohobooks.zohobooks_item:
        name: "Widget A"
        rate: 25.00
        sku: "WGT-A-001"
        product_type: "goods"
        item_type: "inventory"
        track_inventory: true
        initial_stock: 100
        initial_stock_rate: 20.00
        reorder_level: 25
        state: present

    - name: Update an existing item
      zaepho.zohobooks.zohobooks_item:
        name: "Hard Drive"
        description: "Updated - 1TB Hard Drive"
        rate: 150.00
        state: present

    - name: Mark item as inactive
      zaepho.zohobooks.zohobooks_item:
        name: "Old Product"
        state: inactive

    - name: Delete an item
      zaepho.zohobooks.zohobooks_item:
        name: "Discontinued Item"
        state: absent
```

### Querying Items

```yaml
---
- name: Get item information
  hosts: localhost
  tasks:
    - name: Get all items
      zaepho.zohobooks.zohobooks_item_info:
      environment:
        ZOHO_ORGANIZATION_ID: "{{ zoho_org_id }}"
        ZOHO_ACCESS_TOKEN: "{{ zoho_token }}"
      register: all_items

    - name: Get item by name
      zaepho.zohobooks.zohobooks_item_info:
        name: "Hard Drive"
      environment:
        ZOHO_ORGANIZATION_ID: "{{ zoho_org_id }}"
        ZOHO_ACCESS_TOKEN: "{{ zoho_token }}"
      register: item

    - name: Get item by SKU
      zaepho.zohobooks.zohobooks_item_info:
        sku: "HD-500GB-001"
      environment:
        ZOHO_ORGANIZATION_ID: "{{ zoho_org_id }}"
        ZOHO_ACCESS_TOKEN: "{{ zoho_token }}"
      register: item

    - name: Get all active items
      zaepho.zohobooks.zohobooks_item_info:
        filter_by: "Status.Active"
      environment:
        ZOHO_ORGANIZATION_ID: "{{ zoho_org_id }}"
        ZOHO_ACCESS_TOKEN: "{{ zoho_token }}"
      register: active_items

    - name: Display item details
      debug:
        msg: "Found {{ item.count }} item(s)"
```

## Roadmap

**Current Version: 0.2.0** (Development)

### Completed
- `zohobooks_account` module for managing chart of accounts
- `zohobooks_account_info` module for retrieving account information
- `zohobooks_item` module for managing items (goods, services, digital services)
- `zohobooks_item_info` module for retrieving item information
- Basic authentication via environment variables and parameters
- Support for create, update, delete, and read operations
- Inventory tracking support for items
- Item activation/deactivation
- Modern Python 3.6+ support with f-strings and type hints ready

### Planned Features
- Additional modules for:
  - Customers
  - Invoices
  - Expenses
  - Bills
  - Payments
- Enhanced error handling and validation
- Comprehensive test coverage
- Documentation improvements

## Documentation and Resources

### Collection Documentation

Complete module documentation is available at:

- **[Collection Documentation](https://zaepho-org.github.io/ansible_collection_zohobooks/)** (GitHub Pages)
- Local documentation can be built using `docs/build.sh` (see [docs/README.md](docs/README.md))

### Zoho Books API
- [Zoho Books API Documentation](https://www.zoho.com/books/api/v3/)
- [Zoho Books Developer Console](https://api-console.zoho.com/)

### Ansible Resources
- [Ansible user guide](https://docs.ansible.com/ansible/devel/user_guide/index.html)
- [Ansible developer guide](https://docs.ansible.com/ansible/devel/dev_guide/index.html)
- [Ansible collections requirements](https://docs.ansible.com/ansible/devel/community/collection_contributors/collection_requirements.html)
- [Using Ansible collections](https://docs.ansible.com/ansible/devel/user_guide/collections_using.html)

## Licensing

This collection is licensed under the GNU General Public License v3.0 or later.

See [LICENSE](LICENSE) for the full license text.

## Author

Kevin Colby ([@zaepho](https://github.com/zaepho))

## AI Assistance Disclosure
Portions of this code were generated or refined with the assistance of generative AI tools. All AI-generated code was reviewed, tested, and modified by the project author(s) to ensure accuracy and functionality.