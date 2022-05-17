import os

from cli.templates import get_templates
from cli.tests.common import CommandTestCase


class CliExtensionTemplateRenderTest(CommandTestCase):

    def test_render_extension_base(self):
        mod_name = "az-firewall"

        tmpl = get_templates()['extension']['HISTORY.rst']
        data = tmpl.render()
        output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output", mod_name, "HISTORY.rst")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(data)

        tmpl = get_templates()['extension']['readme.md']
        data = tmpl.render(
            mod_name=mod_name
        )
        output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output", mod_name, "readme.md")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(data)

        tmpl = get_templates()['extension']['setup.cfg']
        data = tmpl.render()
        output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output", mod_name, "setup.cfg")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(data)

        tmpl = get_templates()['extension']['setup.py']
        data = tmpl.render(
            mod_name=mod_name
        )
        output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output", mod_name, "setup.py")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(data)

    def test_render_azext_base(self):
        mod_name = "az-firewall"
        azext_name = f"azext_{mod_name.replace('-', '_')}"

        tmpl = get_templates()['extension']['azext_']['__init__.py']
        data = tmpl.render(
            mod_name=mod_name
        )
        output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output", mod_name,
                                   azext_name, "__init__.py")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(data)

        tmpl = get_templates()['extension']['azext_']['_help.py']
        data = tmpl.render()
        output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output", mod_name,
                                   azext_name, "_help.py")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(data)

        tmpl = get_templates()['extension']['azext_']['_params.py']
        data = tmpl.render()
        output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output", mod_name,
                                   azext_name, "_params.py")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(data)

        tmpl = get_templates()['extension']['azext_']['commands.py']
        data = tmpl.render()
        output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output", mod_name,
                                   azext_name, "commands.py")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(data)

        tmpl = get_templates()['extension']['azext_']['custom.py']
        data = tmpl.render()
        output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output", mod_name,
                                   azext_name, "custom.py")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(data)

        # tmpl = get_templates()['extension']['azext_']['azext_metadata.json']
        # data = tmpl.render(
        #     Config=Config
        # )
        # output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output", mod_name,
        #                            azext_name, "azext_metadata.json")
        # os.makedirs(os.path.dirname(output_path), exist_ok=True)
        # with open(output_path, 'w') as f:
        #     f.write(data)

    def test_render_azext_tests(self):
        mod_name = "az-firewall"
        azext_name = f"azext_{mod_name.replace('-', '_')}"

        tmpl = get_templates()['extension']['azext_']['tests']['__init__.py']
        data = tmpl.render()
        output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output", mod_name,
                                   azext_name, "tests", "__init__.py")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(data)

        tmpl = get_templates()['extension']['azext_']['tests']['profile']['__init__.py']
        profile = 'latest'

        data = tmpl.render()
        output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output", mod_name,
                                   azext_name, "tests", profile, "__init__.py")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(data)

        name = "aaz_render"
        tmpl = get_templates()['extension']['azext_']['tests']['profile']['test_.py']

        data = tmpl.render(name=name)
        output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output", mod_name,
                                   azext_name, "tests", profile, f"test_{name}.py")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(data)
