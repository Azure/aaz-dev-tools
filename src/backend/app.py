from flask import Flask, request
from swagger.view.specs import generate_specs, get_specs_for_module
import webbrowser
from threading import Timer

app = Flask(__name__, static_folder='../web/build', static_url_path='/')

@app.route("/")
def index():
    return app.send_static_file('index.html')

@app.route("/specifications")
def get_specs():
    return generate_specs()

@app.route("/specification")
def get_specs_for():
    return get_specs_for_module(request.args.get('name'))

def open_browser():
    webbrowser.open_new('http://127.0.0.1:5000/')

Timer(1, open_browser).start()