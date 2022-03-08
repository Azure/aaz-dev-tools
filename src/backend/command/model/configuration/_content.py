from schematics.models import Model
from schematics.types import PolyModelType

from ._arg_builder import CMDArgBuilder
from ._fields import CMDVariantField
from ._schema import CMDSchemaBaseField, CMDSchema
from ._utils import CMDDiffLevelEnum


class CMDRequestJson(Model):
    """Used for Request Body and Instance Update operation"""

    # properties as tags
    ref = CMDVariantField()

    # properties as nodes
    schema = PolyModelType(CMDSchema, allow_subclasses=True)

    class Options:
        serialize_when_none = False

    def generate_args(self):
        if not self.schema:
            return []
        assert isinstance(self.schema, CMDSchema)
        builder = CMDArgBuilder.new_builder(schema=self.schema)
        args = builder.get_args()
        return args

    def diff(self, old, level):
        diff = {}
        if level >= CMDDiffLevelEnum.BreakingChange:
            if (self.ref is not None) != (old.ref is not None):
                diff["ref"] = f"{old.ref} != {self.ref}"
            schema_diff = self.schema.diff(old.schema, level)
            if schema_diff:
                diff["schema"] = schema_diff

        if level >= CMDDiffLevelEnum.Associate:
            if self.ref != old.ref:
                diff["ref"] = f"{old.ref} != {self.ref}"
        return diff

    def reformat(self, schema_cls_map, **kwargs):
        # TODO:
        pass


class CMDResponseJson(Model):
    # properties as tags
    var = CMDVariantField()

    # properties as nodes
    schema = CMDSchemaBaseField(required=True)

    class Options:
        serialize_when_none = False

    def diff(self, old, level):
        diff = {}
        if level >= CMDDiffLevelEnum.BreakingChange:
            schema_diff = self.schema.diff(old.schema, level)
            if schema_diff:
                diff["schema"] = schema_diff

        if level >= CMDDiffLevelEnum.Associate:
            if self.var != old.var:
                diff["var"] = f"{old.var} != {self.var}"
        return diff

    def reformat(self, schema_cls_map, **kwargs):
        # TODO:
        pass
