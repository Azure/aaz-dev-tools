from schematics.models import Model
from schematics.types import StringType, ModelType, BooleanType


class XmsLongRunningOperationField(BooleanType):
    """
    Some requests like creating/deleting a resource cannot be carried out immediately. In such a situation, the server sends a 201 (Created) or 202 (Accepted) and provides a link to monitor the status of the request. When such an operation is marked with extension "x-ms-long-running-operation": true, in OpenAPI, the generated code will know how to fetch the link to monitor the status. It will keep on polling at regular intervals till the request reaches one of the terminal states: Succeeded, Failed, or Canceled.

    https://github.com/Azure/autorest/blob/main/docs/extensions/readme.md#x-ms-long-running-operation
    """

    def __init__(self, **kwargs):
        super(XmsLongRunningOperationField, self).__init__(
            serialized_name='x-ms-long-running-operation',
            deserialize_from='x-ms-long-running-operation',
            **kwargs
        )


class XmsLongRunningOperationOptions(Model):
    """
    When x-ms-long-running-operation is specified, there should also be a x-ms-long-running-operation-options specified.

    See Azure RPC Spec for asynchronous operation notes.

    https://github.com/Azure/autorest/blob/main/docs/extensions/readme.md#x-ms-long-running-operation-options

    It will keep on polling at regular intervals till the request reaches one of the terminal states: Succeeded, Failed, or Canceled.
    """

    final_state_via = StringType(
        choices=(
            'azure-async-operation',  # (default if not specified) poll until terminal state, the final response will be available at the uri pointed to by the header Azure-AsyncOperation
            'location',  # poll until terminal state, the final response will be available at the uri pointed to by the header Location
            'original-uri'  # poll until terminal state, the final response will be available via GET at the original resource URI. Very common for PUT operations.
        ), default='azure-async-operation',
        serialized_name='final-state-via',
        deserialize_from='final-state-via',
    )

    final_state_schema = StringType(
        serialized_name="final-state-schema",
        deserialize_from="final-state-schema",
    )


class XmsLongRunningOperationOptionsField(ModelType):

    def __init__(self, **kwargs):
        super(XmsLongRunningOperationOptionsField, self).__init__(
            XmsLongRunningOperationOptions,
            serialized_name='x-ms-long-running-operation-options',
            deserialize_from='x-ms-long-running-operation-options',
            **kwargs
        )
