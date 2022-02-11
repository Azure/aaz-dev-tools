import os

from cli.templates import get_templates
from cli.tests.common import CommandTestCase


class TemplateRenderTest(CommandTestCase):

    def test_render_init(self):
        tmpl = get_templates()['main']['__init__.py']
        data = tmpl.render(
            pkg_name="hd_insight"
        )

        output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output", "module", "__init__.py")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(data)

    def test_render_help(self):
        tmpl = get_templates()['main']['_help.py']
        data = tmpl.render()

        output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output", "module", "_help.py")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(data)

    def test_render_params(self):
        tmpl = get_templates()['main']['_params.py']
        data = tmpl.render()

        output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output", "module", "_params.py")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(data)

    def test_render_commands(self):
        tmpl = get_templates()['main']['commands.py']
        data = tmpl.render()

        output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output", "module", "commands.py")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(data)

    def test_render_custom(self):
        tmpl = get_templates()['main']['custom.py']
        data = tmpl.render()

        output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output", "module", "custom.py")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(data)
