from unittest import TestCase
from command.model.configuration._operation import *


class OperationTest(TestCase):

    def test_http_operation(self):
        operation = CMDHttpOperation({
            "when": [
                "$condition_1",
                "$condition_2",
            ],
            "longRunning": True,
            "http": {
                "path": "/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.DataFactory/factories/{factoryName}/integrationRuntimes/{integrationRuntimeName}",
                "request": {
                    "method": "put",
                    "path": {
                        "params": [
                            {
                                "name": "subscriptionId",
                                "required": True,
                                "arg": "$subscription",
                            },
                            {
                                "name": "resourceGroupName",
                                "required": True,
                                "arg": "$resourceGroup",
                            },
                            {
                                "name": "factoryName",
                                "required": True,
                                "arg": "$factoryName",
                            },
                            {
                                "name": "integrationRuntimeName",
                                "required": True,
                                "arg": "$integrationRuntimeName",
                            }
                        ]
                    },
                    "query": {
                        "consts": [
                            {
                                "name": "api-version",
                                "value": "2018-06-01",
                            }
                        ]
                    },
                    "header": {
                        "params": [
                            {
                                "name": "If-Match",
                                "arg": "$ifMatch",
                            },
                        ]
                    },
                    "body": {
                        "json": {
                            "type": "object",
                            "props": [
                                {
                                    "name": "type",
                                    "type": "string",
                                    "required": True,
                                    "arg": "$type",
                                    "enum": {
                                        "items": [
                                            {
                                                "value": "Managed",
                                            },
                                            {
                                                "value": "SelfHosted",
                                            }
                                        ]
                                    },
                                },
                                {
                                    "name": "description",
                                    "type": "string",
                                    "arg": "$description"
                                }
                            ],
                            "discriminators": [
                                {
                                    "prop": "type",
                                    "value": "Managed",
                                    "props": [
                                        {
                                            "name": "typeProperties",
                                            "type": "object",
                                            "required": True,
                                            "props": [
                                                {
                                                    "name": "typeProperties",
                                                    "type": "object",
                                                    "required": True,
                                                    "props": [
                                                        {
                                                            "name": "ssisProperties",
                                                            "type": "object",
                                                            "arg": "$ssisProperties",
                                                            "props": [
                                                                {
                                                                    "name": "expressCustomSetupProperties",
                                                                    "type": "array<object>",
                                                                    "arg": "$ssisProperties.expressCustomSetupProperties",
                                                                    "item": {
                                                                        "type": "object",
                                                                        "props": [
                                                                            {
                                                                                "name": "type",
                                                                                "type": "string",
                                                                                "required": True,
                                                                                "enum": {
                                                                                    "items": [
                                                                                        {
                                                                                            "arg": "$ssisProperties.expressCustomSetupProperties[].CmdkeySetup",
                                                                                            "value": "CmdkeySetup",
                                                                                        },
                                                                                        {
                                                                                            "arg": "$ssisProperties.expressCustomSetupProperties[].EnvironmentVariableSetup",
                                                                                            "value": "EnvironmentVariableSetup",
                                                                                        },
                                                                                        {
                                                                                            "arg": "$ssisProperties.expressCustomSetupProperties[].ComponentSetup",
                                                                                            "value": "ComponentSetup",
                                                                                        },
                                                                                        {
                                                                                            "arg": "$ssisProperties.expressCustomSetupProperties[].AzPowerShellSetup",
                                                                                            "value": "AzPowerShellSetup",
                                                                                        }
                                                                                    ]
                                                                                }
                                                                            },
                                                                        ],
                                                                        "discriminators": [
                                                                            {
                                                                                "prop": "type",
                                                                                "value": "CmdkeySetup",
                                                                                "props": [
                                                                                    {
                                                                                        "name": "typeProperties",
                                                                                        "type": "object",
                                                                                        "required": True,
                                                                                        "props": [
                                                                                            {
                                                                                                "name": "targetName",
                                                                                                "type": "object",
                                                                                                "required": True,
                                                                                                "arg": "$ssisProperties.expressCustomSetupProperties[].CmdkeySetup.targetName",
                                                                                            },
                                                                                            {
                                                                                                "name": "userName",
                                                                                                "type": "object",
                                                                                                "required": True,
                                                                                                "arg": "$ssisProperties.expressCustomSetupProperties[].CmdkeySetup.userName",
                                                                                            },
                                                                                            {
                                                                                                "name": "password",
                                                                                                "type": "object",
                                                                                                "required": True,
                                                                                                "arg": "$ssisProperties.expressCustomSetupProperties[].CmdkeySetup.password",
                                                                                                "props": [
                                                                                                    {
                                                                                                        "name": "type",
                                                                                                        "type": "string",
                                                                                                        "required": True,
                                                                                                        "enum": {
                                                                                                            "items": [
                                                                                                                {
                                                                                                                    "arg": "$ssisProperties.expressCustomSetupProperties[].CmdkeySetup.password.SecureString",
                                                                                                                    "value": "SecureString",
                                                                                                                }
                                                                                                            ],
                                                                                                        },
                                                                                                    }

                                                                                                ],
                                                                                                "discriminators": [
                                                                                                    {
                                                                                                        "prop": "type",
                                                                                                        "value": "SecureString",
                                                                                                        "props": [
                                                                                                            {
                                                                                                                "name": "value",
                                                                                                                "type": "string",
                                                                                                                "required": True,
                                                                                                                "arg": "$ssisProperties.expressCustomSetupProperties[].CmdkeySetup.password.SecureString.value"
                                                                                                            }
                                                                                                        ]
                                                                                                    }
                                                                                                ]
                                                                                            }
                                                                                        ]

                                                                                    }

                                                                                ]
                                                                            }
                                                                        ]
                                                                    }
                                                                }
                                                            ]
                                                        }
                                                    ]
                                                }
                                            ]
                                        },
                                        {
                                            "name": "managedVirtualNetwork",
                                            "type": "object",
                                            "arg": "$managedVirtualNetwork",
                                            "props": [
                                                {
                                                    "name": "type",
                                                    "type": "string",
                                                    "required": True,
                                                    "arg": "$managedVirtualNetwork.type",
                                                    "enum": {
                                                        "items": [
                                                            {
                                                                "value": "ManagedVirtualNetworkReference"
                                                            }
                                                        ]
                                                    }
                                                },
                                                {
                                                    "name": "referenceName",
                                                    "type": "string",
                                                    "required": True,
                                                    "arg": "$managedVirtualNetwork.referenceName"
                                                }
                                            ]
                                        }
                                    ],
                                },
                                {
                                    "prop": "type",
                                    "value": "SelfHosted",
                                    "props": [
                                        {
                                            "name": "typeProperties",
                                            "type": "object",
                                            "required": True,
                                            "props": [
                                                {
                                                    "name": "linkedInfo",
                                                    "type": "object",
                                                    "arg": "$linkedInfo",
                                                    "props": [
                                                        {
                                                            "name": "authorizationType",
                                                            "type": "string",
                                                            "required": True,
                                                            "arg": "$linkedInfo.authorizationType"
                                                        }
                                                    ]
                                                }
                                            ]
                                        }
                                    ]
                                }
                            ],
                        }
                    }
                },
                "responses": [
                    {
                        "statusCode": [200, 201],
                        "header": {
                            "items": [
                                {
                                    "name": "Sync-Token",
                                    "var": "$SyncTokenHeader"
                                }
                            ]
                        },
                        "body": {
                            "json": {
                                "var": "$instance",
                                "type": "object",
                                "props": [
                                    {
                                        "name": "type",
                                        "type": "string",
                                        "required": True,
                                        "enum": {
                                            "items": [
                                                {
                                                    "value": "Managed",
                                                },
                                                {
                                                    "value": "SelfHosted",
                                                }
                                            ]
                                        },
                                    },
                                    {
                                        "name": "description",
                                        "type": "string",
                                    }
                                ],
                                "discriminators": [
                                    {
                                        "prop": "type",
                                        "value": "Managed",
                                        "props": [
                                            {
                                                "name": "typeProperties",
                                                "type": "object",
                                                "required": True,
                                                "props": [
                                                    {
                                                        "name": "typeProperties",
                                                        "type": "object",
                                                        "required": True,
                                                        "props": [
                                                            {
                                                                "name": "ssisProperties",
                                                                "type": "object",
                                                                "props": [
                                                                    {
                                                                        "name": "expressCustomSetupProperties",
                                                                        "type": "array<object>",
                                                                        "item": {
                                                                            "type": "object",
                                                                            "props": [
                                                                                {
                                                                                    "name": "type",
                                                                                    "type": "string",
                                                                                    "required": True,
                                                                                    "enum": {
                                                                                        "items": [
                                                                                            {
                                                                                                "value": "CmdkeySetup",
                                                                                            },
                                                                                            {
                                                                                                "value": "EnvironmentVariableSetup",
                                                                                            },
                                                                                            {
                                                                                                "value": "ComponentSetup",
                                                                                            },
                                                                                            {
                                                                                                "value": "AzPowerShellSetup",
                                                                                            }
                                                                                        ]
                                                                                    }
                                                                                },
                                                                            ],
                                                                            "discriminators": [
                                                                                {
                                                                                    "prop": "type",
                                                                                    "value": "CmdkeySetup",
                                                                                    "props": [
                                                                                        {
                                                                                            "name": "typeProperties",
                                                                                            "type": "object",
                                                                                            "required": True,
                                                                                            "props": [
                                                                                                {
                                                                                                    "name": "targetName",
                                                                                                    "type": "object",
                                                                                                    "required": True,
                                                                                                    },
                                                                                                {
                                                                                                    "name": "userName",
                                                                                                    "type": "object",
                                                                                                    "required": True,
                                                                                                    },
                                                                                                {
                                                                                                    "name": "password",
                                                                                                    "type": "object",
                                                                                                    "required": True,
                                                                                                    "props": [
                                                                                                        {
                                                                                                            "name": "type",
                                                                                                            "type": "string",
                                                                                                            "required": True,
                                                                                                            "enum": {
                                                                                                                "items": [
                                                                                                                    {
                                                                                                                        "value": "SecureString",
                                                                                                                    }
                                                                                                                ],
                                                                                                            },
                                                                                                        }

                                                                                                    ],
                                                                                                    "discriminators": [
                                                                                                        {
                                                                                                            "prop": "type",
                                                                                                            "value": "SecureString",
                                                                                                            "props": [
                                                                                                                {
                                                                                                                    "name": "value",
                                                                                                                    "type": "string",
                                                                                                                    "required": True,
                                                                                                                }
                                                                                                            ]
                                                                                                        }
                                                                                                    ]
                                                                                                }
                                                                                            ]

                                                                                        }

                                                                                    ]
                                                                                }
                                                                            ]
                                                                        }
                                                                    }
                                                                ]
                                                            }
                                                        ]
                                                    }
                                                ]
                                            },
                                            {
                                                "name": "managedVirtualNetwork",
                                                "type": "object",
                                                "props": [
                                                    {
                                                        "name": "type",
                                                        "type": "string",
                                                        "required": True,
                                                        "enum": {
                                                            "items": [
                                                                {
                                                                    "value": "ManagedVirtualNetworkReference"
                                                                }
                                                            ]
                                                        }
                                                    },
                                                    {
                                                        "name": "referenceName",
                                                        "type": "string",
                                                        "required": True,
                                                    }
                                                ]
                                            }
                                        ],
                                    },
                                    {
                                        "prop": "type",
                                        "value": "SelfHosted",
                                        "props": [
                                            {
                                                "name": "typeProperties",
                                                "type": "object",
                                                "required": True,
                                                "props": [
                                                    {
                                                        "name": "linkedInfo",
                                                        "type": "object",
                                                        "props": [
                                                            {
                                                                "name": "authorizationType",
                                                                "type": "string",
                                                                "required": True,
                                                            }
                                                        ]
                                                    }
                                                ]
                                            }
                                        ]
                                    }
                                ],
                            }
                        }
                    },
                    {
                        "isError": True,
                        "header": {
                            "items": [
                                {
                                    "name": "x-ms-request-id",
                                }
                            ]
                        },
                        "body": {
                            "json": {
                                "type": "object",
                                "cls": "@CloudError",
                                "props": [
                                    {
                                        "name": "error",
                                        "type": "object",
                                        "clientFlatten": True,
                                        "props": [
                                            {
                                                "name": "code",
                                                "type": "string",
                                                "required": True,
                                            },
                                            {
                                                "name": "message",
                                                "type": "string",
                                                "required": True,
                                            },
                                            {
                                                "name": "target",
                                                "type": "string",
                                            },
                                            {
                                                "name": "details",
                                                "type": "array<@CloudError>",
                                                "item": {
                                                    "type": "@CloudError"
                                                }
                                            }
                                        ]
                                    }
                                ]

                            }
                        }
                    }

                ]
            }
        })
        operation.validate()
        print(operation.to_native())
        print(operation.to_primitive())

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
        print(operation.to_native())
        print(operation.to_primitive())
