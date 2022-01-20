from schematics.models import Model
from schematics.types import StringType, PolyModelType, ListType

from ._arg import CMDArg


class CMDArgGroup(Model):
    # properties as tags
    name = StringType(required=True)

    # properties as nodes
    args = ListType(PolyModelType(CMDArg, allow_subclasses=True), min_size=1)

    # def iter_args(self):
    #     for arg in self.args:
    #         yield arg
    #         if hasattr(arg, "iter_args"):
    #             for sub_arg in arg.iter_args():
    #                 yield sub_arg
