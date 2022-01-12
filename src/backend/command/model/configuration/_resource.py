from schematics.models import Model
from schematics.types import StringType
from utils.fields import PlaneField

from ._fields import CMDResourceIdField, CMDVersionField


class CMDResource(Model):
    # properties as tags
    id = CMDResourceIdField(required=True)
    version = CMDVersionField(required=True)

    plane = PlaneField()
    swagger = StringType(required=True)  # swagger path, /<plane>/<path:mod_names>/resource-providers/<rp_name>/resources/<resource_id>/v/<version>
