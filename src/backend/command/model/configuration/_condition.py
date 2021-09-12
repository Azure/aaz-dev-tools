from schematics.models import Model
from ._fields import CMDVariantField


class CMDCondition(Model):
    # properties as tags
    var = CMDVariantField()  # define variant
    ref = CMDVariantField()  # reference variant

    # properties as nodes
    # TODO:
