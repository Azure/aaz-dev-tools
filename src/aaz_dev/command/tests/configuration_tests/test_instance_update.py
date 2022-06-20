from unittest import TestCase

from command.model.configuration._instance_update import *
from command.tests.common import verify_xml


class InstanceUpdateTest(TestCase):

    def test_json_instance_update(self):
        instance_update = CMDJsonInstanceUpdateAction({
            "instance": "$Instance",
            "json": {
                "schema": {
                    "type": "object",
                    "name": "parameters",
                    "props": [
                        {
                            "type": "object",
                            "name": "properties",
                            "required": True,
                            "props": [
                                {
                                    "type": "array<object>",
                                    "name": "authorizations",
                                    "arg": "$parameters.properties.authorizations",
                                    "item": {
                                        "type": "object",
                                        "props": [
                                            {
                                                "type": "uuid",
                                                "name": "principalId",
                                                "arg": "$parameters.properties.authorizations[].principalId",
                                                "required": True
                                            },
                                            {
                                                "type": "uuid",
                                                "name": "roleDefinitionId",
                                                "arg": "$parameters.properties.authorizations[].roleDefinitionId",
                                                "required": True
                                            }
                                        ]
                                    }
                                },
                                {
                                    "type": "object",
                                    "name": "encryption",
                                    "arg": "$parameters.properties.encryption",
                                    "props": [
                                        {
                                            "type": "object",
                                            "name": "entities",
                                            "arg": "$parameters.properties.encryption.entities",
                                            "required": True,
                                            "props": [
                                                {
                                                    "type": "object",
                                                    "name": "managedServices",
                                                    "arg": "$parameters.properties.encryption.entities.managedServices",
                                                    "props": [
                                                        {
                                                            "type": "string",
                                                            "name": "keySource",
                                                            "arg": "$parameters.properties.encryption.entities.managedServices.keySource",
                                                            "required": True,
                                                            "enum": {
                                                                "items": [
                                                                    {"value": "Microsoft.Keyvault"}
                                                                ]
                                                            }
                                                        },
                                                        {
                                                            "type": "object",
                                                            "name": "keyVaultProperties",
                                                            "arg": "$parameters.properties.encryption.entities.managedServices.keyVaultProperties",
                                                            "props": [
                                                                {
                                                                    "type": "string",
                                                                    "name": "keyName",
                                                                    "arg": "$parameters.properties.encryption.entities.managedServices.keyVaultProperties.keyName",
                                                                    "required": True
                                                                },
                                                                {
                                                                    "type": "string",
                                                                    "name": "keyVaultUri",
                                                                    "arg": "$parameters.properties.encryption.entities.managedServices.keyVaultProperties.keyVaultUri",
                                                                    "required": True
                                                                },
                                                                {
                                                                    "type": "string",
                                                                    "name": "keyVersion",
                                                                    "arg": "$parameters.properties.encryption.entities.managedServices.keyVaultProperties.keyVersion",
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
                                    "arg": "$parameters.properties.managedResourceGroupId",
                                    "required": True
                                },
                                {
                                    "type": "object",
                                    "name": "parameters",
                                    "arg": "$parameters.properties.parameters",
                                    "props": [
                                        {
                                            "type": "object",
                                            "name": "amlWorkspaceId",
                                            "arg": "$parameters.properties.parameters.amlWorkspaceId",
                                            "props": [
                                                {
                                                    "type": "string",
                                                    "name": "value",
                                                    "arg": "@WorkspaceCustomStringParameter_update.value",
                                                    "required": True
                                                }
                                            ],
                                            "cls": "WorkspaceCustomStringParameter_update"
                                        },
                                        {
                                            "type": "@WorkspaceCustomStringParameter_update",
                                            "name": "customPrivateSubnetName",
                                            "arg": "$parameters.properties.parameters.customPrivateSubnetName"
                                        },
                                        {
                                            "type": "@WorkspaceCustomStringParameter_update",
                                            "name": "customPublicSubnetName",
                                            "arg": "$parameters.properties.parameters.customPublicSubnetName"
                                        },
                                        {
                                            "type": "@WorkspaceCustomStringParameter_update",
                                            "name": "customVirtualNetworkId",
                                            "arg": "$parameters.properties.parameters.customVirtualNetworkId"
                                        },
                                        {
                                            "type": "object",
                                            "name": "enableNoPublicIp",
                                            "arg": "$parameters.properties.parameters.enableNoPublicIp",
                                            "props": [
                                                {
                                                    "type": "boolean",
                                                    "name": "value",
                                                    "arg": "@WorkspaceCustomBooleanParameter_update.value",
                                                    "required": True
                                                }
                                            ],
                                            "cls": "WorkspaceCustomBooleanParameter_update"
                                        },
                                        {
                                            "type": "object",
                                            "name": "encryption",
                                            "arg": "$parameters.properties.parameters.encryption",
                                            "props": [
                                                {
                                                    "type": "object",
                                                    "name": "value",
                                                    "arg": "$parameters.properties.parameters.encryption.value",
                                                    "props": [
                                                        {
                                                            "type": "string",
                                                            "name": "KeyName",
                                                            "arg": "$parameters.properties.parameters.encryption.value.KeyName"
                                                        },
                                                        {
                                                            "default": {"value": "Default"},
                                                            "type": "string",
                                                            "name": "keySource",
                                                            "arg": "$parameters.properties.parameters.encryption.value.keySource",
                                                            "enum": {
                                                                "items": [
                                                                    {"value": "Default"},
                                                                    {"value": "Microsoft.Keyvault"}
                                                                ]
                                                            }
                                                        },
                                                        {
                                                            "type": "string",
                                                            "name": "keyvaulturi",
                                                            "arg": "$parameters.properties.parameters.encryption.value.keyvaulturi"
                                                        },
                                                        {
                                                            "type": "string",
                                                            "name": "keyversion",
                                                            "arg": "$parameters.properties.parameters.encryption.value.keyversion"
                                                        }
                                                    ]
                                                }
                                            ]
                                        },
                                        {
                                            "type": "@WorkspaceCustomStringParameter_update",
                                            "name": "loadBalancerBackendPoolName",
                                            "arg": "$parameters.properties.parameters.loadBalancerBackendPoolName"
                                        },
                                        {
                                            "type": "@WorkspaceCustomStringParameter_update",
                                            "name": "loadBalancerId",
                                            "arg": "$parameters.properties.parameters.loadBalancerId"
                                        },
                                        {
                                            "type": "@WorkspaceCustomStringParameter_update",
                                            "name": "natGatewayName",
                                            "arg": "$parameters.properties.parameters.natGatewayName"
                                        },
                                        {
                                            "type": "@WorkspaceCustomBooleanParameter_update",
                                            "name": "prepareEncryption",
                                            "arg": "$parameters.properties.parameters.prepareEncryption"
                                        },
                                        {
                                            "type": "@WorkspaceCustomStringParameter_update",
                                            "name": "publicIpName",
                                            "arg": "$parameters.properties.parameters.publicIpName"
                                        },
                                        {
                                            "type": "@WorkspaceCustomBooleanParameter_update",
                                            "name": "requireInfrastructureEncryption",
                                            "arg": "$parameters.properties.parameters.requireInfrastructureEncryption"
                                        },
                                        {
                                            "type": "@WorkspaceCustomStringParameter_update",
                                            "name": "storageAccountName",
                                            "arg": "$parameters.properties.parameters.storageAccountName"
                                        },
                                        {
                                            "type": "@WorkspaceCustomStringParameter_update",
                                            "name": "storageAccountSkuName",
                                            "arg": "$parameters.properties.parameters.storageAccountSkuName"
                                        },
                                        {
                                            "type": "@WorkspaceCustomStringParameter_update",
                                            "name": "vnetAddressPrefix",
                                            "arg": "$parameters.properties.parameters.vnetAddressPrefix"
                                        }
                                    ]
                                },
                                {
                                    "type": "string",
                                    "name": "publicNetworkAccess",
                                    "arg": "$parameters.properties.publicNetworkAccess",
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
                                    "arg": "$parameters.properties.requiredNsgRules",
                                    "enum": {
                                        "items": [
                                            {"value": "AllRules"},
                                            {"value": "NoAzureDatabricksRules"},
                                            {"value": "NoAzureServiceRules"}
                                        ]
                                    }
                                },
                                {
                                    "type": "string",
                                    "name": "uiDefinitionUri",
                                    "arg": "$parameters.properties.uiDefinitionUri"
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
                                    "arg": "$parameters.sku.name",
                                    "required": True
                                },
                                {
                                    "type": "string",
                                    "name": "tier",
                                    "arg": "$parameters.sku.tier"
                                }
                            ]
                        },
                        {
                            "type": "object",
                            "name": "tags",
                            "arg": "$parameters.tags",
                            "additionalProps": {"item": {"type": "string"}}
                        }
                    ],
                    "clientFlatten": True
                }
            }
        })

        instance_update.validate()
        instance_update.to_native()
        instance_update.to_primitive()

        verify_xml(self, instance_update)
