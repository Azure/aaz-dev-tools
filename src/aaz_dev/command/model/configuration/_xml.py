from pluralizer import Pluralizer
import re

from lxml.builder import ElementMaker
from lxml.etree import Element, tostring
from xml.sax.saxutils import unescape
from xmltodict import parse

from schematics.types import ListType, ModelType
from schematics.types.compound import PolyModelType
from schematics.types.serializable import Serializable
from ._fields import CMDPrimitiveField

XML_ROOT = "CodeGen"


class XMLSerializer:

    @classmethod
    def to_xml(cls, value):
        primitive = value.to_primitive(context={"to_xml": True})
        root = build_xml(primitive)
        return unescape(
            tostring(root, xml_declaration=True, pretty_print=True, encoding="utf-8").decode()
        )

    @classmethod
    def from_xml(cls, model, xml):
        primitive = parse(cls._escape(xml), attr_prefix="")
        return build_model(model, primitive[XML_ROOT])

    @staticmethod
    def _escape(data):
        ret = ""
        lines = re.findall(r"<(.+)>", data)
        for line in lines:
            # handle long-summary
            if line.startswith("line>"):
                ret += "<" + line + ">" + "\n"
                continue
            line = line.replace("&", "&amp;")
            line = line.replace(">", "&gt;")
            line = line.replace("<", "&lt;")
            ret += "<" + line + ">" + "\n"
        return ret


def build_xml(primitive, parent=None):
    if parent is None:
        parent = getattr(ElementMaker(), XML_ROOT)()
    # normalize element name
    if elem_name := _pluralizer.singular(parent.tag):
        parent.tag = elem_name
    for field_name, data in primitive.items():
        primitive_to_xml(field_name, data, parent)
    return parent


def primitive_to_xml(field_name, data, parent):
    if isinstance(data, dict):
        _parent = getattr(ElementMaker(), field_name)()
        parent.append(build_xml(data, _parent))
    elif isinstance(data, list):
        for d in data:
            primitive_to_xml(field_name, d, parent)
    else:
        # handle long-summary
        if field_name == "line":
            child = Element("line")
            child.text = str(data)
            parent.append(child)
        # store metadata as attributes
        elif prev := parent.get(field_name):
            curr = " ".join(sorted(f"{prev} {data}".split(), key=len, reverse=True))
            parent.set(field_name, curr)
        else:
            parent.set(field_name, str(data))


def build_model(model, primitive):
    if hasattr(model, "_field_list"):
        instance = model()
        for field_name, field in model._field_list:
            if isinstance(field, Serializable):
                continue
            serialized_name = field.serialized_name or field_name
            # obtain suitable element name
            if serialized_name in primitive:
                curr_name = serialized_name
            elif (elem_name := _pluralizer.singular(serialized_name)) in primitive:
                curr_name = elem_name
            else:
                continue
            data = primitive[curr_name]
            curr_field = _unwrap(field)
            field_value = obtain_field_value(field, curr_field, data)
            setattr(instance, field_name, field_value)
        return instance
    else:
        # handle primitive field
        if model.primitive_type is not None:
            cast = model.primitive_type
        elif isinstance(model, CMDPrimitiveField):
            cast = model.convert_from_xml
        else:
            raise NotImplementedError(f"Cannot convert value from xml for field type: {type(model)}")
        return cast(primitive)


def obtain_field_value(prev, curr, data):
    if isinstance(prev, ListType):
        field_value = []
        # filter long-summary and singular options
        if " " in data and curr.parent_field.name not in {"lines", "singular_options"}:
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


def _unwrap(field):
    if isinstance(field, ListType):
        return _unwrap(field.field)
    elif isinstance(field, ModelType):
        return field.model_class
    else:
        return field


_pluralizer = Pluralizer()
