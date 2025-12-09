#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: zohobooks_item
short_description: Manage ZohoBooks items
version_added: "0.2.0"
description:
    - Create, update, or delete items in ZohoBooks
    - Idempotent operations based on item name
options:
    organization_id:
        description:
            - ZohoBooks organization ID
            - Can also be set via ZOHO_ORGANIZATION_ID environment variable
        required: false
        type: str
    access_token:
        description:
            - ZohoBooks API access token
            - Can also be set via ZOHO_ACCESS_TOKEN environment variable
        required: false
        type: str
    name:
        description:
            - Name of the item
        required: true
        type: str
    rate:
        description:
            - Rate/price of the item
        required: false
        type: float
    description:
        description:
            - Description of the item
        required: false
        type: str
    sku:
        description:
            - Stock Keeping Unit (SKU) - must be unique
        required: false
        type: str
    product_type:
        description:
            - Type of product
        required: false
        type: str
        choices:
            - goods
            - service
            - digital_service
    unit:
        description:
            - Unit of measurement
        required: false
        type: str
    tax_id:
        description:
            - Tax ID to apply to the item
        required: false
        type: str
    tax_percentage:
        description:
            - Tax percentage to apply
        required: false
        type: float
    purchase_rate:
        description:
            - Purchase rate of the item
        required: false
        type: float
    purchase_account_id:
        description:
            - Account ID for purchases
        required: false
        type: str
    account_id:
        description:
            - Income/Sales account ID
        required: false
        type: str
    inventory_account_id:
        description:
            - Inventory account ID
        required: false
        type: str
    item_type:
        description:
            - Type of item (inventory or non-inventory)
        required: false
        type: str
        choices:
            - inventory
            - non_inventory
    track_inventory:
        description:
            - Whether to track inventory for this item
        required: false
        type: bool
        default: false
    initial_stock:
        description:
            - Initial stock quantity
        required: false
        type: float
    initial_stock_rate:
        description:
            - Rate of initial stock
        required: false
        type: float
    reorder_level:
        description:
            - Reorder level for inventory
        required: false
        type: float
    state:
        description:
            - Desired state of the item
        required: false
        type: str
        choices: ['present', 'absent', 'active', 'inactive']
        default: 'present'
    api_domain:
        description:
            - ZohoBooks API domain
            - Can also be set via ZOHO_API_DOMAIN environment variable
        required: false
        type: str
        default: 'https://books.zoho.com'
author:
    - Kevin Colby (@zaepho)
'''

EXAMPLES = r'''
- name: Create a goods item (using explicit parameters)
  zohobooks_item:
    organization_id: "123456789"
    access_token: "{{ zoho_access_token }}"
    name: "Hard Drive"
    rate: 120.00
    description: "500GB Hard Drive"
    sku: "HD-500GB-001"
    product_type: "goods"
    unit: "unit"
    state: present

- name: Create item using environment variables
  zohobooks_item:
    name: "Software License"
    rate: 99.99
    description: "Annual software license"
    product_type: "service"
    state: present
  environment:
    ZOHO_ORGANIZATION_ID: "123456789"
    ZOHO_ACCESS_TOKEN: "your_access_token"
    ZOHO_API_DOMAIN: "https://books.zoho.com"

- name: Create inventory item with initial stock
  zohobooks_item:
    organization_id: "123456789"
    access_token: "{{ zoho_access_token }}"
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
  zohobooks_item:
    organization_id: "123456789"
    access_token: "{{ zoho_access_token }}"
    name: "Hard Drive"
    description: "Updated description - 1TB Hard Drive"
    rate: 150.00
    state: present

- name: Mark item as inactive
  zohobooks_item:
    organization_id: "123456789"
    access_token: "{{ zoho_access_token }}"
    name: "Old Product"
    state: inactive

- name: Mark item as active
  zohobooks_item:
    organization_id: "123456789"
    access_token: "{{ zoho_access_token }}"
    name: "Seasonal Product"
    state: active

