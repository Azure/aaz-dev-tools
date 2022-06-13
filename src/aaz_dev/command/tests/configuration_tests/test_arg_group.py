from unittest import TestCase
from command.model.configuration._arg_group import *


class ArgumentGroupTest(TestCase):

    def test_arg_group(self):
        arg_group = CMDArgGroup({
            "name": "Destinations",
            "args": [
                {
                    "var": "$logAnalytics",
                    "options": [
                        "--log-analytics",
                    ],
                    "type": "array<object>",
                    "format": {
                        "minLength": 1,
                    },
                    "help": {
                        "short": "List of Log Analytics destinations."
                    },
                    "item": {
                        "type": "object",
                        "args": [
                            {
                                "var": "$logAnalytics[].workspaceResourceId",
                                "options": [
                                    "workspace"
                                ],
                                "type": "string",
                                "required": True,
                                "help": {
                                    "short": "The resource ID of the Log Analytics workspace.",
                                }
                            },
                            {
                                "var": "$logAnalytics[].name",
                                "options": [
                                    "name"
                                ],
                                "type": "string",
                                "required": True,
                                "help": {
                                    "short": "A friendly name for the destination.",
                                    "long": [
                                        "This name should be unique across all destinations (regardless of type) within the data collection rule."
                                    ]
                                }
                            }
                        ]
                    }
                }
            ]
        })

        arg_group.validate()
        print(arg_group.to_native())
        print(arg_group.to_primitive())
