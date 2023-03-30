

class AAZErrorFormatEnum:

    ODataV4Format = "ODataV4Format"  # registered in azure.cli.core.aaz._error_format
    MgmtErrorFormat = "MgmtErrorFormat"  # registered in azure.cli.core.aaz._error_format

    @classmethod
    def validate(cls, format):
        return format in (cls.ODataV4Format, cls.MgmtErrorFormat)

    @classmethod
    def classify_error_format(cls, builder, schema):
        from command.model.configuration import CMDObjectSchemaBase, CMDObjectSchema, CMDClsSchemaBase
        if isinstance(schema, CMDClsSchemaBase):
            schema = builder.get_cls_definition_model(schema)
        if not isinstance(schema, CMDObjectSchemaBase) or not schema.props:
            return None

        props = {}
        for prop in schema.props:
            props[prop.name] = prop

        if "error" in props:
            schema = props['error']
            if isinstance(schema, CMDClsSchemaBase):
                schema = builder.get_cls_definition_model(schema)
            if not isinstance(schema, CMDObjectSchemaBase):
                return None

        prop_keys = set()
        for prop in schema.props:
            prop_keys.add(prop.name)

        if not ("code" in prop_keys and "message" in prop_keys):
            # code and message is required
            return None

        prop_keys.difference_update({"code", "message", "target", "details", "innerError", "innererror"})  # some api use "innerError" instead of "innererror"
        if len(prop_keys) == 0:
            return cls.ODataV4Format
        if prop_keys == {"additionalInfo"}:
            return cls.MgmtErrorFormat

        return None
