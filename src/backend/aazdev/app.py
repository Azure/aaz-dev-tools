from flask import Flask
from flask.cli import FlaskGroup, shell_command, routes_command
from utils import Config

from .run import run_command


def create_app():
    app = Flask(__name__, static_folder=Config.STATIC_FOLDER, static_url_path=Config.STATIC_URL_PATH)

    @app.route('/', defaults={'path': ''})
    @app.route('/<string:path>')
    @app.route('/<path:path>')
    def index(path):
        if '.' in path:
            return app.send_static_file(path)
        return app.send_static_file('index.html')

    # register routes of swagger module
    from swagger.api import register_blueprints
    register_blueprints(app)

    # register routes of command module
    from command.api import register_blueprints
    register_blueprints(app)

    # register routes of cli module
    from cli.api import register_blueprints
    register_blueprints(app)

    return app


cli = FlaskGroup(
    create_app=create_app,
    add_default_commands=False
)

cli.add_command(shell_command)
cli.add_command(routes_command)
cli.add_command(run_command)
