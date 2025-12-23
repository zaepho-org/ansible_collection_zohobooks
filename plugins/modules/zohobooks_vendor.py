#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2024
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = r'''
---
module: zohobooks_vendor
short_description: Manage ZohoBooks vendors
version_added: "0.3.0"
description:
    - Create, update, or delete vendors in ZohoBooks
    - Manage vendor status (active/inactive)
    - Idempotent operations based on vendor name
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
            - Display name for the vendor
            - Used for searching and displaying vendors
        required: true
        type: str
    company_name:
        description:
            - Legal company name
        required: false
        type: str
    vendor_sub_type:
        description:
            - Type of vendor
        required: false
        type: str
        choices: ['individual', 'business']
    email:
        description:
            - Email address of the vendor
        required: false
        type: str
    phone:
        description:
            - Phone number of the vendor
        required: false
        type: str
    mobile:
        description:
            - Mobile phone number of the vendor
        required: false
        type: str
    website:
        description:
            - Website URL of the vendor
        required: false
        type: str
    currency_code:
        description:
            - Currency code for the vendor (e.g., USD, EUR)
        required: false
        type: str
    payment_terms:
        description:
            - Default payment terms in days
        required: false
        type: int
    payment_terms_label:
        description:
            - Label for the payment terms
        required: false
        type: str
    billing_address:
        description:
            - Billing address details
        required: false
        type: dict
        suboptions:
            attention:
                description: Attention line
                type: str
            address:
                description: Street address
                type: str
            street2:
                description: Second line of address
                type: str
            city:
                description: City name
                type: str
            state:
                description: State or province
                type: str
            zip:
                description: ZIP or postal code
                type: str
            country:
                description: Country name
                type: str
            fax:
                description: Fax number
                type: str
    tax_id:
        description:
            - Tax ID or VAT registration number
        required: false
        type: str
    notes:
        description:
            - Additional notes about the vendor
        required: false
        type: str
    custom_fields:
        description:
            - Custom field values as a dictionary
        required: false
        type: dict
    state:
        description:
            - Desired state of the vendor
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
        default: 'https://www.zohoapis.com'
author:
    - Kevin Colby (@zaepho)
'''

EXAMPLES = r'''
- name: Create a vendor (using explicit parameters)
  zohobooks_vendor:
    organization_id: "123456789"
    access_token: "{{ zoho_access_token }}"
    contact_name: "Acme Suppliers"
    company_name: "Acme Suppliers Inc."
    vendor_sub_type: "business"
    email: "contact@acmesuppliers.com"
    phone: "555-1234"
    payment_terms: 30
    payment_terms_label: "Net 30"
    state: present

- name: Create vendor using environment variables
  zohobooks_vendor:
    contact_name: "Office Depot"
    company_name: "Office Depot Inc."
    vendor_sub_type: "business"
    email: "vendor@officedepot.com"
    state: present
  environment:
    ZOHO_ORGANIZATION_ID: "123456789"
    ZOHO_ACCESS_TOKEN: "your_access_token"
    ZOHO_API_DOMAIN: "https://www.zohoapis.com"

- name: Create vendor with billing address
  zohobooks_vendor:
    organization_id: "123456789"
    access_token: "{{ zoho_access_token }}"
    contact_name: "Tech Solutions"
    company_name: "Tech Solutions LLC"
    vendor_sub_type: "business"
    email: "billing@techsolutions.com"
    billing_address:
      address: "123 Main Street"
      city: "New York"
      state: "NY"
      zip: "10001"
      country: "USA"
    state: present

- name: Update an existing vendor
  zohobooks_vendor:
    organization_id: "123456789"
    access_token: "{{ zoho_access_token }}"
    contact_name: "Acme Suppliers"
    email: "newemail@acmesuppliers.com"
    payment_terms: 45
    state: present

- name: Mark vendor as inactive
  zohobooks_vendor:
    organization_id: "123456789"
    access_token: "{{ zoho_access_token }}"
    contact_name: "Old Supplier"
    state: inactive

- name: Mark vendor as active
  zohobooks_vendor:
    organization_id: "123456789"
    access_token: "{{ zoho_access_token }}"
    contact_name: "Acme Suppliers"
    state: active

- name: Delete a vendor
  zohobooks_vendor:
    organization_id: "123456789"
    access_token: "{{ zoho_access_token }}"
    contact_name: "Obsolete Vendor"
    state: absent
'''