- name: Delete an item
  zohobooks_item:
    organization_id: "123456789"
    access_token: "{{ zoho_access_token }}"
    name: "Discontinued Item"
    state: absent
'''

RETURN = r'''
item:
    description: Item details
    returned: when state is present, active, or inactive
    type: dict
    sample:
        item_id: "123456789"
        name: "Hard Drive"
        rate: 120.00
        description: "500GB Hard Drive"
        sku: "HD-500GB-001"
        product_type: "goods"
        status: "active"
changed:
    description: Whether the item was changed
    returned: always
    type: bool
msg:
    description: Information about the operation
    returned: always
    type: str
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import fetch_url
import json
import os


class ZohoBooksItem:
    def __init__(self, module):
        self.module = module
        self.org_id = module.params['organization_id']
        self.token = module.params['access_token']
        self.api_domain = module.params['api_domain']
        self.base_url = f"{self.api_domain}/api/v3"

    def _make_request(self, endpoint, method='GET', data=None):
        """Make HTTP request to ZohoBooks API"""
        url = f"{self.base_url}/{endpoint}"
        headers = {
            'Authorization': f'Zoho-oauthtoken {self.token}',
            'Content-Type': 'application/json'
        }

        params = {'organization_id': self.org_id}
        if '?' in url:
            url += '&' + '&'.join([f"{k}={v}" for k, v in params.items()])
        else:
            url += '?' + '&'.join([f"{k}={v}" for k, v in params.items()])

        body = json.dumps(data) if data else None

        resp, info = fetch_url(
            self.module,
            url,
            method=method,
            data=body,
            headers=headers
        )

        if info['status'] not in [200, 201]:
            error_msg = f"API request failed: {info['status']}"
            if resp:
                try:
                    error_data = json.loads(resp.read())
                    error_msg += f" - {error_data.get('message', '')}"
                except Exception:
                    pass
            self.module.fail_json(msg=error_msg, status=info['status'])

        if resp:
            return json.loads(resp.read())
        return {}

    def get_item_by_name(self, item_name):
        """Find item by name"""
        response = self._make_request('items')

        if response.get('code') == 0:
            items = response.get('items', [])
            for item in items:
                if item.get('name') == item_name:
                    return item
        return None

    def create_item(self, params):
        """Create a new item"""
        data = {
            'name': params['name']
        }

        # Add optional fields if provided
        if params.get('rate') is not None:
            data['rate'] = params['rate']
        if params.get('description'):
            data['description'] = params['description']
        if params.get('sku'):
            data['sku'] = params['sku']
        if params.get('product_type'):
            data['product_type'] = params['product_type']
        if params.get('unit'):
            data['unit'] = params['unit']
        if params.get('tax_id'):
            data['tax_id'] = params['tax_id']
        if params.get('tax_percentage') is not None:
            data['tax_percentage'] = params['tax_percentage']
        if params.get('purchase_rate') is not None:
            data['purchase_rate'] = params['purchase_rate']
        if params.get('purchase_account_id'):
            data['purchase_account_id'] = params['purchase_account_id']
        if params.get('account_id'):
            data['account_id'] = params['account_id']
        if params.get('inventory_account_id'):
            data['inventory_account_id'] = params['inventory_account_id']
        if params.get('item_type'):
            data['item_type'] = params['item_type']
        if params.get('track_inventory') is not None:
            data['track_inventory'] = params['track_inventory']
        if params.get('initial_stock') is not None:
            data['initial_stock'] = params['initial_stock']
        if params.get('initial_stock_rate') is not None:
            data['initial_stock_rate'] = params['initial_stock_rate']
        if params.get('reorder_level') is not None:
            data['reorder_level'] = params['reorder_level']

        response = self._make_request('items', method='POST', data=data)

        if response.get('code') == 0:
            return response.get('item')

        self.module.fail_json(msg=f"Failed to create item: {response.get('message')}")

    def update_item(self, item_id, params):
        """Update an existing item"""
        data = {}

        if params.get('name'):
            data['name'] = params['name']
        if params.get('rate') is not None:
            data['rate'] = params['rate']
        if params.get('description') is not None:
            data['description'] = params['description']
        if params.get('sku') is not None:
            data['sku'] = params['sku']
        if params.get('product_type'):
            data['product_type'] = params['product_type']
        if params.get('unit') is not None:
            data['unit'] = params['unit']
        if params.get('tax_id') is not None:
            data['tax_id'] = params['tax_id']
        if params.get('tax_percentage') is not None:
            data['tax_percentage'] = params['tax_percentage']
        if params.get('purchase_rate') is not None:
            data['purchase_rate'] = params['purchase_rate']
        if params.get('purchase_account_id') is not None:
            data['purchase_account_id'] = params['purchase_account_id']
        if params.get('account_id') is not None:
            data['account_id'] = params['account_id']
        if params.get('inventory_account_id') is not None:
            data['inventory_account_id'] = params['inventory_account_id']
        if params.get('reorder_level') is not None:
            data['reorder_level'] = params['reorder_level']

        if not data:
            return None

        endpoint = f'items/{item_id}'
        response = self._make_request(endpoint, method='PUT', data=data)

        if response.get('code') == 0:
            return response.get('item')

        self.module.fail_json(msg=f"Failed to update item: {response.get('message')}")

    def delete_item(self, item_id):
        """Delete an item"""
        endpoint = f'items/{item_id}'
        response = self._make_request(endpoint, method='DELETE')

        if response.get('code') == 0:
            return True

        self.module.fail_json(msg=f"Failed to delete item: {response.get('message')}")

    def mark_item_active(self, item_id):
        """Mark an item as active"""
        endpoint = f'items/{item_id}/active'
        response = self._make_request(endpoint, method='POST')

        if response.get('code') == 0:
            return response.get('item')

        self.module.fail_json(msg=f"Failed to activate item: {response.get('message')}")

    def mark_item_inactive(self, item_id):
        """Mark an item as inactive"""
        endpoint = f'items/{item_id}/inactive'
        response = self._make_request(endpoint, method='POST')

        if response.get('code') == 0:
            return response.get('item')

        self.module.fail_json(msg=f"Failed to deactivate item: {response.get('message')}")

    def needs_update(self, existing, params):
        """Check if item needs updating"""
        if params.get('rate') is not None:
            if existing.get('rate') != params['rate']:
                return True

        if params.get('description') is not None:
            if existing.get('description', '') != params['description']:
                return True

        if params.get('sku') is not None:
            if existing.get('sku', '') != params['sku']:
                return True

        if params.get('product_type'):
            if existing.get('product_type', '') != params['product_type']:
                return True

        if params.get('unit') is not None:
            if existing.get('unit', '') != params['unit']:
                return True

        if params.get('tax_percentage') is not None:
            if existing.get('tax_percentage') != params['tax_percentage']:
                return True

        if params.get('purchase_rate') is not None:
            if existing.get('purchase_rate') != params['purchase_rate']:
                return True

        if params.get('reorder_level') is not None:
            if existing.get('reorder_level') != params['reorder_level']:
                return True

        return False


