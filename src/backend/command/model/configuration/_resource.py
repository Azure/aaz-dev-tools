from schematics.models import Model
from schematics.types import StringType

from ._fields import CMDResourceIdField, CMDVersionField


class CMDResource(Model):
    # properties as tags
    id = CMDResourceIdField(required=True)
    version = CMDVersionField(required=True)

    provider = StringType(required=True)  # swagger resource provider, /<plane>/<path:mod_names>/resource-providers/<rp_name>
