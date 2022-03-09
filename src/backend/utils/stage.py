from schematics.types import StringType


class AAZStageEnum:
    Experimental = "Experimental"
    Preview = "Preview"
    Stable = "Stable"


class AAZStageField(StringType):
    """The stage for command group, command or argument."""

    def __init__(self, *args, **kwargs):
        super().__init__(
            choices=(AAZStageEnum.Experimental, AAZStageEnum.Preview, AAZStageEnum.Stable),
            default=AAZStageEnum.Stable,
            serialize_when_none=False,
            *args,
            **kwargs
        )
