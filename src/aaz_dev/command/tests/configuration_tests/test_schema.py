from unittest import TestCase
from command.model.configuration._schema import *


class SchemaTest(TestCase):

    def test_string_schema(self):
        prop = CMDStringSchema({
            "name": "location",
            "arg": "$location",
            "required": True,
            "readonly": False,
            "format": {
                "pattern": "[a-zA-Z]+",
                "maxLength": 10,
                "minLength": 5,
            },
            "enum": {
                "items": [
                    {
                        "value": "westus"
                    },
                    {
                        "value": "southeastus"
                    }
                ]
            },
            "default": {
                "value": ""
            },
        })
        prop.validate()
        print(prop.to_native())
        print(prop.to_primitive())

    def test_integer_schema(self):
        prop = CMDIntegerSchema({
            "name": "location",
            "arg": "$location",
            "required": True,
            "readonly": False,
            "format": {
                "bits": 64,
                "multipleOf": 5,
                "maximum": 10,
                "minimum": 5,
            },
            "enum": {
                "items": [
                    {
                        "value": 5
                    },
                    {
                        "value": 10
                    }
                ]
            },
            "default": {
                "value": 5
            },
        })
        prop.validate()
        print(prop.to_native())
        print(prop.to_primitive())

    def test_boolean_schema(self):
        prop = CMDBooleanSchema({
            "name": "location",
            "arg": "$location",
            "required": True,
            "readonly": False,
            "default": {
                "value": False,
            },
        })
        prop.validate()
        print(prop.to_native())
        print(prop.to_primitive())

    def test_float_schema(self):
        prop = CMDFloatSchema({
            "name": "location",
            "arg": "$location",
            "required": True,
            "readonly": False,
            "format": {
                "bits": 64,
                "multipleOf": 0.1,
                "maximum": 10.0,
                "minimum": 5.0,
                "exclusiveMaximum": True,
            },
            "enum": {
                "items": [
                    {
                        "value": 5.0
                    },
                    {
                        "value": 10.0
                    }
                ]
            },
            "default": {
                "value": 5
            },
        })
        prop.validate()
        print(prop.to_native())
        print(prop.to_primitive())

    def test_object_schema(self):
        prop = CMDObjectSchema({
            "name": "properties",
            "type": "object",
            "required": True,
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
        })
        prop.validate()
        print(prop.to_native())
        print(prop.to_primitive())

    def test_array_schema(self):
        prop = CMDArraySchema({
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
        })
        prop.validate()
        print(prop.to_native())
        print(prop.to_primitive())

    def test_object_json(self):
        json = CMDObjectJson({
            "var": "$instance",
            "ref": "$inst",
            "cls": "@CustomProperty",
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
        })
        json.validate()
        print(json.to_native())
        print(json.to_primitive())

    def test_array_json(self):
        json = CMDArrayJson({
            "var": "$instanceList",
            "ref": "$insts",
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
        })
        json.validate()
        print(json.to_native())
        print(json.to_primitive())
