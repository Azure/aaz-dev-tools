# -----------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------

import re
import html
import inflect

from lxml.builder import ElementMaker
from lxml.etree import Element, tostring

from command.model.configuration import CMDResource
from swagger.controller.command_generator import CommandGenerator


def generate_config(swagger_path, config_path, module_name, resource_id, api_version):
    generator = CommandGenerator(module_name="(MgmtPlane)/" + module_name, swagger_path=swagger_path)
    cmd_resource = CMDResource({"id": resource_id, "version": api_version})
    resources = generator.load_resources([cmd_resource])
    command_group = generator.create_draft_command_group(resources[resource_id])
    # structurally build configuration via xml
    root = Element("CodeGen", version="2.0")
    root.append(_build_xml("resource", cmd_resource.to_primitive()))
    root.append(_build_xml("command_group", command_group.to_primitive()))

    with open(config_path, "w") as fp:
        fp.write(
            html.unescape(
                tostring(root, xml_declaration=True,  pretty_print=True, encoding="utf-8").decode()
            )
        )
    return "Done."


def _build_xml(root, primitive, parent=None):
    linker = ElementMaker()
    if parent is None:
        parent = getattr(linker, root)()
    # normalize the name of element tag
    if curr_tag := _inflect_engine.singular_noun(parent.tag):
        parent.tag = curr_tag
    camel_pattern = re.compile(r"(?<!^)(?=[A-Z])")
    parent.tag = camel_pattern.sub("_", parent.tag).lower()

    for key, val in primitive.items():
        _primitive_to_xml(root, key, val, parent)
    return parent


def _primitive_to_xml(root, key, val, parent):
    linker = ElementMaker()
    if isinstance(val, dict):
        _parent = getattr(linker, key)()
        parent.append(_build_xml(root, val, _parent))
    elif isinstance(val, list):
        for _val in val:
            _primitive_to_xml(root, key, _val, parent)
    else:
        # sort when one key has multiple values
        if prev := parent.get(key):
            curr = " ".join(sorted(f"{prev} {val}".split(), reverse=True))
            parent.set(key, curr)
        else:
            parent.set(key, str(val))


_inflect_engine = inflect.engine()
