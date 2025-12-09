#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: zohobooks_account
short_description: Manage ZohoBooks chart of accounts
version_added: "0.1.0"
description:
    - Create, update, or delete accounts in ZohoBooks chart of accounts
    - Idempotent operations based on account name
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
            - Name of the account
        required: true
        type: str
    account_type:
        description:
            - Type of account
        required: false
        type: str
        choices:
            - other_asset
            - other_current_asset
            - cash
            - bank
            - fixed_asset
            - other_current_liability
            - credit_card
            - long_term_liability
            - other_liability
            - equity
            - income
            - other_income
            - expense
            - cost_of_goods_sold
            - other_expense
    description:
        description:
            - Description of the account
        required: false
        type: str
    account_code:
        description:
            - Account code/number
        required: false
        type: str
    parent_account_id:
        description:
            - Parent account ID for sub-accounts
        required: false
        type: str
    is_sub_account:
        description:
            - Whether this is a sub-account
        required: false
        type: bool
        default: false
    state:
        description:
            - Desired state of the account
        required: false
        type: str
        choices: ['present', 'absent']
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
- name: Create a bank account (using explicit parameters)
  zohobooks_account:
    organization_id: "123456789"
    access_token: "{{ zoho_access_token }}"
    account_name: "Business Checking"
    account_type: "bank"
    account_code: "1001"
    description: "Primary business checking account"
    state: present

- name: Create account using environment variables
  zohobooks_account:
    account_name: "Business Savings"
    account_type: "bank"
    account_code: "1002"
    description: "Business savings account"
    state: present
  environment:
    ZOHO_ORGANIZATION_ID: "123456789"
    ZOHO_ACCESS_TOKEN: "your_access_token"
    ZOHO_API_DOMAIN: "https://books.zoho.com"

- name: Create a sub-account
  zohobooks_account:
    organization_id: "123456789"
    access_token: "{{ zoho_access_token }}"
    account_name: "Office Supplies"
    account_type: "expense"
    parent_account_id: "987654321"
    is_sub_account: true
    state: present

- name: Update an existing account
  zohobooks_account:
    organization_id: "123456789"
    access_token: "{{ zoho_access_token }}"
    account_name: "Business Checking"
    description: "Updated description"
    state: present

- name: Delete an account
  zohobooks_account:
    organization_id: "123456789"
    access_token: "{{ zoho_access_token }}"
    account_name: "Old Account"
    state: absent
'''

RETURN = r'''
account:
    description: Account details
    returned: when state is present
    type: dict
    sample:
        account_id: "123456789"
        account_name: "Business Checking"
        account_type: "bank"
        account_code: "1001"
        description: "Primary business checking account"
changed:
    description: Whether the account was changed
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


class ZohoBooksAccount:
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

    def get_account_by_name(self, account_name):
        """Find account by name"""
        response = self._make_request('chartofaccounts')

        if response.get('code') == 0:
            accounts = response.get('chartofaccounts', [])
            for account in accounts:
                if account.get('account_name') == account_name:
                    return account
        return None

    def create_account(self, params):
        """Create a new account"""
        data = {
            'account_name': params['account_name']
        }

        if params.get('account_type'):
            data['account_type'] = params['account_type']
        if params.get('description'):
            data['description'] = params['description']
        if params.get('account_code'):
            data['account_code'] = params['account_code']
        if params.get('parent_account_id'):
            data['parent_account_id'] = params['parent_account_id']

        response = self._make_request('chartofaccounts', method='POST', data=data)

        if response.get('code') == 0:
            return response.get('account')

        self.module.fail_json(msg=f"Failed to create account: {response.get('message')}")

    def update_account(self, account_id, params):
        """Update an existing account"""
        data = {}

        if params.get('account_name'):
            data['account_name'] = params['account_name']
        if params.get('description') is not None:
            data['description'] = params['description']
        if params.get('account_code') is not None:
            data['account_code'] = params['account_code']

        if not data:
            return None

        endpoint = f'chartofaccounts/{account_id}'
        response = self._make_request(endpoint, method='PUT', data=data)

        if response.get('code') == 0:
            return response.get('account')

        self.module.fail_json(msg=f"Failed to update account: {response.get('message')}")

    def delete_account(self, account_id):
        """Delete an account"""
        endpoint = f'chartofaccounts/{account_id}'
        response = self._make_request(endpoint, method='DELETE')

        if response.get('code') == 0:
            return True

        self.module.fail_json(msg=f"Failed to delete account: {response.get('message')}")

    def needs_update(self, existing, params):
        """Check if account needs updating"""
        if params.get('description') is not None:
            if existing.get('description', '') != params['description']:
                return True

        if params.get('account_code') is not None:
            if existing.get('account_code', '') != params['account_code']:
                return True

        return False


def main():
    module = AnsibleModule(
        argument_spec=dict(
            organization_id=dict(type='str', required=False),
            access_token=dict(type='str', required=False, no_log=True),
            account_name=dict(type='str', required=True),
            account_type=dict(
                type='str',
                choices=[
                    'other_asset', 'other_current_asset', 'cash', 'bank',
                    'fixed_asset', 'other_current_liability', 'credit_card',
                    'long_term_liability', 'other_liability', 'equity',
                    'income', 'other_income', 'expense', 'cost_of_goods_sold',
                    'other_expense'
                ]
            ),
            description=dict(type='str'),
            account_code=dict(type='str'),
            parent_account_id=dict(type='str'),
            is_sub_account=dict(type='bool', default=False),
            state=dict(type='str', choices=['present', 'absent'], default='present'),
            api_domain=dict(type='str', default='https://books.zoho.com')
        ),
        supports_check_mode=True,
        required_if=[
            ('state', 'present', ['account_type'], True)
        ]
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

    zb = ZohoBooksAccount(module)
    params = module.params
    state = params['state']
    account_name = params['account_name']

    # Get existing account
    existing_account = zb.get_account_by_name(account_name)

    result = {
        'changed': False,
        'account': None,
        'msg': ''
    }

    if state == 'present':
        if existing_account:
            # Account exists - check if update needed
            if zb.needs_update(existing_account, params):
                if module.check_mode:
                    result['changed'] = True
                    result['msg'] = 'Account would be updated'
                else:
                    account_id = existing_account['account_id']
                    updated_account = zb.update_account(account_id, params)
                    result['changed'] = True
                    result['account'] = updated_account
                    result['msg'] = 'Account updated successfully'
            else:
                result['changed'] = False
                result['account'] = existing_account
                result['msg'] = 'Account already exists with correct parameters'
        else:
            # Account doesn't exist - create it
            if module.check_mode:
                result['changed'] = True
                result['msg'] = 'Account would be created'
            else:
                new_account = zb.create_account(params)
                result['changed'] = True
                result['account'] = new_account
                result['msg'] = 'Account created successfully'

    elif state == 'absent':
        if existing_account:
            if module.check_mode:
                result['changed'] = True
                result['msg'] = 'Account would be deleted'
            else:
                account_id = existing_account['account_id']
                zb.delete_account(account_id)
                result['changed'] = True
                result['msg'] = 'Account deleted successfully'
        else:
            result['changed'] = False
            result['msg'] = 'Account does not exist'

    module.exit_json(**result)


if __name__ == '__main__':
    main()
