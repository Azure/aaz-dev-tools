from unittest import TestCase
from command.model.configuration._instance_update import *


class InstanceUpdateTest(TestCase):

    def test_json_instance_update(self):

        instance_update = CMDJsonInstanceUpdateAction({
            "instance": "$instance.property",
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
        })

        instance_update.validate()
        print(instance_update.to_native())
        print(instance_update.to_primitive())
