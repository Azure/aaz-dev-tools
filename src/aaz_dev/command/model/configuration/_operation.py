from schematics.models import Model
from schematics.types import PolyModelType, ModelType, ListType, StringType

from ._fields import CMDVariantField, CMDDescriptionField
from ._http import CMDHttpAction
from ._instance_update import CMDInstanceUpdateAction
from ._instance_create import CMDInstanceCreateAction
from ._instance_delete import CMDInstanceDeleteAction


class CMDOperation(Model):
    POLYMORPHIC_KEY = None

    # properties as tags
    when = ListType(CMDVariantField())  # conditions

    class Options:
        serialize_when_none = False

    @classmethod
    def _claim_polymorphic(cls, data):
        if cls.POLYMORPHIC_KEY is None:
            return False

        if isinstance(data, dict):
            return cls.POLYMORPHIC_KEY in data
        elif isinstance(data, CMDOperation):
            return hasattr(data, cls.POLYMORPHIC_KEY)
        return False

    def generate_args(self, ref_args, has_subresource):
        raise NotImplementedError()

    def reformat(self, **kwargs):
        raise NotImplementedError()

    def register_cls(self, **kwargs):
        return NotImplementedError()


class CMDHttpOperationLongRunning(Model):
    # properties as tags
    final_state_via = StringType(
        choices=(
            'azure-async-operation',
            # (default if not specified) poll until terminal state, the final response will be available at the uri pointed to by the header Azure-AsyncOperation
            'location',
            # poll until terminal state, the final response will be available at the uri pointed to by the header Location
            'original-uri'
            # poll until terminal state, the final response will be available via GET at the original resource URI. Very common for PUT operations.
        ),
        default='azure-async-operation',
        serialized_name='finalStateVia',
        deserialize_from='finalStateVia',
    )


class CMDHttpOperation(CMDOperation):
    POLYMORPHIC_KEY = "http"

    # properties as tags
    long_running = ModelType(
        CMDHttpOperationLongRunning,
        serialized_name="longRunning",
        deserialize_from="longRunning",
    )

    operation_id = StringType(
        serialized_name="operationId",
        deserialize_from="operationId",
        required=True
    )   # OperationId from swagger

    description = CMDDescriptionField()

    # properties as nodes
    http = ModelType(CMDHttpAction, required=True)

    def generate_args(self, ref_args, has_subresource):
        return self.http.generate_args(ref_args=ref_args, has_subresource=has_subresource)

    def reformat(self, **kwargs):
        self.http.reformat(**kwargs)

    def register_cls(self, **kwargs):
        self.http.register_cls(**kwargs)


class CMDInstanceCreateOperation(CMDOperation):
    POLYMORPHIC_KEY = "instanceCreate"

    instance_create = PolyModelType(
        CMDInstanceCreateAction,
        allow_subclasses=True,
        required=True,
        serialized_name="instanceCreate",
        deserialize_from="instanceCreate"
    )

    def generate_args(self, ref_args, has_subresource):
        return self.instance_create.generate_args(ref_args=ref_args)

    def reformat(self, **kwargs):
        self.instance_create.reformat(**kwargs)

    def register_cls(self, **kwargs):
        self.instance_create.register_cls(**kwargs)


class CMDInstanceUpdateOperation(CMDOperation):
    POLYMORPHIC_KEY = "instanceUpdate"

    # properties as nodes
    instance_update = PolyModelType(
        CMDInstanceUpdateAction,
        allow_subclasses=True,
        required=True,
        serialized_name="instanceUpdate",
        deserialize_from="instanceUpdate"
    )

    def generate_args(self, ref_args, has_subresource):
        return self.instance_update.generate_args(ref_args=ref_args)

    def reformat(self, **kwargs):
        self.instance_update.reformat(**kwargs)

    def register_cls(self, **kwargs):
        self.instance_update.register_cls(**kwargs)


class CMDInstanceDeleteOperation(CMDOperation):
    POLYMORPHIC_KEY = "instanceDelete"

    instance_delete = PolyModelType(
        CMDInstanceDeleteAction,
        allow_subclasses=True,
        required=True,
        serialized_name="instanceDelete",
        deserialize_from="instanceDelete"
    )

    def generate_args(self, ref_args, has_subresource):
        return self.instance_delete.generate_args(ref_args=ref_args)

    def reformat(self, **kwargs):
        self.instance_delete.reformat(**kwargs)

    def register_cls(self, **kwargs):
        self.instance_delete.register_cls(**kwargs)
