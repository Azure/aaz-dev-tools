import os

from cli.templates import get_templates
from cli.tests.common import CommandTestCase


class CliMainTemplateRenderTest(CommandTestCase):

    def test_render_module_common(self):
        mod_name = "hd-insight"
        pkg_name = mod_name.replace('-', '_')

        tmpl = get_templates()['main']['__init__.py']
        data = tmpl.render(
            mod_name=mod_name
        )
        output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output", pkg_name, "__init__.py")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(data)

        tmpl = get_templates()['main']['_help.py']
        data = tmpl.render()
        output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output", pkg_name, "_help.py")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(data)

        tmpl = get_templates()['main']['_params.py']
        data = tmpl.render()
        output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output", pkg_name, "_params.py")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(data)

        tmpl = get_templates()['main']['commands.py']
        data = tmpl.render()
        output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output", pkg_name, "commands.py")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(data)

        tmpl = get_templates()['main']['custom.py']
        data = tmpl.render()
        output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output", pkg_name, "custom.py")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(data)

    def test_render_tests(self):
        mod_name = "hd-insight"
        pkg_name = mod_name.replace('-', '_')
        profile = 'latest'

        tmpl = get_templates()['main']['tests']['__init__.py']
        data = tmpl.render()
        output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output", pkg_name, "tests",
                                   "__init__.py")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(data)

        tmpl = get_templates()['main']['tests']['profile']['__init__.py']
        data = tmpl.render()
        output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output", pkg_name, "tests", profile,
                                   "__init__.py")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(data)

        name = "aaz_render"
        tmpl = get_templates()['main']['tests']['profile']['test_.py']
        data = tmpl.render(name=name)
        output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output", pkg_name, "tests", profile,
                                   f"test_{name}.py")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(data)
