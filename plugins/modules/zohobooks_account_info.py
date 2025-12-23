#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024, Kevin Colby (@zaepho)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: zohobooks_account_info
short_description: Retrieve ZohoBooks chart of accounts information
version_added: "0.2.0"
description:
    - Retrieve information about accounts in ZohoBooks chart of accounts
    - Can retrieve a specific account by name or ID, or list all accounts
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
    account_name:
        description:
            - Name of the account to retrieve
            - Mutually exclusive with account_id
        required: false
        type: str
    account_id:
        description:
            - ID of the account to retrieve
            - Mutually exclusive with account_name
        required: false
        type: str
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
- name: Get all accounts
  zaepho.zohobooks.zohobooks_account_info:
    organization_id: "123456789"
    access_token: "{{ zoho_access_token }}"
  register: all_accounts

- name: Get account by name
  zaepho.zohobooks.zohobooks_account_info:
    organization_id: "123456789"
    access_token: "{{ zoho_access_token }}"
    account_name: "Business Checking"
  register: account

- name: Get account by ID
  zaepho.zohobooks.zohobooks_account_info:
    organization_id: "123456789"
    access_token: "{{ zoho_access_token }}"
    account_id: "987654321"
  register: account

- name: Get accounts using environment variables
  zaepho.zohobooks.zohobooks_account_info:
    account_name: "Business Savings"
  environment:
    ZOHO_ORGANIZATION_ID: "123456789"
    ZOHO_ACCESS_TOKEN: "your_access_token"
    ZOHO_API_DOMAIN: "https://www.zohoapis.com"
  register: account

- name: Display account information
  debug:
    var: account.accounts
'''

RETURN = r'''
accounts:
    description: List of accounts matching the criteria
    returned: always
    type: list
    elements: dict
    sample:
        - account_id: "123456789"
          account_name: "Business Checking"
          account_type: "bank"
          account_code: "1001"
          description: "Primary business checking account"
          is_active: true
          is_user_created: true
          can_show_in_ze: false
          is_involved_in_transaction: false
count:
    description: Number of accounts returned
    returned: always
    type: int
    sample: 1
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import fetch_url
import json
import os


class ZohoBooksAccountInfo:
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

    def get_all_accounts(self):
        """Retrieve all accounts"""
        response = self._make_request('chartofaccounts')

        if response.get('code') == 0:
            return response.get('chartofaccounts', [])

        self.module.fail_json(msg=f"Failed to retrieve accounts: {response.get('message')}")

    def get_account_by_id(self, account_id):
        """Retrieve a specific account by ID"""
        endpoint = f'chartofaccounts/{account_id}'
        response = self._make_request(endpoint)

        if response.get('code') == 0:
            account = response.get('account')
            return [account] if account else []

        # If account not found, return empty list instead of failing
        if response.get('code') == 1004:  # Resource not found
            return []

        self.module.fail_json(msg=f"Failed to retrieve account: {response.get('message')}")

    def get_account_by_name(self, account_name):
        """Find account by name"""
        all_accounts = self.get_all_accounts()

        matching_accounts = [
            account for account in all_accounts
            if account.get('account_name') == account_name
        ]

        return matching_accounts


def main():
    module = AnsibleModule(
        argument_spec=dict(
            organization_id=dict(type='str', required=False),
            access_token=dict(type='str', required=False, no_log=True),
            account_name=dict(type='str', required=False),
            account_id=dict(type='str', required=False),
            api_domain=dict(type='str', default='https://www.zohoapis.com')
        ),
        supports_check_mode=True,
        mutually_exclusive=[
            ['account_name', 'account_id']
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

    zb = ZohoBooksAccountInfo(module)
    account_name = module.params['account_name']
    account_id = module.params['account_id']

    # Retrieve accounts based on parameters
    if account_id:
        accounts = zb.get_account_by_id(account_id)
    elif account_name:
        accounts = zb.get_account_by_name(account_name)
    else:
        accounts = zb.get_all_accounts()

    result = {
        'changed': False,
        'accounts': accounts,
        'count': len(accounts)
    }

    module.exit_json(**result)


if __name__ == '__main__':
    main()
