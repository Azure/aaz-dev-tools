import json

from flask import Flask, jsonify
from flask.cli import FlaskGroup, shell_command, routes_command
from flask.logging import create_logger

from utils import exceptions
from utils.config import Config
from aaz_dev.app.run import run_command


def create_app():
    app = Flask(__name__, static_folder=Config.STATIC_FOLDER, static_url_path=Config.STATIC_URL_PATH)
    logger = create_logger(app)

    @app.route('/', defaults={'path': ''})
    @app.route('/<string:path>')
    @app.route('/<path:path>')
    def index(path):
        if '.' in path:
            return app.send_static_file(path)
        return app.send_static_file('index.html')

    @app.errorhandler(exceptions.InvalidAPIUsage)
    def invalid_api_usage(e):
        logger.error(f'InvalidAPIUsage:\n{json.dumps(e.to_dict(), indent=2)}',)
        return jsonify(e.to_dict()), e.status_code

    # register url converters
    from .url_converters import Base64Converter, NameConverter, NameWithCapitalConverter, NamesPathConverter, ListPathConvertor
    app.url_map.converters['base64'] = Base64Converter
    app.url_map.converters['name'] = NameConverter
    app.url_map.converters['Name'] = NameWithCapitalConverter
    app.url_map.converters['names_path'] = NamesPathConverter
    app.url_map.converters['list_path'] = ListPathConvertor

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
