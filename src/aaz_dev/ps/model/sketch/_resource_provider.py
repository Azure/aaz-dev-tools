from schematics.models import Model
from schematics.types import StringType, ListType, ModelType
from ._resource import PSSketchResource


class PSSketchResourceProvider(Model):

    resources = ListType(ModelType(PSSketchResource))
    swagger = StringType(required=True) # swagger resource provider, <plane>/<path:mod_names>/ResourceProviders/<rp_name>

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
