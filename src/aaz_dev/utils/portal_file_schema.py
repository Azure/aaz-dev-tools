
PORTAL_FILE_SCHEMA = {
    "type": "object",
    "properties": {
        "resourceType": {"type": "string"},
        "apiVersion": {"type": "string"},
        "learnMore": {
            "type": "object",
            "properties": {
                "url": {"type": "string"}
            }
        },
        "commands": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "description": {"type": "string"},
                    "path": {"type": "string"},
                    "confirmation": {"type": "boolean"},
                    "help": {
                        "type": "object",
                        "properties": {
                            "learnMore": {
                                "type": "object",
                                "properties": {
                                    "url": {"type": "string"}
                                }
                            },
                            "parameterSets": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "parameters": {
                                            "type": "array",
                                            "items": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        }
                    },
                    "examples": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "description": {"type": "string"},
                                "parameters": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "name": {"type": "string"},
                                            "value": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
