from schematics.models import Model
from schematics.types import PolyModelType, ListType
from schematics.types.serializable import serializable

from ._fields import CMDVariantField


class CMDConditionOperator(Model):
    # properties as tags
    TYPE_VALUE = None

    @serializable
    def type(self):
        return self._get_type()

    def _get_type(self):
        assert self.TYPE_VALUE is not None
        return self.TYPE_VALUE

    @classmethod
    def _claim_polymorphic(cls, data):
        if cls.TYPE_VALUE is None:
            return False

        if isinstance(data, dict):
            type_value = data.get('type', None)
            return type_value == cls.TYPE_VALUE
        elif isinstance(data, CMDConditionOperator):
            return data.TYPE_VALUE == cls.TYPE_VALUE
        return False


class CMDConditionAndOperator(CMDConditionOperator):
    TYPE_VALUE = "and"

    # properties as nodes
    operators = ListType(PolyModelType(CMDConditionOperator, allow_subclasses=True), min_size=2)


class CMDConditionOrOperator(CMDConditionOperator):
    TYPE_VALUE = "or"

    operators = ListType(PolyModelType(CMDConditionOperator, allow_subclasses=True), min_size=2)


class CMDConditionNotOperator(CMDConditionOperator):
    TYPE_VALUE = "not"

    # properties as nodes
    operator = PolyModelType(CMDConditionOperator, allow_subclasses=True, required=True)


class CMDConditionHasValueOperator(CMDConditionOperator):
    TYPE_VALUE = "hasValue"

    # properties as tags
    arg = CMDVariantField(required=True)


class CMDCondition(Model):
    # properties as tags
    var = CMDVariantField(required=True)  # define variant

    # properties as nodes
    operator = PolyModelType(CMDConditionOperator, allow_subclasses=True, required=True)
