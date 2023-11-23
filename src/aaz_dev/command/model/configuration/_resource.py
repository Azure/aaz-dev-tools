from schematics.models import Model
from schematics.types import StringType

from ._fields import CMDResourceIdField, CMDVersionField
from ._utils import CMDDiffLevelEnum
from utils.base64 import b64decode_str


class CMDResource(Model):
    # properties as tags
    id = CMDResourceIdField(required=True)
    version = CMDVersionField(required=True)
    subresource = StringType()  # subresource index, used for sub commands generation.

    swagger = StringType(required=True)  # swagger resource provider, <plane>/<path:mod_names>/ResourceProviders/<rp_name>/Paths/<base64Encoded Path>/V/<base64Encoded version>

    class Options:
        serialize_when_none = False

    @property
    def plane(self):
        return self.swagger.split('/')[0]

    @property
    def mod_names(self):
        return self.swagger.split("/ResourceProviders/")[0].split('/')[1:]

    @property
    def rp_name(self):
        return self.swagger.split("/ResourceProviders/")[1].split('/')[0]

    @property
    def swagger_path(self):
        return b64decode_str(self.swagger.split("/Paths/")[1].split('/')[0])

    def diff(self, old, level):
        if type(self) is not type(old):
            return f"Type: {type(old)} != {type(self)}"
        diff = {}
        if level >= CMDDiffLevelEnum.BreakingChange:
            if self.id != old.id:
                diff["id"] = f"{old.id} != {self.id}"
            if self.version != old.version:
                diff["version"] = f"{old.version} != {self.version}"
            if self.subresource != old.subresource:
                diff["subresource"] = f"{old.subresource} != {self.subresource}"
            if self.plane != old.plane:
                diff["plane"] = f"{old.plane} != {self.plane}"
            if self.rp_name != old.rp_name:
                diff["rp_name"] = f"{old.rp_name} != {self.rp_name}"

        if level >= CMDDiffLevelEnum.Structure:
            if self.mod_names != old.mod_names:
                diff["mod_names"] = f"{old.mod_names} != {self.mod_names}"
            if self.swagger_path != old.swagger_path:
                diff["swagger_path"] = f"{old.swagger_path} != {self.swagger_path}"

        return diff
