from schematics.models import Model
from schematics.types import PolyModelType, ListType, StringType
from ._fields import CMDVariantField


class CMDConditionOperator(Model):
    # properties as tags
    TYPE_VALUE = None

    type_ = StringType(required=True)

    @classmethod
    def _claim_polymorphic(cls, data):
        if isinstance(data, dict):
            type_value = data.get('type', None)
            if type_value is not None:
                typ = type_value.replace("<", " ").replace(">", " ").strip().split()[0]
                return typ == cls.TYPE_VALUE
        return False


class CMDConditionAndOperator(CMDConditionOperator):
    TYPE_VALUE = "and"

    # properties as nodes
    operators = ListType(PolyModelType(CMDConditionOperator, allow_subclasses=True))


class CMDConditionOrOperator(CMDConditionOperator):
    TYPE_VALUE = "or"

    operators = ListType(PolyModelType(CMDConditionOperator, allow_subclasses=True))


class CMDConditionNotOperator(CMDConditionOperator):
    TYPE_VALUE = "not"

    # properties as nodes
    operator = PolyModelType(CMDConditionOperator, allow_subclasses=True)


class CMDConditionHasValueOperator(CMDConditionOperator):
    TYPE_VALUE = "hasValue"

    # properties as tags
    arg = CMDVariantField(required=True)


class CMDCondition(Model):
    # properties as tags
    var = CMDVariantField()  # define variant

    # properties as nodes
    operator = PolyModelType(CMDConditionOperator, allow_subclasses=True)
