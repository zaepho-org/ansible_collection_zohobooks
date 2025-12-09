#!/usr/bin/python
# pylint: disable=E0401
# item_info.py - A custom module plugin for Ansible.
# Author: Kevin Colby (@zaepho)
# License: GPL-3.0-or-later
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, annotations, division, print_function


DOCUMENTATION = """
    module: item_info
    author: Kevin Colby (@zaepho)
    version_added: "1.0.0"
    short_description: Gets a Zoho Books Item
    description:
      - This module get one or more items from the Zoho Books API.
    options:
      name:
        description: Name of the item to get from Zoho Books
        type: str
      item_id:
        description: item_id of the item to get from Zoho Books
        type: str
"""

EXAMPLES = """
# item_info module example

- name: Get Item
  zaepho.zohobooks.item_info:
    name: "Widget"
"""


__metaclass__ = type  # pylint: disable=C0103

from typing import TYPE_CHECKING

from ansible.module_utils.basic import AnsibleModule, env_fallback  # type: ignore


if TYPE_CHECKING:
    from typing import Callable


def _get_by_name(name: str) -> str:
    """Returns Hello message.

    Args:
        name: The name to greet.

    Returns:
        str: The greeting message.
    """
    return "Hello, " + name


def main() -> None:
    """entry point for module execution"""
    argument_spec = dict(
        name=dict(type="str", required=False),
        item_id=dict(type="str", required=False),
        access_token=dict(
            type="str",
            required=True,
            no_log=True,
            fallback=(env_fallback, ['ZOHO_ACCESS_TOKEN'])
        )
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True
    )

    result = {
        "changed": False,
    }

    _get_by_name(module.params["name"])

    module.exit_json(**result)


if __name__ == "__main__":
    main()
