# -----------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------
import numbers

from lxml.builder import ElementMaker
from lxml.etree import tostring
from schematics.types import ListType, ModelType
from schematics.types.compound import PolyModelType
from xmltodict import parse

XML_ROOT = "CodeGen"


class XMLSerializer:
    def __init__(self, instance):
        self.instance = instance

    def to_xml(self):
        primitive = self.instance.to_primitive()
        root = build_xml(primitive)
        return tostring(root, xml_declaration=True, pretty_print=True, encoding="utf-8")

    # def from_xml(self, xml):
    #     model_data = parse(xml, attr_prefix="")
    #     return build_model(self.model_cls, model_data[XML_ROOT])


def build_xml(primitive, parent=None):
    linker = ElementMaker()
    if parent is None:
        parent = getattr(linker, XML_ROOT)()

    for field_name, data in primitive.items():
        _primitive_to_xml(field_name, data, parent)
    return parent


def _primitive_to_xml(field_name, data, parent):
    linker = ElementMaker()
    if isinstance(data, dict):
        _parent = getattr(linker, field_name)()
        parent.append(build_xml(data, _parent))
    elif isinstance(data, list):
        for d in data:
            _primitive_to_xml(field_name, d, parent)
    else:
        # store metadata as attributes
        if prev := parent.get(field_name):
            curr = " ".join(sorted(f"{prev} {data}".split(), reverse=True))
            parent.set(field_name, curr)
        else:
            parent.set(field_name, str(data))
