from schematics.models import Model
from schematics.types import StringType
from uuid import uuid4


class Linkable:

    def __init__(self):
        self._linked = False
        self.traces = None
        self._random_uuid = uuid4()

    def is_linked(self):
        if not hasattr(self, '_linked'):
            self._linked = False
        return self._linked

    def link(self, swagger_loader, *traces, **kwargs):
        self._linked = True
        assert len(traces) > 0
        self.traces = tuple(traces)
        for trace in self.traces:
            assert isinstance(trace, (str, int))

    def __hash__(self):
        return hash(self._random_uuid)


class ReferenceField(StringType):

    def __init__(self, serialized_name="$ref", deserialize_from="$ref", **kwargs):

        super(ReferenceField, self).__init__(
            serialized_name=serialized_name,
            deserialize_from=deserialize_from,
            **kwargs
        )


class Reference(Model, Linkable):
    """A simple object to allow referencing other definitions in the specification. It can be used to reference parameters and responses that are defined at the top level for reuse."""

    ref = ReferenceField(required=True)  # The reference string

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ref_instance = None

    def link(self, swagger_loader, *traces, **kwargs):
        if self.is_linked():
            return
        super().link(swagger_loader, *traces, **kwargs)

        self.ref_instance, instance_traces = swagger_loader.load_ref(self.ref, *self.traces, 'ref')
        if isinstance(self.ref_instance, Linkable):
            self.ref_instance.link(swagger_loader, *instance_traces, **kwargs)

    @classmethod
    def _claim_polymorphic(cls, data):
        return isinstance(data, dict) and "$ref" in data and len(data) == 1
