from flask import Flask, request
from swagger.view.specs import load_specs, get_specs_for_module
import webbrowser
from threading import Timer
import click
from flask.cli import FlaskGroup

def open_browser():
    webbrowser.open_new('http://127.0.0.1:5000/')

def create_app():
    app = Flask(__name__, static_folder='../web/build', static_url_path='/')
    # other setup

    @app.route("/")
    def index():
        return app.send_static_file('index.html')

    @app.route("/specifications")
    def get_specs():
        return load_specs('specs.json')

    @app.route("/specification")
    def get_specs_for():
        return get_specs_for_module(request.args.get('name'))

    Timer(1, open_browser).start()
    return app

@click.group(cls=FlaskGroup, create_app=create_app)
def cli():
    """Management script for the aazdev application."""
