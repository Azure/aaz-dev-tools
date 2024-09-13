
_templates = None


def get_templates():
    global _templates
    if _templates is None:
        import os
        from jinja2 import Environment, FileSystemLoader
        from ._filters import custom_filters
        env = Environment(loader=FileSystemLoader(searchpath=os.path.dirname(os.path.abspath(__file__))))
        env.filters.update(custom_filters)
        _templates = {
            'aaz': {
                '__init__.py': env.get_template("aaz/__init__.py.j2"),
                'profile': {
                    '__init__.py': env.get_template("aaz/profile/__init__.py.j2"),
                    '_clients.py': env.get_template("aaz/profile/_clients.py.j2"),
                },
                'group': {
                    '__cmd_group.py': env.get_template("aaz/group/__cmd_group.py.j2"),
                    '__init__.py': env.get_template("aaz/group/__init__.py.j2"),
                },
                'command': {
                    '_cmd.py': env.get_template("aaz/command/_cmd.py.j2"),
                }
            },
            'extension': {
                "HISTORY.rst": env.get_template("extension/HISTORY.rst.j2"),
                "README.md": env.get_template("extension/README.md.j2"),
                "setup.cfg": env.get_template("extension/setup.cfg.j2"),
                "setup.py": env.get_template("extension/setup.py.j2"),
                "azext_": {
                    "__init__.py": env.get_template("extension/azext_/__init__.py.j2"),
                    "_help.py": env.get_template("extension/azext_/_help.py.j2"),
                    "_params.py": env.get_template("extension/azext_/_params.py.j2"),
                    # "azext_metadata.json": env.get_template("extension/azext_/azext_metadata.json.j2"),
                    "commands.py": env.get_template("extension/azext_/commands.py.j2"),
                    "custom.py": env.get_template("extension/azext_/custom.py.j2"),
                    "tests": {
                        "__init__.py": env.get_template("extension/azext_/tests/__init__.py.j2"),
                        "profile": {
                            "__init__.py": env.get_template("extension/azext_/tests/profile/__init__.py.j2"),
                            "test_.py": env.get_template("extension/azext_/tests/profile/test_.py.j2"),
                        }
                    }
                }
            },
            'main': {
                "__init__.py": env.get_template("main/__init__.py.j2"),
                "_help.py": env.get_template("main/_help.py.j2"),
                "_params.py": env.get_template("main/_params.py.j2"),
                "commands.py": env.get_template("main/commands.py.j2"),
                "custom.py": env.get_template("main/custom.py.j2"),
                "tests": {
                    "__init__.py": env.get_template("main/tests/__init__.py.j2"),
                    "profile": {
                        "__init__.py": env.get_template("main/tests/profile/__init__.py.j2"),
                        "test_.py": env.get_template("main/tests/profile/test_.py.j2"),
                    }
                }
            },
            'powershell': {
                "configuration": env.get_template("powershell/configuration.yaml.j2")
            },
        }
    return _templates
