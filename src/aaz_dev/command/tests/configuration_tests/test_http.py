from unittest import TestCase

from command.model.configuration._http import *
from command.tests.common import verify_xml


class HttpTest(TestCase):

    def test_http_action(self):
        http_action = CMDHttpAction({
            "path": "/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Sql/managedInstances/{managedInstanceName}/dnsAliases/{dnsAliasName}",
            "request": {
                "method": "get",
                "path": {
                    "params": [
                        {
                            "type": "string",
                            "name": "dnsAliasName",
                            "arg": "$Path.dnsAliasName",
                            "required": True
                        },
                        {
                            "type": "string",
                            "name": "managedInstanceName",
                            "arg": "$Path.managedInstanceName",
                            "required": True
                        },
                        {
                            "type": "string",
                            "name": "resourceGroupName",
                            "arg": "$Path.resourceGroupName",
                            "required": True
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
                            "default": {"value": "2021-11-01-preview"},
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
                                    {
                                        "readOnly": True,
                                        "type": "ResourceId",
                                        "name": "id",
                                        "format": {
                                            "template": "/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Sql/managedInstances/{}/dnsAliases/{}"
                                        }
                                    },
                                    {
                                        "readOnly": True,
                                        "type": "string",
                                        "name": "name"
                                    },
                                    {
                                        "type": "object",
                                        "name": "properties",
                                        "props": [
                                            {
                                                "readOnly": True,
                                                "type": "string",
                                                "name": "azureDnsRecord"
                                            },
                                            {
                                                "readOnly": True,
                                                "type": "string",
                                                "name": "publicAzureDnsRecord"
                                            }
                                        ],
                                        "clientFlatten": True
                                    },
                                    {
                                        "readOnly": True,
                                        "type": "string",
                                        "name": "type"
                                    }
                                ],
                                "cls": "ManagedServerDnsAlias_read"
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
        })

        http_action.validate()
        http_action.to_native()
        http_action.to_primitive()

        verify_xml(self, http_action)
