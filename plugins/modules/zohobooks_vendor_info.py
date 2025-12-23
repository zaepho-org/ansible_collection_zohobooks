#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, Kevin Colby (@zaepho)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: zohobooks_vendor_info
short_description: Retrieve ZohoBooks vendor information
version_added: "0.3.0"
description:
    - Retrieve information about vendors in ZohoBooks
    - Can retrieve a specific vendor by name or ID, or list all vendors
    - Optionally filter vendors by status (active, inactive, or all)
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
    contact_name:
        description:
            - Name of the vendor to retrieve
            - Mutually exclusive with contact_id
        required: false
        type: str
    contact_id:
        description:
            - ID of the vendor to retrieve
            - Mutually exclusive with contact_name
        required: false
        type: str
    filter_by:
        description:
            - Filter vendors by status
        required: false
        type: str
        choices: ['Status.Active', 'Status.Inactive', 'Status.All']
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
- name: Get all vendors
  zaepho.zohobooks.zohobooks_vendor_info:
    organization_id: "123456789"
    access_token: "{{ zoho_access_token }}"
  register: all_vendors

- name: Get vendor by name
  zaepho.zohobooks.zohobooks_vendor_info:
    organization_id: "123456789"
    access_token: "{{ zoho_access_token }}"
    contact_name: "Acme Suppliers"
  register: vendor

- name: Get vendor by ID
  zaepho.zohobooks.zohobooks_vendor_info:
    organization_id: "123456789"
    access_token: "{{ zoho_access_token }}"
    contact_id: "987654321"
  register: vendor

- name: Get all active vendors
  zaepho.zohobooks.zohobooks_vendor_info:
    organization_id: "123456789"
    access_token: "{{ zoho_access_token }}"
    filter_by: "Status.Active"
  register: active_vendors

- name: Get all inactive vendors
  zaepho.zohobooks.zohobooks_vendor_info:
    organization_id: "123456789"
    access_token: "{{ zoho_access_token }}"
    filter_by: "Status.Inactive"
  register: inactive_vendors

- name: Get vendors using environment variables
  zaepho.zohobooks.zohobooks_vendor_info:
    contact_name: "Office Depot"
  environment:
    ZOHO_ORGANIZATION_ID: "123456789"
    ZOHO_ACCESS_TOKEN: "your_access_token"
    ZOHO_API_DOMAIN: "https://www.zohoapis.com"
  register: vendor

- name: Display vendor information
  debug:
    var: vendor.vendors
'''

RETURN = r'''
vendors:
    description: List of vendors matching the criteria
    returned: always
    type: list
    elements: dict
    sample:
        - contact_id: "123456789"
          contact_name: "Acme Suppliers"
          company_name: "Acme Suppliers Inc."
          contact_type: "vendor"
          vendor_sub_type: "business"
          email: "contact@acmesuppliers.com"
          phone: "555-1234"
          status: "active"
          payment_terms: 30
          payment_terms_label: "Net 30"
          billing_address:
            address: "123 Main Street"
            city: "New York"
            state: "NY"
            zip: "10001"
            country: "USA"
count:
    description: Number of vendors returned
    returned: always
    type: int
    sample: 1
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import fetch_url
import json
import os


class ZohoBooksVendorInfo:
    def __init__(self, module):
        self.module = module
        self.org_id = module.params['organization_id']
        self.token = module.params['access_token']
        self.api_domain = module.params['api_domain']
        self.base_url = f"{self.api_domain}/books/v3"

    def _make_request(self, endpoint, method='GET'):
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

        resp, info = fetch_url(
            self.module,
            url,
            method=method,
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

    def get_all_vendors(self, filter_by=None):
        """Retrieve all vendors with automatic pagination"""
        all_vendors = []
        page = 1
        has_more_page = True

        while has_more_page:
            endpoint = f'contacts?contact_type=vendor&page={page}'

            if filter_by:
                endpoint += f'&filter_by={filter_by}'

            response = self._make_request(endpoint)

            if response.get('code') == 0:
                contacts = response.get('contacts', [])
                all_vendors.extend(contacts)

                # Check if there are more pages
                page_context = response.get('page_context', {})
                has_more_page = page_context.get('has_more_page', False)
                page += 1
            else:
                self.module.fail_json(msg=f"Failed to retrieve vendors: {response.get('message')}")

        return all_vendors

    def get_vendor_by_id(self, contact_id):
        """Retrieve a specific vendor by ID"""
        endpoint = f'contacts/{contact_id}'
        response = self._make_request(endpoint)

        if response.get('code') == 0:
            contact = response.get('contact')
            # Verify this is actually a vendor
            if contact and contact.get('contact_type') == 'vendor':
                return [contact]
            return []

        # If contact not found, return empty list instead of failing
        if response.get('code') == 1004:  # Resource not found
            return []

        self.module.fail_json(msg=f"Failed to retrieve vendor: {response.get('message')}")

    def get_vendor_by_name(self, contact_name, filter_by=None):
        """Find vendor by name"""
        all_vendors = self.get_all_vendors(filter_by)

        matching_vendors = [
            vendor for vendor in all_vendors
            if vendor.get('contact_name') == contact_name
        ]

        return matching_vendors


def main():
    module = AnsibleModule(
        argument_spec=dict(
            organization_id=dict(type='str', required=False),
            access_token=dict(type='str', required=False, no_log=True),
            contact_name=dict(type='str', required=False),
            contact_id=dict(type='str', required=False),
            filter_by=dict(
                type='str',
                required=False,
                choices=['Status.Active', 'Status.Inactive', 'Status.All']
            ),
            api_domain=dict(type='str', default='https://www.zohoapis.com')
        ),
        supports_check_mode=True,
        mutually_exclusive=[
            ['contact_name', 'contact_id']
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

    zb = ZohoBooksVendorInfo(module)
    contact_name = module.params['contact_name']
    contact_id = module.params['contact_id']
    filter_by = module.params['filter_by']

    # Retrieve vendors based on parameters
    if contact_id:
        vendors = zb.get_vendor_by_id(contact_id)
    elif contact_name:
        vendors = zb.get_vendor_by_name(contact_name, filter_by)
    else:
        vendors = zb.get_all_vendors(filter_by)

    result = {
        'changed': False,
        'vendors': vendors,
        'count': len(vendors)
    }

    module.exit_json(**result)


if __name__ == '__main__':
    main()
