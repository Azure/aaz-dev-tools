
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
            'main': {
                "__init__.py": env.get_template("main/__init__.py.j2"),
                "_help.py": env.get_template("main/_help.py.j2"),
                "_params.py": env.get_template("main/_params.py.j2"),
                "commands.py": env.get_template("main/commands.py.j2"),
                "custom.py": env.get_template("main/custom.py.j2"),
            },
        }
    return _templates