def main():
    module = AnsibleModule(
        argument_spec=dict(
            organization_id=dict(type='str', required=False),
            access_token=dict(type='str', required=False, no_log=True),
            name=dict(type='str', required=True),
            rate=dict(type='float'),
            description=dict(type='str'),
            sku=dict(type='str'),
            product_type=dict(
                type='str',
                choices=['goods', 'service', 'digital_service']
            ),
            unit=dict(type='str'),
            tax_id=dict(type='str'),
            tax_percentage=dict(type='float'),
            purchase_rate=dict(type='float'),
            purchase_account_id=dict(type='str'),
            account_id=dict(type='str'),
            inventory_account_id=dict(type='str'),
            item_type=dict(type='str', choices=['inventory', 'non_inventory']),
            track_inventory=dict(type='bool', default=False),
            initial_stock=dict(type='float'),
            initial_stock_rate=dict(type='float'),
            reorder_level=dict(type='float'),
            state=dict(type='str', choices=['present', 'absent', 'active', 'inactive'], default='present'),
            api_domain=dict(type='str', default='https://books.zoho.com')
        ),
        supports_check_mode=True
    )

    # Get credentials from environment variables if not provided
    org_id = module.params['organization_id'] or os.environ.get('ZOHO_ORGANIZATION_ID')
    access_token = module.params['access_token'] or os.environ.get('ZOHO_ACCESS_TOKEN')
    api_domain = module.params['api_domain']

    # Override api_domain from environment if not explicitly set and env var exists
    if module.params['api_domain'] == 'https://books.zoho.com' and os.environ.get('ZOHO_API_DOMAIN'):
        api_domain = os.environ.get('ZOHO_API_DOMAIN')

    # Validate required credentials
    if not org_id:
        module.fail_json(msg='organization_id is required either as parameter or ZOHO_ORGANIZATION_ID environment variable')

    if not access_token:
        module.fail_json(msg='access_token is required either as parameter or ZOHO_ACCESS_TOKEN environment variable')

    # Update module params with resolved values
    module.params['organization_id'] = org_id
    module.params['access_token'] = access_token
    module.params['api_domain'] = api_domain

    zb = ZohoBooksItem(module)
    params = module.params
    state = params['state']
    item_name = params['name']

    # Get existing item
    existing_item = zb.get_item_by_name(item_name)

    result = {
        'changed': False,
        'item': None,
        'msg': ''
    }

    if state == 'present':
        if existing_item:
            # Item exists - check if update needed
            if zb.needs_update(existing_item, params):
                if module.check_mode:
                    result['changed'] = True
                    result['msg'] = 'Item would be updated'
                else:
                    item_id = existing_item['item_id']
                    updated_item = zb.update_item(item_id, params)
                    result['changed'] = True
                    result['item'] = updated_item
                    result['msg'] = 'Item updated successfully'
            else:
                result['changed'] = False
                result['item'] = existing_item
                result['msg'] = 'Item already exists with correct parameters'
        else:
            # Item doesn't exist - create it
            if module.check_mode:
                result['changed'] = True
                result['msg'] = 'Item would be created'
            else:
                new_item = zb.create_item(params)
                result['changed'] = True
                result['item'] = new_item
                result['msg'] = 'Item created successfully'

    elif state == 'absent':
        if existing_item:
            if module.check_mode:
                result['changed'] = True
                result['msg'] = 'Item would be deleted'
            else:
                item_id = existing_item['item_id']
                zb.delete_item(item_id)
                result['changed'] = True
                result['msg'] = 'Item deleted successfully'
        else:
            result['changed'] = False
            result['msg'] = 'Item does not exist'

    elif state == 'active':
        if existing_item:
            if existing_item.get('status') == 'active':
                result['changed'] = False
                result['item'] = existing_item
                result['msg'] = 'Item is already active'
            else:
                if module.check_mode:
                    result['changed'] = True
                    result['msg'] = 'Item would be marked as active'
                else:
                    item_id = existing_item['item_id']
                    active_item = zb.mark_item_active(item_id)
                    result['changed'] = True
                    result['item'] = active_item
                    result['msg'] = 'Item marked as active'
        else:
            module.fail_json(msg='Cannot mark non-existent item as active')

    elif state == 'inactive':
        if existing_item:
            if existing_item.get('status') == 'inactive':
                result['changed'] = False
                result['item'] = existing_item
                result['msg'] = 'Item is already inactive'
            else:
                if module.check_mode:
                    result['changed'] = True
                    result['msg'] = 'Item would be marked as inactive'
                else:
                    item_id = existing_item['item_id']
                    inactive_item = zb.mark_item_inactive(item_id)
                    result['changed'] = True
                    result['item'] = inactive_item
                    result['msg'] = 'Item marked as inactive'
        else:
            module.fail_json(msg='Cannot mark non-existent item as inactive')

    module.exit_json(**result)


if __name__ == '__main__':
    main()
