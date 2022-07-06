from unittest import TestCase

from command.model.configuration._operation import *


class OperationTest(TestCase):

    def test_http_operation(self):
        operation = CMDHttpOperation({
            "when": ["$Condition_Workspaces_ListByResourceGroup", "$Condition_Workspaces_ListBySubscription"],
            "operationId": "Workspaces_ListByResourceGroup",
            "longRunning": { "finalStateVia": "azure-async-operation" },
            "http": {
                "path": "/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Databricks/workspaces",
                "request": {
                    "method": "get",
                    "path": {
                        "params": [
                            {
                                "type": "string",
                                "name": "resourceGroupName",
                                "arg": "$Path.resourceGroupName",
                                "required": True,
                                "format": {
                                    "pattern": "^[-\\w\\._\\(\\)]+$",
                                    "maxLength": 90,
                                    "minLength": 1
                                }
                            },
                            {
                                "type": "string",
                                "name": "subscriptionId",
                                "arg": "$Path.subscriptionId",
                                "required": True
                            }
                        ]
                    },
                    "query": {
                        "consts": [
                            {
                                "readOnly": True,
                                "const": True,
                                "default": {"value": "2021-04-01-preview"},
                                "type": "string",
                                "name": "api-version",
                                "required": True
                            }
                        ]
                    }
                },
                "responses": [
                    {
                        "statusCode": [200],
                        "body": {
                            "json": {
                                "var": "$Instance",
                                "schema": {
                                    "type": "object",
                                    "props": [
                                        {"type": "string", "name": "nextLink"},
                                        {
                                            "type": "array<object>",
                                            "name": "value",
                                            "item": {
                                                "type": "object",
                                                "props": [
                                                    {
                                                        "readOnly": True,
                                                        "type": "ResourceId",
                                                        "name": "id",
                                                        "format": {
                                                            "template": "/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Databricks/workspaces/{}"
                                                        }
                                                    },
                                                    {
                                                        "type": "ResourceLocation",
                                                        "name": "location",
                                                        "required": True
                                                    },
                                                    {
                                                        "readOnly": True,
                                                        "type": "string",
                                                        "name": "name"
                                                    },
                                                    {
                                                        "type": "object",
                                                        "name": "properties",
                                                        "required": True,
                                                        "props": [
                                                            {
                                                                "type": "array<object>",
                                                                "name": "authorizations",
                                                                "item": {
                                                                    "type": "object",
                                                                    "props": [
                                                                        {
                                                                            "type": "uuid",
                                                                            "name": "principalId",
                                                                            "required": True
                                                                        },
                                                                        {
                                                                            "type": "uuid",
                                                                            "name": "roleDefinitionId",
                                                                            "required": True
                                                                        }
                                                                    ]
                                                                }
                                                            },
                                                            {
                                                                "type": "object",
                                                                "name": "createdBy",
                                                                "props": [
                                                                    {
                                                                        "readOnly": True,
                                                                        "type": "uuid",
                                                                        "name": "applicationId"
                                                                    },
                                                                    {
                                                                        "readOnly": True,
                                                                        "type": "uuid",
                                                                        "name": "oid"
                                                                    },
                                                                    {
                                                                        "readOnly": True,
                                                                        "type": "string",
                                                                        "name": "puid"
                                                                    }
                                                                ],
                                                                "cls": "CreatedBy_read"
                                                            },
                                                            {
                                                                "readOnly": True,
                                                                "type": "dateTime",
                                                                "name": "createdDateTime"
                                                            },
                                                            {
                                                                "type": "object",
                                                                "name": "encryption",
                                                                "props": [
                                                                    {
                                                                        "type": "object",
                                                                        "name": "entities",
                                                                        "required": True,
                                                                        "props": [
                                                                            {
                                                                                "type": "object",
                                                                                "name": "managedServices",
                                                                                "props": [
                                                                                    {
                                                                                        "type": "string",
                                                                                        "name": "keySource",
                                                                                        "required": True,
                                                                                        "enum": {
                                                                                            "items": [
                                                                                                {
                                                                                                    "value": "Microsoft.Keyvault"
                                                                                                }
                                                                                            ]
                                                                                        }
                                                                                    },
                                                                                    {
                                                                                        "type": "object",
                                                                                        "name": "keyVaultProperties",
                                                                                        "props": [
                                                                                            {
                                                                                                "type": "string",
                                                                                                "name": "keyName",
                                                                                                "required": True
                                                                                            },
                                                                                            {
                                                                                                "type": "string",
                                                                                                "name": "keyVaultUri",
                                                                                                "required": True
                                                                                            },
                                                                                            {
                                                                                                "type": "string",
                                                                                                "name": "keyVersion",
                                                                                                "required": True
                                                                                            }
                                                                                        ]
                                                                                    }
                                                                                ]
                                                                            }
                                                                        ]
                                                                    }
                                                                ]
                                                            },
                                                            {
                                                                "type": "string",
                                                                "name": "managedResourceGroupId",
                                                                "required": True
                                                            },
                                                            {
                                                                "type": "object",
                                                                "name": "parameters",
                                                                "props": [
                                                                    {
                                                                        "type": "object",
                                                                        "name": "amlWorkspaceId",
                                                                        "props": [
                                                                            {
                                                                                "readOnly": True,
                                                                                "type": "string",
                                                                                "name": "type",
                                                                                "enum": {
                                                                                    "items": [
                                                                                        {"value": "Bool"},
                                                                                        {"value": "Object"},
                                                                                        {"value": "String"}
                                                                                    ]
                                                                                }
                                                                            },
                                                                            {
                                                                                "type": "string",
                                                                                "name": "value",
                                                                                "required": True
                                                                            }
                                                                        ],
                                                                        "cls": "WorkspaceCustomStringParameter_read"
                                                                    },
                                                                    {
                                                                        "type": "@WorkspaceCustomStringParameter_read",
                                                                        "name": "customPrivateSubnetName"
                                                                    },
                                                                    {
                                                                        "type": "@WorkspaceCustomStringParameter_read",
                                                                        "name": "customPublicSubnetName"
                                                                    },
                                                                    {
                                                                        "type": "@WorkspaceCustomStringParameter_read",
                                                                        "name": "customVirtualNetworkId"
                                                                    },
                                                                    {
                                                                        "type": "object",
                                                                        "name": "enableNoPublicIp",
                                                                        "props": [
                                                                            {
                                                                                "readOnly": True,
                                                                                "type": "string",
                                                                                "name": "type",
                                                                                "enum": {
                                                                                    "items": [
                                                                                        {"value": "Bool"},
                                                                                        {"value": "Object"},
                                                                                        {"value": "String"}
                                                                                    ]
                                                                                }
                                                                            },
                                                                            {
                                                                                "type": "boolean",
                                                                                "name": "value",
                                                                                "required": True
                                                                            }
                                                                        ],
                                                                        "cls": "WorkspaceCustomBooleanParameter_read"
                                                                    },
                                                                    {
                                                                        "type": "object",
                                                                        "name": "encryption",
                                                                        "props": [
                                                                            {
                                                                                "readOnly": True,
                                                                                "type": "string",
                                                                                "name": "type",
                                                                                "enum": {
                                                                                    "items": [
                                                                                        {"value": "Bool"},
                                                                                        {"value": "Object"},
                                                                                        {"value": "String"}
                                                                                    ]
                                                                                }
                                                                            },
                                                                            {
                                                                                "type": "object",
                                                                                "name": "value",
                                                                                "props": [
                                                                                    {
                                                                                        "type": "string",
                                                                                        "name": "KeyName"
                                                                                    },
                                                                                    {
                                                                                        "default": {
                                                                                            "value": "Default"
                                                                                        },
                                                                                        "type": "string",
                                                                                        "name": "keySource",
                                                                                        "enum": {
                                                                                            "items": [
                                                                                                {"value": "Default"},
                                                                                                {
                                                                                                    "value": "Microsoft.Keyvault"
                                                                                                }
                                                                                            ]
                                                                                        }
                                                                                    },
                                                                                    {
                                                                                        "type": "string",
                                                                                        "name": "keyvaulturi"
                                                                                    },
                                                                                    {
                                                                                        "type": "string",
                                                                                        "name": "keyversion"
                                                                                    }
                                                                                ]
                                                                            }
                                                                        ]
                                                                    },
                                                                    {
                                                                        "type": "@WorkspaceCustomStringParameter_read",
                                                                        "name": "loadBalancerBackendPoolName"
                                                                    },
                                                                    {
                                                                        "type": "@WorkspaceCustomStringParameter_read",
                                                                        "name": "loadBalancerId"
                                                                    },
                                                                    {
                                                                        "type": "@WorkspaceCustomStringParameter_read",
                                                                        "name": "natGatewayName"
                                                                    },
                                                                    {
                                                                        "type": "@WorkspaceCustomBooleanParameter_read",
                                                                        "name": "prepareEncryption"
                                                                    },
                                                                    {
                                                                        "type": "@WorkspaceCustomStringParameter_read",
                                                                        "name": "publicIpName"
                                                                    },
                                                                    {
                                                                        "type": "@WorkspaceCustomBooleanParameter_read",
                                                                        "name": "requireInfrastructureEncryption"
                                                                    },
                                                                    {
                                                                        "readOnly": True,
                                                                        "type": "object",
                                                                        "name": "resourceTags",
                                                                        "props": [
                                                                            {
                                                                                "readOnly": True,
                                                                                "type": "string",
                                                                                "name": "type",
                                                                                "enum": {
                                                                                    "items": [
                                                                                        {"value": "Bool"},
                                                                                        {"value": "Object"},
                                                                                        {"value": "String"}
                                                                                    ]
                                                                                }
                                                                            }
                                                                        ]
                                                                    },
                                                                    {
                                                                        "type": "@WorkspaceCustomStringParameter_read",
                                                                        "name": "storageAccountName"
                                                                    },
                                                                    {
                                                                        "type": "@WorkspaceCustomStringParameter_read",
                                                                        "name": "storageAccountSkuName"
                                                                    },
                                                                    {
                                                                        "type": "@WorkspaceCustomStringParameter_read",
                                                                        "name": "vnetAddressPrefix"
                                                                    }
                                                                ]
                                                            },
                                                            {
                                                                "readOnly": True,
                                                                "type": "array<object>",
                                                                "name": "privateEndpointConnections",
                                                                "item": {
                                                                    "readOnly": True,
                                                                    "type": "object",
                                                                    "props": [
                                                                        {
                                                                            "readOnly": True,
                                                                            "type": "ResourceId",
                                                                            "name": "id",
                                                                            "format": {
                                                                                "template": "/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Databricks/workspaces/{}/privateEndpointConnections/{}"
                                                                            }
                                                                        },
                                                                        {
                                                                            "readOnly": True,
                                                                            "type": "string",
                                                                            "name": "name"
                                                                        },
                                                                        {
                                                                            "readOnly": True,
                                                                            "type": "object",
                                                                            "name": "properties",
                                                                            "required": True,
                                                                            "props": [
                                                                                {
                                                                                    "readOnly": True,
                                                                                    "type": "object",
                                                                                    "name": "privateEndpoint",
                                                                                    "props": [
                                                                                        {
                                                                                            "readOnly": True,
                                                                                            "type": "string",
                                                                                            "name": "id"
                                                                                        }
                                                                                    ]
                                                                                },
                                                                                {
                                                                                    "readOnly": True,
                                                                                    "type": "object",
                                                                                    "name": "privateLinkServiceConnectionState",
                                                                                    "required": True,
                                                                                    "props": [
                                                                                        {
                                                                                            "readOnly": True,
                                                                                            "type": "string",
                                                                                            "name": "actionRequired"
                                                                                        },
                                                                                        {
                                                                                            "readOnly": True,
                                                                                            "type": "string",
                                                                                            "name": "description"
                                                                                        },
                                                                                        {
                                                                                            "readOnly": True,
                                                                                            "type": "string",
                                                                                            "name": "status",
                                                                                            "required": True,
                                                                                            "enum": {
                                                                                                "items": [
                                                                                                    {
                                                                                                        "value": "Approved"
                                                                                                    },
                                                                                                    {
                                                                                                        "value": "Disconnected"
                                                                                                    },
                                                                                                    {
                                                                                                        "value": "Pending"
                                                                                                    },
                                                                                                    {
                                                                                                        "value": "Rejected"
                                                                                                    }
                                                                                                ]
                                                                                            }
                                                                                        }
                                                                                    ]
                                                                                },
                                                                                {
                                                                                    "readOnly": True,
                                                                                    "type": "string",
                                                                                    "name": "provisioningState",
                                                                                    "enum": {
                                                                                        "items": [
                                                                                            {"value": "Creating"},
                                                                                            {"value": "Deleting"},
                                                                                            {"value": "Failed"},
                                                                                            {"value": "Succeeded"},
                                                                                            {"value": "Updating"}
                                                                                        ]
                                                                                    }
                                                                                }
                                                                            ]
                                                                        },
                                                                        {
                                                                            "readOnly": True,
                                                                            "type": "string",
                                                                            "name": "type"
                                                                        }
                                                                    ]
                                                                }
                                                            },
                                                            {
                                                                "readOnly": True,
                                                                "type": "string",
                                                                "name": "provisioningState",
                                                                "enum": {
                                                                    "items": [
                                                                        {"value": "Accepted"},
                                                                        {"value": "Canceled"},
                                                                        {"value": "Created"},
                                                                        {"value": "Creating"},
                                                                        {"value": "Deleted"},
                                                                        {"value": "Deleting"},
                                                                        {"value": "Failed"},
                                                                        {"value": "Ready"},
                                                                        {"value": "Running"},
                                                                        {"value": "Succeeded"},
                                                                        {"value": "Updating"}
                                                                    ]
                                                                }
                                                            },
                                                            {
                                                                "type": "string",
                                                                "name": "publicNetworkAccess",
                                                                "enum": {
                                                                    "items": [
                                                                        {"value": "Disabled"},
                                                                        {"value": "Enabled"}
                                                                    ]
                                                                }
                                                            },
                                                            {
                                                                "type": "string",
                                                                "name": "requiredNsgRules",
                                                                "enum": {
                                                                    "items": [
                                                                        {"value": "AllRules"},
                                                                        {
                                                                            "value": "NoAzureDatabricksRules"
                                                                        },
                                                                        {"value": "NoAzureServiceRules"}
                                                                    ]
                                                                }
                                                            },
                                                            {
                                                                "type": "object",
                                                                "name": "storageAccountIdentity",
                                                                "props": [
                                                                    {
                                                                        "readOnly": True,
                                                                        "type": "uuid",
                                                                        "name": "principalId"
                                                                    },
                                                                    {
                                                                        "readOnly": True,
                                                                        "type": "uuid",
                                                                        "name": "tenantId"
                                                                    },
                                                                    {
                                                                        "readOnly": True,
                                                                        "type": "string",
                                                                        "name": "type"
                                                                    }
                                                                ]
                                                            },
                                                            {
                                                                "type": "string",
                                                                "name": "uiDefinitionUri"
                                                            },
                                                            {
                                                                "type": "@CreatedBy_read",
                                                                "name": "updatedBy"
                                                            },
                                                            {
                                                                "readOnly": True,
                                                                "type": "string",
                                                                "name": "workspaceId"
                                                            },
                                                            {
                                                                "readOnly": True,
                                                                "type": "string",
                                                                "name": "workspaceUrl"
                                                            }
                                                        ],
                                                        "clientFlatten": True
                                                    },
                                                    {
                                                        "type": "object",
                                                        "name": "sku",
                                                        "props": [
                                                            {
                                                                "type": "string",
                                                                "name": "name",
                                                                "required": True
                                                            },
                                                            {"type": "string", "name": "tier"}
                                                        ]
                                                    },
                                                    {
                                                        "readOnly": True,
                                                        "type": "object",
                                                        "name": "systemData",
                                                        "props": [
                                                            {
                                                                "readOnly": True,
                                                                "type": "dateTime",
                                                                "name": "createdAt"
                                                            },
                                                            {
                                                                "readOnly": True,
                                                                "type": "string",
                                                                "name": "createdBy"
                                                            },
                                                            {
                                                                "readOnly": True,
                                                                "type": "string",
                                                                "name": "createdByType",
                                                                "enum": {
                                                                    "items": [
                                                                        {"value": "Application"},
                                                                        {"value": "Key"},
                                                                        {"value": "ManagedIdentity"},
                                                                        {"value": "User"}
                                                                    ]
                                                                }
                                                            },
                                                            {
                                                                "readOnly": True,
                                                                "type": "dateTime",
                                                                "name": "lastModifiedAt"
                                                            },
                                                            {
                                                                "readOnly": True,
                                                                "type": "string",
                                                                "name": "lastModifiedBy"
                                                            },
                                                            {
                                                                "readOnly": True,
                                                                "type": "string",
                                                                "name": "lastModifiedByType",
                                                                "enum": {
                                                                    "items": [
                                                                        {"value": "Application"},
                                                                        {"value": "Key"},
                                                                        {"value": "ManagedIdentity"},
                                                                        {"value": "User"}
                                                                    ]
                                                                }
                                                            }
                                                        ]
                                                    },
                                                    {
                                                        "type": "object",
                                                        "name": "tags",
                                                        "additionalProps": {
                                                            "item": {"type": "string"}
                                                        }
                                                    },
                                                    {
                                                        "readOnly": True,
                                                        "type": "string",
                                                        "name": "type"
                                                    }
                                                ]
                                            }
                                        }
                                    ]
                                }
                            }
                        }
                    },
                    {
                        "isError": True,
                        "body": {
                            "json": {"schema": {"type": "@ODataV4Format"}}
                        }
                    }
                ]
            }
        }
        )
        operation.validate()
        operation.to_native()
        operation.to_primitive()

    def test_instance_update_operation(self):
        operation = CMDInstanceUpdateOperation({
            "when": [
                "$condition_3",
            ],
            "instanceUpdate": {
                "instance": "$instance.property",
                "clientFlatten": True,
                "generic": {
                    "add": "$add",
                    "set": "$set",
                    "remove": "$remove",
                    "force_string": "$forceString"
                }
            }
        })
        operation.validate()
        operation.to_native()
        operation.to_primitive()
