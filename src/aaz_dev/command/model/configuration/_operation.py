from schematics.models import Model
from schematics.types import PolyModelType, ModelType, ListType, StringType

from ._fields import CMDVariantField, CMDDescriptionField
from ._http import CMDHttpAction
from ._instance_update import CMDInstanceUpdateAction
from ._instance_create import CMDInstanceCreateAction
from ._instance_delete import CMDInstanceDeleteAction
from ._utils import CMDDiffLevelEnum


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

    def generate_args(self, ref_args, has_subresource, var_prefix=None):
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

    def diff(self, old, level):
        if type(self) is not type(old):
            return f"Type: {type(old)} != {type(self)}"
        diff = {}
        if level >= CMDDiffLevelEnum.BreakingChange:
            if self.final_state_via != old.final_state_via:
                diff["final_state_via"] = f"{old.final_state_via} != {self.final_state_via}"
        return diff


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

    def generate_args(self, ref_args, has_subresource, var_prefix=None):
        return self.http.generate_args(ref_args=ref_args, has_subresource=has_subresource, var_prefix=var_prefix)

    def reformat(self, **kwargs):
        self.http.reformat(**kwargs)

    def register_cls(self, **kwargs):
        self.http.register_cls(**kwargs)

    def diff(self, old, level):
        if type(self) is not type(old):
            return f"Type: {type(old)} != {type(self)}"
        diff = {}
        if level >= CMDDiffLevelEnum.BreakingChange:
            if (not self.long_running) != (not old.long_running):
                diff["long_running"] = "New long_running" if self.long_running else "Miss long_running"
            elif self.long_running:
                if lr_diff := self.long_running.diff(old.long_running, level):
                    diff["long_running"] = lr_diff

        if level >= CMDDiffLevelEnum.Structure:
            if self.operation_id != old.operation_id:
                diff["operation_id"] = f"{old.operation_id} != {self.operation_id}"

        if level >= CMDDiffLevelEnum.All:
            if self.description != old.description:
                diff["description"] = f"{old.description} != {self.description}"

        http_diff = self.http.diff(old.http, level)
        if http_diff:
            diff["http"] = http_diff
        return diff


class CMDInstanceCreateOperation(CMDOperation):
    POLYMORPHIC_KEY = "instanceCreate"

    instance_create = PolyModelType(
        CMDInstanceCreateAction,
        allow_subclasses=True,
        required=True,
        serialized_name="instanceCreate",
        deserialize_from="instanceCreate"
    )

    def generate_args(self, ref_args, has_subresource, var_prefix=None):
        return self.instance_create.generate_args(ref_args=ref_args, var_prefix=var_prefix)

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

    def generate_args(self, ref_args, has_subresource, var_prefix=None):
        return self.instance_update.generate_args(ref_args=ref_args, var_prefix=var_prefix)

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

    def generate_args(self, ref_args, has_subresource, var_prefix=None):
        return self.instance_delete.generate_args(ref_args=ref_args, var_prefix=var_prefix)

    def reformat(self, **kwargs):
        self.instance_delete.reformat(**kwargs)

    def register_cls(self, **kwargs):
        self.instance_delete.register_cls(**kwargs)
