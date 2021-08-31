from schematics.models import Model
from schematics.types import StringType


class Linkable:

    def __init__(self):
        self._linked = False

    def is_linked(self):
        if not hasattr(self, '_linked'):
            self._linked = False
        return self._linked

    def link(self, swagger_loader, file_path, *traces):
        self._linked = True


class ReferenceType(StringType):

    def __init__(self, serialized_name="$ref", deserialize_from="$ref", **kwargs):

        super(ReferenceType, self).__init__(
            serialized_name=serialized_name,
            deserialize_from=deserialize_from,
            **kwargs
        )


class Reference(Model, Linkable):
    """A simple object to allow referencing other definitions in the specification. It can be used to reference parameters and responses that are defined at the top level for reuse."""

    ref = ReferenceType(required=True)  # The reference string

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ref_instance = None

    def link(self, swagger_loader, file_path, *traces):
        if self.is_linked():
            return
        super().link(swagger_loader, file_path, *traces)

        self.ref_instance, path, ref_key = swagger_loader.load_ref(file_path, self.ref)
        if isinstance(self.ref_instance, Linkable):
            self.ref_instance.link(swagger_loader, path, *traces, ref_key)

    @classmethod
    def _claim_polymorphic(cls, data):
        return isinstance(data, dict) and "$ref" in data
