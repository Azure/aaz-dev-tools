from schematics.models import Model
from schematics.types import StringType, PolyModelType, ListType

from ._arg import CMDArg
from utils import exceptions


class CMDArgGroup(Model):
    # properties as tags
    name = StringType(required=True)

    # properties as nodes
    args = ListType(PolyModelType(CMDArg, allow_subclasses=True), min_size=1)

    def reformat(self, **kwargs):
        for arg in self.args:
            try:
                arg.reformat(**kwargs)
            except exceptions.VerificationError as err:
                err.payload['details'] = {
                    "type": "Argument",
                    "options": arg.options,
                    "var": arg.var,
                    "details": err.payload['details']
                }
                raise err
        self.args = sorted(self.args, key=lambda a: a.var)
