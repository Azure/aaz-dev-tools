from schematics.models import Model
from schematics.types import StringType, PolyModelType, ListType

from ._arg import CMDArg, CMDClsArgBase, CMDObjectArgBase, CMDArrayArgBase
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

    def register_cls(self, cls_register_map):
        if self.args:
            for arg in self.args:
                _iter_over_arg_for_cls_register(arg, cls_register_map)


def _iter_over_arg_for_cls_register(arg, cls_register_map):
    if arg is None:
        return

    if isinstance(arg, CMDClsArgBase):
        cls_name = arg.type[1:]
        if cls_name not in cls_register_map:
            cls_register_map[cls_name] = {
                "implement": None,
                "refers": []
            }
        cls_register_map[cls_name]['refers'].append(arg)
        return

    if getattr(arg, 'cls', None):
        cls_name = arg.cls
        if cls_name not in cls_register_map:
            cls_register_map[cls_name] = {
                "implement": None,
                "refers": []
            }
        cls_register_map[cls_name]['implement'] = arg

    if isinstance(arg, CMDObjectArgBase):
        if arg.args:
            for sub_arg in arg.args:
                _iter_over_arg_for_cls_register(sub_arg, cls_register_map)

        if arg.additional_props and arg.additional_props.item:
            _iter_over_arg_for_cls_register(arg.additional_props.item, cls_register_map)

    elif isinstance(arg, CMDArrayArgBase):
        _iter_over_arg_for_cls_register(arg.item, cls_register_map)
