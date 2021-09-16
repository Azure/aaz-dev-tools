from unittest import TestCase
from command.model.configuration._arg import *


class ArgumentTest(TestCase):

    def test_string_argument(self):

        arg = CMDStringArg({
            "var": "$argName",
            "options": [
                "--name",
                "-n"
            ],
            "required": True,
            "stage": "Stable",
            "help": {
                "short": "The Name Of Argument",
                "long": [
                    "Sentence 1",
                    "Sentence 2"
                ],
                "refCommands": [
                    "az network create",
                    "az vnet create",
                ]
            },
            "default": {
                "value": "defaultValue"
            },
            "blank": {
                "value": "blankValue"
            },
            "format": {
                "pattern": "[a-zA-Z0-9]+",
                "maxLength": 100,
                "minLength": 1,
            },
            "enum": {
                "items": [
                    {
                        "name": "Enum 1",
                        "value": "1"
                    },
                    {
                        "name": "Enum 2",
                        "hide": True,
                        "value": "2"
                    },
                    {
                        "name": "Enum 3",
                        "hide": False,
                        "value": "3"
                    }
                ]
            }
        })

        arg.validate()
        print(arg.to_native())
        print(arg.to_primitive())

    def test_byte_argument(self):
        arg = CMDByteArg({
            "var": "$argName",
            "options": [
                "--name",
                "-n"
            ],
            "required": True,
            "stage": "Stable",
            "help": {
                "short": "The Name Of Argument",
                "long": [
                    "Sentence 1",
                    "Sentence 2"
                ],
                "refCommands": [
                    "az network create",
                    "az vnet create",
                ]
            },
            "default": {
                "value": "defaultValue"
            },
            "blank": {
                "value": "blankValue"
            },
            "format": {
                "pattern": "[a-zA-Z0-9]+",
                "maxLength": 100,
                "minLength": 1,
            },
            "enum": {
                "items": [
                    {
                        "name": "Enum 1",
                        "value": "1"
                    },
                    {
                        "name": "Enum 2",
                        "hide": True,
                        "value": "2"
                    },
                    {
                        "name": "Enum 3",
                        "hide": False,
                        "value": "3"
                    }
                ]
            }
        })

        arg.validate()
        print(arg.to_native())
        print(arg.to_primitive())

    def test_binary_argument(self):
        arg = CMDBinaryArg({
            "var": "$argName",
            "options": [
                "--name",
                "-n"
            ],
            "required": True,
            "stage": "Stable",
            "help": {
                "short": "The Name Of Argument",
                "long": [
                    "Sentence 1",
                    "Sentence 2"
                ],
                "refCommands": [
                    "az network create",
                    "az vnet create",
                ]
            },
            "default": {
                "value": "defaultValue"
            },
            "blank": {
                "value": "blankValue"
            },
            "format": {
                "pattern": "[a-zA-Z0-9]+",
                "maxLength": 100,
                "minLength": 1,
            },
            "enum": {
                "items": [
                    {
                        "name": "Enum 1",
                        "value": "1"
                    },
                    {
                        "name": "Enum 2",
                        "hide": True,
                        "value": "2"
                    },
                    {
                        "name": "Enum 3",
                        "hide": False,
                        "value": "3"
                    }
                ]
            }
        })

        arg.validate()
        print(arg.to_native())
        print(arg.to_primitive())

    def test_duration_argument(self):
        arg = CMDDurationArg({
            "var": "$argName",
            "options": [
                "--name",
                "-n"
            ],
            "required": True,
            "stage": "Stable",
            "help": {
                "short": "The Name Of Argument",
                "long": [
                    "Sentence 1",
                    "Sentence 2"
                ],
                "refCommands": [
                    "az network create",
                    "az vnet create",
                ]
            },
            "default": {
                "value": "defaultValue"
            },
            "blank": {
                "value": "blankValue"
            },
            "format": {
                "pattern": "[a-zA-Z0-9]+",
                "maxLength": 100,
                "minLength": 1,
            },
            "enum": {
                "items": [
                    {
                        "name": "Enum 1",
                        "value": "1"
                    },
                    {
                        "name": "Enum 2",
                        "hide": True,
                        "value": "2"
                    },
                    {
                        "name": "Enum 3",
                        "hide": False,
                        "value": "3"
                    }
                ]
            }
        })

        arg.validate()
        print(arg.to_native())
        print(arg.to_primitive())

    def test_date_argument(self):
        arg = CMDDateArg({
            "var": "$argName",
            "options": [
                "--name",
                "-n"
            ],
            "required": True,
            "stage": "Stable",
            "help": {
                "short": "The Name Of Argument",
                "long": [
                    "Sentence 1",
                    "Sentence 2"
                ],
                "refCommands": [
                    "az network create",
                    "az vnet create",
                ]
            },
            "default": {
                "value": "defaultValue"
            },
            "blank": {
                "value": "blankValue"
            },
            "format": {
                "pattern": "[a-zA-Z0-9]+",
                "maxLength": 100,
                "minLength": 1,
            },
            "enum": {
                "items": [
                    {
                        "name": "Enum 1",
                        "value": "1"
                    },
                    {
                        "name": "Enum 2",
                        "hide": True,
                        "value": "2"
                    },
                    {
                        "name": "Enum 3",
                        "hide": False,
                        "value": "3"
                    }
                ]
            }
        })

        arg.validate()
        print(arg.to_native())
        print(arg.to_primitive())

    def test_date_time_argument(self):
        arg = CMDDateTimeArg({
            "var": "$argName",
            "options": [
                "--name",
                "-n"
            ],
            "required": True,
            "stage": "Stable",
            "help": {
                "short": "The Name Of Argument",
                "long": [
                    "Sentence 1",
                    "Sentence 2"
                ],
                "refCommands": [
                    "az network create",
                    "az vnet create",
                ]
            },
            "default": {
                "value": "defaultValue"
            },
            "blank": {
                "value": "blankValue"
            },
            "format": {
                "pattern": "[a-zA-Z0-9]+",
                "maxLength": 100,
                "minLength": 1,
            },
            "enum": {
                "items": [
                    {
                        "name": "Enum 1",
                        "value": "1"
                    },
                    {
                        "name": "Enum 2",
                        "hide": True,
                        "value": "2"
                    },
                    {
                        "name": "Enum 3",
                        "hide": False,
                        "value": "3"
                    }
                ]
            }
        })

        arg.validate()
        print(arg.to_native())
        print(arg.to_primitive())

    def test_uuid_argument(self):
        arg = CMDUuidArg({
            "var": "$argName",
            "options": [
                "--name",
                "-n"
            ],
            "required": True,
            "stage": "Stable",
            "help": {
                "short": "The Name Of Argument",
                "long": [
                    "Sentence 1",
                    "Sentence 2"
                ],
                "refCommands": [
                    "az network create",
                    "az vnet create",
                ]
            },
            "default": {
                "value": "defaultValue"
            },
            "blank": {
                "value": "blankValue"
            },
            "format": {
                "pattern": "[a-zA-Z0-9]+",
                "maxLength": 100,
                "minLength": 1,
            },
            "enum": {
                "items": [
                    {
                        "name": "Enum 1",
                        "value": "1"
                    },
                    {
                        "name": "Enum 2",
                        "hide": True,
                        "value": "2"
                    },
                    {
                        "name": "Enum 3",
                        "hide": False,
                        "value": "3"
                    }
                ]
            }
        })

        arg.validate()
        print(arg.to_native())
        print(arg.to_primitive())

    def test_password_argument(self):
        arg = CMDPasswordArg({
            "var": "$argName",
            "options": [
                "--name",
                "-n"
            ],
            "required": True,
            "stage": "Stable",
            "help": {
                "short": "The Name Of Argument",
                "long": [
                    "Sentence 1",
                    "Sentence 2"
                ],
                "refCommands": [
                    "az network create",
                    "az vnet create",
                ]
            },
            "default": {
                "value": "defaultValue"
            },
            "blank": {
                "value": "blankValue"
            },
            "format": {
                "pattern": "[a-zA-Z0-9]+",
                "maxLength": 100,
                "minLength": 1,
            },
            "enum": {
                "items": [
                    {
                        "name": "Enum 1",
                        "value": "1"
                    },
                    {
                        "name": "Enum 2",
                        "hide": True,
                        "value": "2"
                    },
                    {
                        "name": "Enum 3",
                        "hide": False,
                        "value": "3"
                    }
                ]
            }
        })

        arg.validate()
        print(arg.to_native())
        print(arg.to_primitive())

    def test_integer_argument(self):

        arg = CMDIntegerArg({
            "var": "$age",
            "options": [
                "--age",
                "-a"
            ],
            "required": True,
            "stage": "Preview",
            "help": {
                "short": "The Name Of Argument",
                "long": [
                    "Sentence 1",
                    "Sentence 2"
                ],
                "refCommands": [
                    "az network create",
                    "az vnet create",
                ]
            },
            "default": {
                "value": "defaultValue"
            },
            "blank": {
                "value": "blankValue"
            },
            "format": {
                "multipleOf": 2,
                "maximum": 100,
                "minimum": 1,
            },
            "enum": {
                "items": [
                    {
                        "name": "Enum 1",
                        "value": 1
                    },
                    {
                        "name": "Enum 2",
                        "hide": True,
                        "value": 2
                    },
                    {
                        "name": "Enum 3",
                        "hide": False,
                        "value": 3
                    }
                ]
            }
        })

        arg.validate()
        print(arg.to_native())
        print(arg.to_primitive())

    def test_integer32_argument(self):

        arg = CMDInteger32Arg({
            "var": "$age",
            "options": [
                "--age",
                "-a"
            ],
            "required": True,
            "stage": "Preview",
            "help": {
                "short": "The Name Of Argument",
                "long": [
                    "Sentence 1",
                    "Sentence 2"
                ],
                "refCommands": [
                    "az network create",
                    "az vnet create",
                ]
            },
            "default": {
                "value": "defaultValue"
            },
            "blank": {
                "value": "blankValue"
            },
            "format": {
                "multipleOf": 2,
                "maximum": 100,
                "minimum": 1,
            },
            "enum": {
                "items": [
                    {
                        "name": "Enum 1",
                        "value": 1
                    },
                    {
                        "name": "Enum 2",
                        "hide": True,
                        "value": 2
                    },
                    {
                        "name": "Enum 3",
                        "hide": False,
                        "value": 3
                    }
                ]
            }
        })

        arg.validate()
        print(arg.to_native())
        print(arg.to_primitive())

    def test_integer64_argument(self):

        arg = CMDInteger64Arg({
            "var": "$age",
            "options": [
                "--age",
                "-a"
            ],
            "required": True,
            "stage": "Preview",
            "help": {
                "short": "The Name Of Argument",
                "long": [
                    "Sentence 1",
                    "Sentence 2"
                ],
                "refCommands": [
                    "az network create",
                    "az vnet create",
                ]
            },
            "default": {
                "value": "defaultValue"
            },
            "blank": {
                "value": "blankValue"
            },
            "format": {
                "multipleOf": 2,
                "maximum": 100,
                "minimum": 1,
            },
            "enum": {
                "items": [
                    {
                        "name": "Enum 1",
                        "value": 1
                    },
                    {
                        "name": "Enum 2",
                        "hide": True,
                        "value": 2
                    },
                    {
                        "name": "Enum 3",
                        "hide": False,
                        "value": 3
                    }
                ]
            }
        })

        arg.validate()
        print(arg.to_native())
        print(arg.to_primitive())

    def test_boolean_argument(self):

        arg = CMDBooleanArg({
            "var": "$enabled",
            "options": [
                "--age",
                "-a"
            ],
            "required": True,
            "stage": "Experimental",
            "help": {
                "short": "The Name Of Argument",
                "long": [
                    "Sentence 1",
                    "Sentence 2"
                ],
                "refCommands": [
                    "az network create",
                    "az vnet create",
                ]
            },
            "default": {
                "value": False
            },
            "blank": {
                "value": True
            },
        })

        arg.validate()
        print(arg.to_native())
        print(arg.to_primitive())

    def test_float_argument(self):

        arg = CMDFloatArg({
            "var": "$price",
            "options": [
                "--price",
                "-p"
            ],
            "required": True,
            "help": {
                "short": "The Name Of Argument",
                "long": [
                    "Sentence 1",
                    "Sentence 2"
                ],
                "refCommands": [
                    "az network create",
                    "az vnet create",
                ]
            },
            "default": {
                "value": 1.0
            },
            "blank": {
                "value": 0.1
            },
            "format": {
                "multipleOf": 0.1,
                "maximum": 10.1,
                "exclusiveMaximum": True,
                "minimum": -0.1,
                "exclusiveMinimum": False,
            },
            "enum": {
                "items": [
                    {
                        "name": "Max",
                        "value": 10.1
                    },
                    {
                        "name": "Min",
                        "value": -0.1,
                    },
                    {
                        "name": "Mid",
                        "hide": True,
                        "value": 5.0,
                    }
                ]
            }
        })

        arg.validate()
        print(arg.to_native())
        print(arg.to_primitive())

    def test_float32_argument(self):

        arg = CMDFloat32Arg({
            "var": "$price",
            "options": [
                "--price",
                "-p"
            ],
            "required": True,
            "help": {
                "short": "The Name Of Argument",
                "long": [
                    "Sentence 1",
                    "Sentence 2"
                ],
                "refCommands": [
                    "az network create",
                    "az vnet create",
                ]
            },
            "default": {
                "value": 1.0
            },
            "blank": {
                "value": 0.1
            },
            "format": {
                "multipleOf": 0.1,
                "maximum": 10.1,
                "exclusiveMaximum": True,
                "minimum": -0.1,
                "exclusiveMinimum": False,
            },
            "enum": {
                "items": [
                    {
                        "name": "Max",
                        "value": 10.1
                    },
                    {
                        "name": "Min",
                        "value": -0.1,
                    },
                    {
                        "name": "Mid",
                        "hide": True,
                        "value": 5.0,
                    }
                ]
            }
        })

        arg.validate()
        print(arg.to_native())
        print(arg.to_primitive())

    def test_float64_argument(self):

        arg = CMDFloat64Arg({
            "var": "$price",
            "options": [
                "--price",
                "-p"
            ],
            "required": True,
            "help": {
                "short": "The Name Of Argument",
                "long": [
                    "Sentence 1",
                    "Sentence 2"
                ],
                "refCommands": [
                    "az network create",
                    "az vnet create",
                ]
            },
            "default": {
                "value": 1.0
            },
            "blank": {
                "value": 0.1
            },
            "format": {
                "multipleOf": 0.1,
                "maximum": 10.1,
                "exclusiveMaximum": True,
                "minimum": -0.1,
                "exclusiveMinimum": False,
            },
            "enum": {
                "items": [
                    {
                        "name": "Max",
                        "value": 10.1
                    },
                    {
                        "name": "Min",
                        "value": -0.1,
                    },
                    {
                        "name": "Mid",
                        "hide": True,
                        "value": 5.0,
                    }
                ]
            }
        })

        arg.validate()
        print(arg.to_native())
        print(arg.to_primitive())

    def test_object_argument(self):

        arg = CMDObjectArg({
            "var": "$instance",
            "options": [
                "--instance",
                "-i"
            ],
            "required": True,
            "help": {
                "short": "The Name Of Argument",
                "long": [
                    "Sentence 1",
                    "Sentence 2"
                ],
                "refCommands": [
                    "az network create",
                    "az vnet create",
                ]
            },
            "default": {
                "value": {
                    "name": "aaa",
                    "age": 1
                }
            },
            "blank": {
                "value": None
            },
            "format": {
                "maxProperties": 10,
                "minProperties": 2,
            }
        })
        arg.validate()
        print(arg.to_native())
        print(arg.to_primitive())

    def test_array_argument(self):
        arg = CMDArrayArg({
            "var": "$instance",
            "options": [
                "--instance",
                "-i"
            ],
            "required": True,
            "help": {
                "short": "The Name Of Argument",
                "long": [
                    "Sentence 1",
                    "Sentence 2"
                ],
                "refCommands": [
                    "az network create",
                    "az vnet create",
                ]
            },
            "default": {
                "value": [
                    {
                        "name": "aaa",
                        "age": 1
                    },
                    {
                        "name": "bbb",
                        "age": 2
                    }
                ]
            },
            "blank": {
                "value": []
            },
            "format": {
                "unique": True,
                "maxLength": 10,
                "minLength": 2,
            },
            "item": {
                "type": "string"
            }
        })
        arg.validate()
        print(arg.to_native())
        print(arg.to_primitive())

    def test_complicated_argument(self):
        data = {
            "var": "$dataFlows",
            "options": [
                "--data-flows"
            ],
            "type": "array<object>",
            "help": {
                "short": "The specification of data flows.",
                "long": [
                    "The specification of data flows.",
                    "Multiple actions can be specified by using more than one --data-flows argument.",
                ]
            },
            "format": {
                "minLength": 1
            },
            "item": {
                "type": "object",
                "args": [
                    {
                        "var": "$dataFlows[].streams",
                        "required": True,
                        "options": [
                            "streams"
                        ],
                        "type": "array<string>",
                        "help": {
                            "short": "List of streams for this data flow.",
                        },
                        "format": {
                            "unique": True,
                            "minLength": 1
                        },
                        "item": {
                            "type": "string",
                            "enum": {
                                "items": [
                                    {
                                        "name": "Microsoft-Event",
                                        "value": "Microsoft-Event",
                                    },
                                    {
                                        "name": "Microsoft-InsightsMetrics",
                                        "value": "Microsoft-InsightsMetrics",
                                    },
                                    {
                                        "name": "Microsoft-Perf",
                                        "value": "Microsoft-Perf",
                                    },
                                    {
                                        "name": "Microsoft-Syslog",
                                        "value": "Microsoft-Syslog",
                                    },
                                    {
                                        "name": "Microsoft-WindowsEvent",
                                        "value": "Microsoft-WindowsEvent",
                                    }
                                ]
                            }
                        }
                    },
                    {
                        "var": "$dataFlows[].destinations",
                        "required": True,
                        "options": [
                            "destinations"
                        ],
                        "type": "array<string>",
                        "help": {
                            "short": "List of destinations for this data flow.",
                        },
                        "format": {
                            "minLength": 1
                        },
                        "item": {
                            "type": "string",
                        }
                    }
                ]
            }
        }
        field = PolyModelType(CMDArg, allow_subclasses=True)
        arg = field(data)

        arg.validate()
        print(arg.to_native())
        print(arg.to_primitive())