RETURN = r'''
vendor:
    description: Vendor details
    returned: when state is present, active, or inactive
    type: dict
    sample:
        contact_id: "123456789"
        contact_name: "Acme Suppliers"
        company_name: "Acme Suppliers Inc."
        contact_type: "vendor"
        vendor_sub_type: "business"
        email: "contact@acmesuppliers.com"
        phone: "555-1234"
        status: "active"
        payment_terms: 30
        payment_terms_label: "Net 30"
changed:
    description: Whether the vendor was changed
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


class ZohoBooksVendor:
    def __init__(self, module):
        self.module = module
        self.org_id = module.params['organization_id']
        self.token = module.params['access_token']
        self.api_domain = module.params['api_domain']
        self.base_url = f"{self.api_domain}/books/v3"

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

    def get_vendor_by_name(self, contact_name):
        """Find vendor by contact name"""
        response = self._make_request('contacts?contact_type=vendor')

        if response.get('code') == 0:
            contacts = response.get('contacts', [])
            for contact in contacts:
                if contact.get('contact_name') == contact_name:
                    return contact
        return None

    def create_vendor(self, params):
        """Create a new vendor"""
        data = {
            'contact_name': params['contact_name'],
            'contact_type': 'vendor'
        }

        # Add optional fields
        if params.get('company_name'):
            data['company_name'] = params['company_name']
        if params.get('vendor_sub_type'):
            data['vendor_sub_type'] = params['vendor_sub_type']
        if params.get('email'):
            data['email'] = params['email']
        if params.get('phone'):
            data['phone'] = params['phone']
        if params.get('mobile'):
            data['mobile'] = params['mobile']
        if params.get('website'):
            data['website'] = params['website']
        if params.get('currency_code'):
            data['currency_code'] = params['currency_code']
        if params.get('payment_terms') is not None:
            data['payment_terms'] = params['payment_terms']
        if params.get('payment_terms_label'):
            data['payment_terms_label'] = params['payment_terms_label']
        if params.get('billing_address'):
            data['billing_address'] = params['billing_address']
        if params.get('tax_id'):
            data['tax_id'] = params['tax_id']
        if params.get('notes'):
            data['notes'] = params['notes']
        if params.get('custom_fields'):
            # Convert custom_fields dict to the format expected by API
            custom_field_list = []
            for key, value in params['custom_fields'].items():
                custom_field_list.append({'label': key, 'value': value})
            data['custom_fields'] = custom_field_list

        response = self._make_request('contacts', method='POST', data=data)

        if response.get('code') == 0:
            return response.get('contact')

        self.module.fail_json(msg=f"Failed to create vendor: {response.get('message')}")

    def update_vendor(self, contact_id, params):
        """Update an existing vendor"""
        data = {}

        # Selectively include changed fields
        if params.get('contact_name'):
            data['contact_name'] = params['contact_name']
        if params.get('company_name') is not None:
            data['company_name'] = params['company_name']
        if params.get('vendor_sub_type') is not None:
            data['vendor_sub_type'] = params['vendor_sub_type']
        if params.get('email') is not None:
            data['email'] = params['email']
        if params.get('phone') is not None:
            data['phone'] = params['phone']
        if params.get('mobile') is not None:
            data['mobile'] = params['mobile']
        if params.get('website') is not None:
            data['website'] = params['website']
        if params.get('currency_code') is not None:
            data['currency_code'] = params['currency_code']
        if params.get('payment_terms') is not None:
            data['payment_terms'] = params['payment_terms']
        if params.get('payment_terms_label') is not None:
            data['payment_terms_label'] = params['payment_terms_label']
        if params.get('billing_address') is not None:
            data['billing_address'] = params['billing_address']
        if params.get('tax_id') is not None:
            data['tax_id'] = params['tax_id']
        if params.get('notes') is not None:
            data['notes'] = params['notes']
        if params.get('custom_fields') is not None:
            # Convert custom_fields dict to the format expected by API
            custom_field_list = []
            for key, value in params['custom_fields'].items():
                custom_field_list.append({'label': key, 'value': value})
            data['custom_fields'] = custom_field_list

        if not data:
            return None

        endpoint = f'contacts/{contact_id}'
        response = self._make_request(endpoint, method='PUT', data=data)

        if response.get('code') == 0:
            return response.get('contact')

        self.module.fail_json(msg=f"Failed to update vendor: {response.get('message')}")

    def delete_vendor(self, contact_id):
        """Delete a vendor"""
        endpoint = f'contacts/{contact_id}'
        response = self._make_request(endpoint, method='DELETE')

        if response.get('code') == 0:
            return True

        self.module.fail_json(msg=f"Failed to delete vendor: {response.get('message')}")

    def mark_vendor_active(self, contact_id):
        """Mark vendor as active"""
        endpoint = f'contacts/{contact_id}/active'
        response = self._make_request(endpoint, method='POST')

        if response.get('code') == 0:
            return response.get('contact')

        self.module.fail_json(msg=f"Failed to mark vendor as active: {response.get('message')}")

    def mark_vendor_inactive(self, contact_id):
        """Mark vendor as inactive"""
        endpoint = f'contacts/{contact_id}/inactive'
        response = self._make_request(endpoint, method='POST')

        if response.get('code') == 0:
            return response.get('contact')

        self.module.fail_json(msg=f"Failed to mark vendor as inactive: {response.get('message')}")

    def needs_update(self, existing, params):
        """Check if vendor needs updating"""
        # Compare fields that can be updated
        if params.get('company_name') is not None:
            if existing.get('company_name', '') != params['company_name']:
                return True

        if params.get('vendor_sub_type') is not None:
            if existing.get('vendor_sub_type', '') != params['vendor_sub_type']:
                return True

        if params.get('email') is not None:
            if existing.get('email', '') != params['email']:
                return True

        if params.get('phone') is not None:
            if existing.get('phone', '') != params['phone']:
                return True

        if params.get('mobile') is not None:
            if existing.get('mobile', '') != params['mobile']:
                return True

        if params.get('website') is not None:
            if existing.get('website', '') != params['website']:
                return True

        if params.get('currency_code') is not None:
            if existing.get('currency_code', '') != params['currency_code']:
                return True

        if params.get('payment_terms') is not None:
            if existing.get('payment_terms', 0) != params['payment_terms']:
                return True

        if params.get('payment_terms_label') is not None:
            if existing.get('payment_terms_label', '') != params['payment_terms_label']:
                return True

        if params.get('billing_address') is not None:
            if existing.get('billing_address', {}) != params['billing_address']:
                return True

        if params.get('tax_id') is not None:
            if existing.get('tax_id', '') != params['tax_id']:
                return True

        if params.get('notes') is not None:
            if existing.get('notes', '') != params['notes']:
                return True

        return False


def main():
    module = AnsibleModule(
        argument_spec=dict(
            organization_id=dict(type='str', required=False),
            access_token=dict(type='str', required=False, no_log=True),
            contact_name=dict(type='str', required=True),
            company_name=dict(type='str'),
            vendor_sub_type=dict(type='str', choices=['individual', 'business']),
            email=dict(type='str'),
            phone=dict(type='str'),
            mobile=dict(type='str'),
            website=dict(type='str'),
            currency_code=dict(type='str'),
            payment_terms=dict(type='int'),
            payment_terms_label=dict(type='str'),
            billing_address=dict(
                type='dict',
                options=dict(
                    attention=dict(type='str'),
                    address=dict(type='str'),
                    street2=dict(type='str'),
                    city=dict(type='str'),
                    state=dict(type='str'),
                    zip=dict(type='str'),
                    country=dict(type='str'),
                    fax=dict(type='str')
                )
            ),
            tax_id=dict(type='str'),
            notes=dict(type='str'),
            custom_fields=dict(type='dict'),
            state=dict(type='str', choices=['present', 'absent', 'active', 'inactive'], default='present'),
            api_domain=dict(type='str', default='https://www.zohoapis.com')
        ),
        supports_check_mode=True
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

    zb = ZohoBooksVendor(module)
    params = module.params
    state = params['state']
    contact_name = params['contact_name']

    # Get existing vendor
    existing_vendor = zb.get_vendor_by_name(contact_name)

    result = {
        'changed': False,
        'vendor': None,
        'msg': ''
    }

    if state == 'present':
        if existing_vendor:
            # Vendor exists - check if update needed
            if zb.needs_update(existing_vendor, params):
                if module.check_mode:
                    result['changed'] = True
                    result['msg'] = 'Vendor would be updated'
                else:
                    contact_id = existing_vendor['contact_id']
                    updated_vendor = zb.update_vendor(contact_id, params)
                    result['changed'] = True
                    result['vendor'] = updated_vendor
                    result['msg'] = 'Vendor updated successfully'
            else:
                result['changed'] = False
                result['vendor'] = existing_vendor
                result['msg'] = 'Vendor already exists with correct parameters'
        else:
            # Vendor doesn't exist - create it
            if module.check_mode:
                result['changed'] = True
                result['msg'] = 'Vendor would be created'
            else:
                new_vendor = zb.create_vendor(params)
                result['changed'] = True
                result['vendor'] = new_vendor
                result['msg'] = 'Vendor created successfully'

    elif state == 'absent':
        if existing_vendor:
            if module.check_mode:
                result['changed'] = True
                result['msg'] = 'Vendor would be deleted'
            else:
                contact_id = existing_vendor['contact_id']
                zb.delete_vendor(contact_id)
                result['changed'] = True
                result['msg'] = 'Vendor deleted successfully'
        else:
            result['changed'] = False
            result['msg'] = 'Vendor does not exist'

    elif state == 'active':
        if existing_vendor:
            if existing_vendor.get('status') == 'active':
                result['changed'] = False
                result['vendor'] = existing_vendor
                result['msg'] = 'Vendor is already active'
            else:
                if module.check_mode:
                    result['changed'] = True
                    result['msg'] = 'Vendor would be marked as active'
                else:
                    contact_id = existing_vendor['contact_id']
                    activated_vendor = zb.mark_vendor_active(contact_id)
                    result['changed'] = True
                    result['vendor'] = activated_vendor
                    result['msg'] = 'Vendor marked as active'
        else:
            module.fail_json(msg='Cannot mark non-existent vendor as active')

    elif state == 'inactive':
        if existing_vendor:
            if existing_vendor.get('status') == 'inactive':
                result['changed'] = False
                result['vendor'] = existing_vendor
                result['msg'] = 'Vendor is already inactive'
            else:
                if module.check_mode:
                    result['changed'] = True
                    result['msg'] = 'Vendor would be marked as inactive'
                else:
                    contact_id = existing_vendor['contact_id']
                    deactivated_vendor = zb.mark_vendor_inactive(contact_id)
                    result['changed'] = True
                    result['vendor'] = deactivated_vendor
                    result['msg'] = 'Vendor marked as inactive'
        else:
            module.fail_json(msg='Cannot mark non-existent vendor as inactive')

    module.exit_json(**result)


if __name__ == '__main__':
    main()
