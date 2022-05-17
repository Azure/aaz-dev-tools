from schematics.models import Model
from schematics.types import StringType

from ._fields import CMDResourceIdField, CMDVersionField
from utils.base64 import b64decode_str


class CMDResource(Model):
    # properties as tags
    id = CMDResourceIdField(required=True)
    version = CMDVersionField(required=True)

    swagger = StringType(required=True)  # swagger resource provider, /<plane>/<path:mod_names>/ResourceProviders/<rp_name>/Paths/<base64Encoded Path>/V/<base64Encoded version>

    @property
    def plane(self):
        return self.swagger.split('/')[1]

    @property
    def mod_names(self):
        return self.swagger.split('/')[2:-6]

    @property
    def rp_name(self):
        return self.swagger.split('/')[-5]

    @property
    def swagger_path(self):
        return b64decode_str(self.swagger.split('/')[-3])
