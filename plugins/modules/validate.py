# Copyright 2023 Nokia
# Licensed under the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause

"""Ansible module for validating configuration on SR Linux devices"""
from __future__ import absolute_import, division, print_function

import json
import random

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.nokia.srlinux.plugins.module_utils.srlinux import (
    JSONRPCClient,
    convertResponseKeys,
)
from ansible_collections.nokia.srlinux.plugins.module_utils.const import (
    JSON_RPC_VERSION,
)

# pylint: disable=invalid-name
__metaclass__ = type

DOCUMENTATION = """
---
module: validate
short_description: "Validating configuration on SR Linux devices."
description:
  - Validating configuration on SR Linux devices using `commit validate` feature of SR Linux.
version_added: "0.1.0"
options:
  update:
    description:
      - Update operations to validate.
    required: false
    type: list
    elements: dict
    suboptions:
      path:
        description:
          - targeted path for update operation
        type: str
        required: true
      value:
        type: dict
        description:
          - values to update
        required: true
  delete:
    description:
      - Delete operations to validate.
    required: false
    type: list
    elements: dict
    suboptions:
      path:
        description:
          - targeted path for delete operation
        type: str
        required: true
  replace:
    description:
      - Replace operations to validate.
    required: false
    type: list
    elements: dict
    suboptions:
      path:
        description:
          - targeted path for replace operation
        type: str
        required: true
      value:
        description:
          - values to replace
        required: true
        type: dict
  yang_models:
    type: str
    description:
      - YANG models to use for the get operation.
    choices:
      - srl
      - oc
    default: srl

author:
  - Patrick Dumais (@Nokia)
  - Roman Dodin (@Nokia)
  - Walter De Smedt (@Nokia)
"""

EXAMPLES = """
- name: Validate a valid change set
  nokia.srlinux.validate:
    update:
      - path: /system/information
        value:
          location: Some location
          contact: Some contact
"""


def main():
    """Main function"""
    argspec = {
        "update": {
            "type": "list",
            "elements": "dict",
            "required": False,
            "options": {
                "path": {"type": "str", "required": True},
                "value": {"type": "dict", "required": True},
            },
        },
        "delete": {
            "type": "list",
            "elements": "dict",
            "required": False,
            "options": {
                "path": {"type": "str", "required": True},
            },
        },
        "replace": {
            "type": "list",
            "elements": "dict",
            "required": False,
            "options": {
                "path": {"type": "str", "required": True},
                "value": {"type": "dict", "required": True},
            },
        },
        "yang_models": {"choices": ["srl", "oc"], "default": "srl"},
    }

    module = AnsibleModule(argument_spec=argspec, supports_check_mode=True)

    client = JSONRPCClient(module)

    updates = module.params.get("update") or []
    deletes = module.params.get("deletes") or []
    replaces = module.params.get("replace") or []
    yang_models = module.params.get("yang_models")

    commands = []
    for x in updates:
        x["action"] = "update"
        commands += [x]
    for x in deletes:
        x["action"] = "delete"
        commands += [x]
    for x in replaces:
        x["action"] = "replace"
        commands += [x]

    data = {
        "jsonrpc": JSON_RPC_VERSION,
        "id": random.randint(0, 65535),
        "method": "validate",
        "params": {
            "commands": commands,
            "yang-models": yang_models,
        },
    }
    response = client.post(payload=json.dumps(data))
    convertResponseKeys(response)

    # If the request was successful, we return the result
    if response and not response.get("error"):
        module.exit_json(**response)

    response["failed"] = True
    module.fail_json(
        msg=response["error"]["message"],
        jsonrpc_req_id=response["jsonrpc_req_id"],
    )


if __name__ == "__main__":
    main()
