

class AAZErrorFormatEnum:

    ODataV4Format = "ODataV4Format"  # registered in n azure.cli.core.aaz._error_format
    MgmtErrorFormat = "MgmtErrorFormat"

    @classmethod
    def classify_error_format(cls, builder, schema):
        from command.model.configuration import CMDObjectSchemaBase, CMDObjectSchema, CMDClsSchemaBase
        if isinstance(schema, CMDClsSchemaBase):
            schema = builder.get_cls_definition_model(schema)
        if not isinstance(schema, CMDObjectSchemaBase):
            return None

        props = {}
        for prop in schema.props:
            props[prop.name] = prop
        if "error" not in props:
            return None

        schema = props['error']
        if isinstance(schema, CMDClsSchemaBase):
            schema = builder.get_cls_definition_model(schema)
        if not isinstance(schema, CMDObjectSchema):
            return None

        prop_keys = set()
        for prop in schema.props:
            prop_keys.add(prop.name)
        if prop_keys == {"code", "message", "target", "details"}:
            return cls.ODataV4Format
        if prop_keys == {"code", "message", "target", "details", "additionalInfo"}:
            return cls.MgmtErrorFormat

        return None
