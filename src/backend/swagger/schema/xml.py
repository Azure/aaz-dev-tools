from schematics.models import Model
from schematics.types import URLType, BaseType, DictType, ModelType, BooleanType, FloatType, IntType, StringType, PolyModelType
from .types import XmsTextType


class XML(Model):
    """
    A metadata object that allows for more fine-tuned XML model definitions.
    When using arrays, XML element names are not inferred (for singular/plural forms) and the name property should be used to add that information. See examples for expected behavior.
    """

    name = StringType(serialize_when_none=False)  # Replaces the name of the element/attribute used for the described schema property. When defined within the Items Object (items), it will affect the name of the individual XML elements within the list. When defined alongside type being array (outside the items), it will affect the wrapping element and only if wrapped is true. If wrapped is false, it will be ignored.
    namespace = URLType(serialize_when_none=False)  # The URL of the namespace definition.
    prefix = StringType(serialize_when_none=False)  # The prefix to be used for the name.
    attribute = BooleanType(default=False, serialize_when_none=False)  # Declares whether the property definition translates to an attribute instead of an element. Default value is false.
    wrapped = BooleanType(default=False, serialize_when_none=False)  # MAY be used only for an array definition. Signifies whether the array is wrapped (for example, <books><book/><book/></books>) or unwrapped (<book/><book/>). Default value is false. The definition takes effect only when defined alongside type being array (outside the items).

    x_ms_text = XmsTextType(serialize_when_none=False)
