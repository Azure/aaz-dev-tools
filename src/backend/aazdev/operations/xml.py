# -----------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -----------------------------------------------------------------------------
from lxml.builder import ElementMaker
from lxml.etree import tostring
from schematics.types import ListType, ModelType
from schematics.types.compound import PolyModelType
from xmltodict import parse

from command.model.configuration._schema import CMDSchemaBaseField

XML_ROOT = "CodeGen"


class XMLSerializer:
    def __init__(self, model):
        self.model = model

    def to_xml(self):
        primitive = self.model.to_primitive()
        root = build_xml(primitive)
        return tostring(root, xml_declaration=True, pretty_print=True, encoding="utf-8")

    def from_xml(self, xml):
        primitive = parse(xml, attr_prefix="")
        return build_model(self.model, primitive[XML_ROOT])


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


def build_model(model, primitive):
    if hasattr(model, "_field_list"):
        instance = model()
        for field_name, field in model._field_list:
            serialized_name = field.serialized_name or field_name
            if serialized_name not in primitive:
                continue
            data = primitive[serialized_name]
            curr_field = unwrap(field)
            # TODO: Handle SchemaBaseField
            if isinstance(curr_field, CMDSchemaBaseField):
                continue
            field_value = obtain_field_value(field, curr_field, data)
            try:
                setattr(instance, field_name, field_value)
            # TODO: Handle Serializable
            except AttributeError:
                continue
        return instance
    else:
        # TODO: Handle PrimitiveField
        cast = model.primitive_type or str
        return cast(primitive)


def unwrap(field):
    if isinstance(field, ListType):
        return unwrap(field.field)
    elif isinstance(field, ModelType):
        return field.model_class
    else:
        return field


def obtain_field_value(prev, curr, data):
    if isinstance(prev, ListType):
        field_value = []
        if " " in data:
            data = data.split()
        if isinstance(data, list):
            for d in data:
                model = curr.find_model(d) if isinstance(curr, PolyModelType) else curr
                value = build_model(model, d)
                field_value.append(value)
        else:
            model = curr.find_model(data) if isinstance(curr, PolyModelType) else curr
            value = build_model(model, data)
            field_value.append(value)
    else:
        model = curr.find_model(data) if isinstance(curr, PolyModelType) else curr
        field_value = build_model(model, data)
    return field_value
