# -*- coding: utf-8 -*-
"""
    schematics_xml.models
    ~~~~~~~~~~~~~~~~~~~~~

    Base models that provide to/from XML methods.
"""

import collections
import numbers

import lxml.builder
import lxml.etree
from schematics import Model
from schematics.types import BaseType, ModelType, CompoundType, ListType, DictType
from schematics.types.base import MultilingualStringType
from schematics.types.compound import PolyModelType
from xmltodict import parse


class XMLModel(Model):
    """
    A model that can convert it's fields to and from XML.
    """
    @property
    def xml_root(self) -> str:
        """
        Override this attribute to set the XML root returned by :py:meth:`.XMLModel.to_xml`.
        """
        return type(self).__name__.lower()

    #: Override this attribute to set the encoding specified in the XML returned by :py:meth:`.XMLModel.to_xml`.
    xml_encoding = 'UTF-8'

    def to_xml(self, role: str=None, app_data: dict=None, encoding: str=None, **kwargs) -> str:
        """
        Return a string of XML that represents this model.

        Currently all arguments are passed through to schematics.Model.to_primitive.

        :param role: schematics Model to_primitive role parameter.
        :param app_data: schematics Model to_primitive app_data parameter.
        :param encoding: xml encoding attribute string.
        :param kwargs: schematics Model to_primitive kwargs parameter.
        """
        primitive = self.to_primitive(role=role, app_data=app_data, **kwargs)
        root = self.primitive_to_xml(primitive)
        return lxml.etree.tostring(  # pylint: disable=no-member
            root,
            pretty_print=True,
            xml_declaration=True,
            encoding=encoding or self.xml_encoding
        )

    def primitive_to_xml(self, primitive: dict, parent: 'lxml.etree._Element'=None):
        element_maker = lxml.builder.ElementMaker()

        if parent is None:
            parent = getattr(element_maker, self.xml_root)()

        for key, value in primitive.items():
            self.primitive_value_to_xml(key, parent, value)

        return parent

    def primitive_value_to_xml(self, key, parent, value):
        element_maker = lxml.builder.ElementMaker()

        if isinstance(value, bool):
            parent.append(getattr(element_maker, key)('1' if value else '0'))

        elif isinstance(value, numbers.Number) or isinstance(value, str):
            parent.append(getattr(element_maker, key)(str(value)))

        elif value is None:
            parent.append(getattr(element_maker, key)(''))

        elif isinstance(value, dict):
            _parent = getattr(element_maker, key)()
            parent.append(self.primitive_to_xml(value, _parent))

        elif isinstance(value, collections.abc.Iterable):
            for _value in value:
                self.primitive_value_to_xml(key, parent, _value)

        else:
            raise TypeError('Unsupported data type: %s (%s)' % (value, type(value).__name__))

    @classmethod
    def from_xml(cls, primitive) -> Model:
        """
        Convert XML into a model.

        :param primitive: A string of XML that represents this Model.
        """
        if model_has_field_type(MultilingualStringType, cls):
            raise NotImplementedError("Field type 'MultilingualStringType' is not supported.")
        primitive = parse(xml)
        if len(primitive) != 1:
            raise NotImplementedError
        for _, raw_data in primitive.items():
            if model_has_field_type(ListType, cls):
                # We need to ensure that single item lists are actually lists and not dicts
                raw_data = ensure_lists_in_model(raw_data, cls)
            return cls(raw_data=raw_data)


def model_has_field_type(needle: BaseType, haystack: Model) -> bool:
    """
    Return True if haystack contains a field of type needle.

    Iterates over all fields (and into field if appropriate) and searches for field type *needle* in model
    *haystack*.

    :param needle: A schematics field class to search for.
    :param haystack: A schematics model to search within.
    """
    for _, field in haystack._field_list:  # pylint: disable=protected-access
        if field_has_type(needle, field):
            return True
    return False


def field_has_type(needle: BaseType, field: BaseType) -> bool:  # pylint: disable=too-many-return-statements, too-many-branches
    """
    Return True if field haystack contains a field of type needle.

    :param needle: A schematics field class to search for.
    :param haystack: An instance of a schematics field within a model.
    """
    if isinstance(field, needle):
        return True

    elif isinstance(field, ModelType):
        if model_has_field_type(needle, field.model_class):
            return True

    elif isinstance(field, PolyModelType):
        if needle in [type(obj) for obj in field.model_classes]:
            return True

        for obj in [obj for obj in field.model_classes if isinstance(obj, ModelType)]:
            if model_has_field_type(needle, obj.model_class):
                return True

    elif isinstance(field, CompoundType):
        if needle == type(field.field):
            return True

        try:
            if needle == field.model_class:
                return True

        except AttributeError:
            pass

        else:
            if model_has_field_type(needle, field.model_class):
                return True

        if field_has_type(needle, field.field):
            return True

    return False


def ensure_lists_in_model(raw_data: dict, model_cls: XMLModel):
    """
    Ensure that single item lists are represented as lists and not dicts.

    In XML single item lists are converted to dicts by xmltodict - there is essentially no
    way for xmltodict to know that it *should* be a list not a dict.

    :param raw_data:
    :param model_cls:
    """
    if not model_has_field_type(ListType, model_cls):
        return raw_data

    for _, field in model_cls._field_list:  # pylint: disable=protected-access
        key = field.serialized_name or field.name
        try:
            value = raw_data[key]
        except KeyError:
            continue

        raw_data[key] = ensure_lists_in_value(value, field)

    return raw_data


def ensure_lists_in_value(value: 'typing.Any', field: BaseType):

    if value is None:
        # Don't turn None items into a list of None items
        return None

    if isinstance(field, ListType):
        if not isinstance(value, list):
            value = [
                ensure_lists_in_value(value, field.field)
            ]
        elif field_has_type(ListType, field.field):
            value = [
                ensure_lists_in_value(_value, field.field)
                for _value in value
            ]

    elif field_has_type(ListType, field):
        if isinstance(field, DictType):
            for _key, _value in value.items():
                value[_key] = ensure_lists_in_value(_value, field.field)

        elif isinstance(field, ModelType):
            value = ensure_lists_in_model(value, field.model_class)

    return value
