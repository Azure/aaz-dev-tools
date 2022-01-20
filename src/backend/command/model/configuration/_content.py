from schematics.models import Model

from ._arg_builder import CMDArgBuilder
from ._fields import CMDVariantField
from ._schema import CMDSchemaBaseField, CMDSchema, CMDSchemaBase
from ._utils import CMDDiffLevelEnum


# json
class CMDJson(Model):
    # properties as tags
    var = CMDVariantField()
    ref = CMDVariantField()

    # properties as nodes
    schema = CMDSchemaBaseField(support_schema=True)  # this property is required when ref property is None
    # Note: the schema can be CMDSchema or CMDSchemaBase.
    # For request or instance update, it's CMDSchema.
    # For response, it's CMDSchemaBase.

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

            if isinstance(self.schema, CMDSchema) and isinstance(old.schema, CMDSchema) or isinstance(self.schema, CMDSchemaBase) and isinstance(old.schema, CMDSchemaBase):
                schema_diff = self.schema.diff(old.schema, level)
                if schema_diff:
                    diff["schema"] = schema_diff
            elif self.schema is not None or old.schema is not None:
                diff["schema"] = f"Different type: {type(old.schema)} != {type(self.schema)}"

        if level >= CMDDiffLevelEnum.Associate:
            if self.var != old.var:
                diff["var"] = f"{old.var} != {self.var}"
            if self.ref != old.ref:
                diff["ref"] = f"{old.ref} != {self.ref}"
        return diff
