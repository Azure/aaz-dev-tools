from schematics.models import Model
from schematics.types import ModelType, ListType, DictType
# from .reference import ReferenceType
from .operation import Operation
from .parameter import ParameterType


class PathItem(Model):
    """Describes the operations available on a single path. A Path Item may be empty, due to ACL constraints. The path itself is still exposed to the documentation viewer but they will not know which operations and parameters are available"""

    get = ModelType(Operation)  # A definition of a GET operation on this path.
    put = ModelType(Operation)  # A definition of a PUT operation on this path.
    post = ModelType(Operation)  # A definition of a POST operation on this path.
    delete = ModelType(Operation)  # A definition of a DELETE operation on this path.
    options = ModelType(Operation)  # A definition of a OPTIONS operation on this path.
    head = ModelType(Operation)  # A definition of a HEAD operation on this path.
    patch = ModelType(Operation)  # A definition of a PATCH operation on this path.

    parameters = ListType(ParameterType(support_reference=True))  # A list of parameters that are applicable for all the operations described under this path. These parameters can be overridden at the operation level, but cannot be removed there. The list MUST NOT include duplicated parameters. A unique parameter is defined by a combination of a name and location. The list can use the Reference Object to link to parameters that are defined at the Swagger Object's parameters. There can be one "body" parameter at most.

    # ignored because it is not used
    # ref = ReferenceType()  # Allows for an external definition of this path item. The referenced structure MUST be in the format of a Path Item Object. If there are conflicts between the referenced definition and this Path Item's definition, the behavior is undefined.

    def unfold(self, ref_loader):
        if self.get is not None:
            self.get.unfold(ref_loader)
        if self.put is not None:
            self.put.unfold(ref_loader)
        if self.post is not None:
            self.post.unfold(ref_loader)
        if self.delete is not None:
            self.delete.unfold(ref_loader)
        if self.options is not None:
            self.options.unfold(ref_loader)
        if self.head is not None:
            self.head.unfold(ref_loader)
        if self.patch is not None:
            self.patch.unfold(ref_loader)


class PathsType(DictType):

    def __init__(self, **kwargs):
        super(PathsType, self).__init__(
            ModelType(PathItem),
            **kwargs
        )


class XmsPathsType(DictType):

    """
    OpenAPI 2.0 has a built-in limitation on paths. Only one operation can be mapped to a path and http method. There are some APIs, however, where multiple distinct operations are mapped to the same path and same http method. For example GET /mypath/query-drive?op=file and GET /mypath/query-drive?op=folder may return two different model types (stream in the first example and JSON model representing Folder in the second). Since OpenAPI does not treat query parameters as part of the path the above 2 operations may not co-exist in the standard "paths" element.

    To overcome this limitation an "x-ms-paths" extension was introduced parallel to "paths". URLs under "x-ms-paths" are allowed to have query parameters for disambiguation, however they are not actually used.

    https://github.com/Azure/autorest/tree/main/docs/extensions#x-ms-paths
    """

    def __init__(self, **kwargs):
        super(XmsPathsType, self).__init__(
            ModelType(PathItem),
            serialized_name="x-ms-paths",
            deserialize_from="x-ms-paths",
            **kwargs
        )

