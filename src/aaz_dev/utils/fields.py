from schematics.types import StringType
from utils.plane import PlaneEnum


class PlaneField(StringType):

    def __init__(self, *args, **kwargs):
        super(PlaneField, self).__init__(
            regex=r'^({})|({}:[a-z0-9_\-.]+)$'.format(PlaneEnum.Mgmt, PlaneEnum._Data),
            *args, **kwargs
        )


__all__ = ["PlaneField"]
