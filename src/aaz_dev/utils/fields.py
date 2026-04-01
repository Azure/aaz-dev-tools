import typing
from typing import Any
from schematics.types import StringType
from utils.plane import PlaneEnum
from utils.client import CloudEnum


class PlaneField(StringType):

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(
            regex=r'^({})|({}:[a-z0-9_\-.]+)$'.format(PlaneEnum.Mgmt, PlaneEnum._Data),
            *args, **kwargs
        )


class CloudField(StringType):

    def __init__(self, *args: Any, **kwargs: Any) -> None:
         super().__init__(
            choices=CloudEnum.choices(),
            *args, **kwargs
        )


__all__ = ["PlaneField"]
