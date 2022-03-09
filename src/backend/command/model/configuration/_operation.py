from schematics.models import Model
from schematics.types import PolyModelType, ModelType, ListType, StringType

from ._fields import CMDVariantField, CMDBooleanField, CMDDescriptionField
from ._http import CMDHttpAction
from ._instance_update import CMDInstanceUpdateAction


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

    def generate_args(self):
        raise NotImplementedError()

    def reformat(self, **kwargs):
        raise NotImplementedError()


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

    def generate_args(self):
        return self.http.generate_args()

    def reformat(self, **kwargs):
        self.http.reformat(**kwargs)


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

    def generate_args(self):
        return self.instance_update.generate_args()

    def reformat(self, **kwargs):
        self.instance_update.reformat(**kwargs)
