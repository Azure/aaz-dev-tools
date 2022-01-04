from flask import Flask
from utils import config
from flask.app import request
from swagger.view.specs import load_specs, get_specs_for_module


def create_app():
    app = Flask(__name__, static_folder=config.STATIC_FOLDER, static_url_path=config.STATIC_URL_PATH)

    @app.route('/', defaults={'path': ''})
    @app.route('/<string:path>')
    @app.route('/<path:path>')
    def index(path):
        if '.' in path:
            return app.send_static_file(path)
        return app.send_static_file('index.html')

    @app.route("/specifications")
    def get_specs():
        return load_specs('specs.json')

    @app.route("/specification")
    def get_specs_for():
        return get_specs_for_module(request.args.get('name'))

    return app
