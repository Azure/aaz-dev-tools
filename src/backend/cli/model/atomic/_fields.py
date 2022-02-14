from schematics.types import StringType
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


class CLIStageEnum:
    Experimental = "Experimental"
    Preview = "Preview"
    Stable = "Stable"


class CLIStageField(StringType):

    def __init__(self, *args, **kwargs):
        super(CLIStageField, self).__init__(
            choices=(CLIStageEnum.Experimental, CLIStageEnum.Preview, CLIStageEnum.Stable),
            default=CLIStageEnum.Stable,
            serialize_when_none=False,
            *args,
            **kwargs
        )


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
