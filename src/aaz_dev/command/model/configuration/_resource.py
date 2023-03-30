from schematics.models import Model
from schematics.types import StringType

from ._fields import CMDResourceIdField, CMDVersionField
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
