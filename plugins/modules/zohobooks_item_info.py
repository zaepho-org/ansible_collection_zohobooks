#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, Kevin Colby (@zaepho)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: zohobooks_item_info
short_description: Retrieve ZohoBooks items information
version_added: "0.2.0"
description:
    - Retrieve information about items in ZohoBooks
    - Can retrieve a specific item by name or ID, or list all items
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
            - Name of the item to retrieve
            - Mutually exclusive with item_id
        required: false
        type: str
    item_id:
        description:
            - ID of the item to retrieve
            - Mutually exclusive with name
        required: false
        type: str
    sku:
        description:
            - SKU of the item to retrieve
            - Mutually exclusive with name and item_id
        required: false
        type: str
    filter_by:
        description:
            - Filter items by status
        required: false
        type: str
        choices:
            - Status.Active
            - Status.Inactive
            - Status.All
    api_domain:
        description:
            - ZohoBooks API domain
            - Can also be set via ZOHO_API_DOMAIN environment variable
        required: false
        type: str
        default: 'https://www.zohoapis.com'
author:
    - Kevin Colby (@zaepho)
'''

EXAMPLES = r'''
- name: Get all items
  zaepho.zohobooks.zohobooks_item_info:
    organization_id: "123456789"
    access_token: "{{ zoho_access_token }}"
  register: all_items

- name: Get item by name
  zaepho.zohobooks.zohobooks_item_info:
    organization_id: "123456789"
    access_token: "{{ zoho_access_token }}"
    name: "Hard Drive"
  register: item

- name: Get item by ID
  zaepho.zohobooks.zohobooks_item_info:
    organization_id: "123456789"
    access_token: "{{ zoho_access_token }}"
    item_id: "987654321"
  register: item

- name: Get item by SKU
  zaepho.zohobooks.zohobooks_item_info:
    organization_id: "123456789"
    access_token: "{{ zoho_access_token }}"
    sku: "HD-500GB-001"
  register: item

- name: Get all active items
  zaepho.zohobooks.zohobooks_item_info:
    organization_id: "123456789"
    access_token: "{{ zoho_access_token }}"
    filter_by: "Status.Active"
  register: active_items

- name: Get items using environment variables
  zaepho.zohobooks.zohobooks_item_info:
    name: "Software License"
  environment:
    ZOHO_ORGANIZATION_ID: "123456789"
    ZOHO_ACCESS_TOKEN: "your_access_token"
    ZOHO_API_DOMAIN: "https://www.zohoapis.com"
  register: item

- name: Display item information
  debug:
    var: item.zohobooks_items
'''

RETURN = r'''
zohobooks_items:
    description: List of items matching the criteria
    returned: always
    type: list
    elements: dict
    sample:
        - item_id: "123456789"
          name: "Hard Drive"
          rate: 120.00
          description: "500GB Hard Drive"
          sku: "HD-500GB-001"
          product_type: "goods"
          status: "active"
          unit: "unit"
          tax_id: "987654321"
          tax_name: "Sales Tax"
          tax_percentage: 10
          track_inventory: false
          item_type: "sales"
count:
    description: Number of items returned
    returned: always
    type: int
    sample: 1
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import fetch_url
import json
import os


class ZohoBooksItemInfo:
    def __init__(self, module):
        self.module = module
        self.org_id = module.params['organization_id']
        self.token = module.params['access_token']
        self.api_domain = module.params['api_domain']
        self.base_url = f"{self.api_domain}/books/v3"

    def _make_request(self, endpoint, method='GET', params=None):
        """Make HTTP request to ZohoBooks API"""
        url = f"{self.base_url}/{endpoint}"
        headers = {
            'Authorization': f'Zoho-oauthtoken {self.token}',
            'Content-Type': 'application/json'
        }

        # Build query parameters
        query_params = {'organization_id': self.org_id}
        if params:
            query_params.update(params)

        if '?' in url:
            url += '&' + '&'.join([f"{k}={v}" for k, v in query_params.items()])
        else:
            url += '?' + '&'.join([f"{k}={v}" for k, v in query_params.items()])

        resp, info = fetch_url(
            self.module,
            url,
            method=method,
            headers=headers
        )

        if info['status'] not in [200, 201]:
            error_msg = f"API request ({url}) failed: {info['status']}"
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

    def get_all_items(self, filter_by=None):
        """Retrieve all items with automatic pagination"""
        params = {}
        if filter_by:
            params['filter_by'] = filter_by

        all_items = []
        page = 1
        has_more_page = True

        while has_more_page:
            params['page'] = page
            response = self._make_request('items', params=params)

            if response.get('code') == 0:
                items = response.get('items', [])
                all_items.extend(items)

                # Check if there are more pages
                page_context = response.get('page_context', {})
                has_more_page = page_context.get('has_more_page', False)
                page += 1
            else:
                self.module.fail_json(msg=f"Failed to retrieve items: {response.get('message')}")

        return all_items

    def get_item_by_id(self, item_id):
        """Retrieve a specific item by ID"""
        endpoint = f'items/{item_id}'
        response = self._make_request(endpoint)

        if response.get('code') == 0:
            item = response.get('item')
            return [item] if item else []

        # If item not found, return empty list instead of failing
        if response.get('code') == 1004:  # Resource not found
            return []

        self.module.fail_json(msg=f"Failed to retrieve item: {response.get('message')}")

    def get_item_by_name(self, item_name):
        """Find item by name"""
        all_items = self.get_all_items()

        matching_items = [
            item for item in all_items
            if item.get('name') == item_name
        ]

        return matching_items

    def get_item_by_sku(self, sku):
        """Find item by SKU"""
        all_items = self.get_all_items()

        matching_items = [
            item for item in all_items
            if item.get('sku') == sku
        ]

        return matching_items


def main():
    module = AnsibleModule(
        argument_spec=dict(
            organization_id=dict(type='str', required=False),
            access_token=dict(type='str', required=False, no_log=True),
            name=dict(type='str', required=False),
            item_id=dict(type='str', required=False),
            sku=dict(type='str', required=False),
            filter_by=dict(
                type='str',
                required=False,
                choices=['Status.Active', 'Status.Inactive', 'Status.All']
            ),
            api_domain=dict(type='str', default='https://www.zohoapis.com')
        ),
        supports_check_mode=True,
        mutually_exclusive=[
            ['name', 'item_id', 'sku']
        ]
    )

    # Get credentials from environment variables if not provided
    org_id = module.params['organization_id'] or os.environ.get('ZOHO_ORGANIZATION_ID')
    access_token = module.params['access_token'] or os.environ.get('ZOHO_ACCESS_TOKEN')
    api_domain = module.params['api_domain']

    # Override api_domain from environment if not explicitly set and env var exists
    if module.params['api_domain'] == 'https://www.zohoapis.com' and os.environ.get('ZOHO_API_DOMAIN'):
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

    zb = ZohoBooksItemInfo(module)
    name = module.params['name']
    item_id = module.params['item_id']
    sku = module.params['sku']
    filter_by = module.params['filter_by']

    # Retrieve items based on parameters
    if item_id:
        items = zb.get_item_by_id(item_id)
    elif name:
        items = zb.get_item_by_name(name)
    elif sku:
        items = zb.get_item_by_sku(sku)
    else:
        items = zb.get_all_items(filter_by=filter_by)

    result = {
        'changed': False,
        'zohobooks_items': items,
        'count': len(items)
    }

    module.exit_json(**result)


if __name__ == '__main__':
    main()
