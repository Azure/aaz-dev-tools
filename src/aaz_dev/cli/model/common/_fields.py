from command.model.configuration import CMDCommand, CMDClientConfig
from schematics.types import StringType, ModelType, BooleanType
from utils.config import Config


class CLIProfileNameField(StringType):
    """The stage for command group, command or argument."""

    def __init__(self, *args, **kwargs):
        super().__init__(
            choices=tuple(Config.CLI_PROFILES),
            default=Config.CLI_DEFAULT_PROFILE,
            serialize_when_none=False,
            *args,
            **kwargs
        )


class CLICommandNameField(StringType):

    def __init__(self, *args, **kwargs):
        super().__init__(
            regex=r'^[a-z0-9]+(-[a-z0-9]+)*$',
            min_length=1, *args, **kwargs)


class CLICommandConfigurationField(ModelType):

    def __init__(self, *args, **kwargs):
        super().__init__(
            CMDCommand,
            serialize_when_none=False,
        )

    def to_primitive(self, value, context=None):
        return None  # return None when value is false to hide field with `serialize_when_none=False`


class CLIVersionField(StringType):

    def __init__(self, *args, **kwargs):
        super(CLIVersionField, self).__init__(*args, **kwargs)


class CLIResourceIdField(StringType):

    def __init__(self, *args, **kwargs):
        super(CLIResourceIdField, self).__init__(
            serialized_name='id',
            deserialize_from='id',
            *args, **kwargs
        )


class CLIModifiedField(BooleanType):

    def to_primitive(self, value, context=None):
        # ignore modified value when using to primitive
        return None


class CLIClientConfigField(ModelType):

    def __init__(self, *args, **kwargs):
        super().__init__(
            CMDClientConfig,
            serialize_when_none=False,
        )

    def to_primitive(self, value, context=None):
        return None  # return None when value is false to hide field with `serialize_when_none=False`
