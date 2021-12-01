from flask import Flask, request
from swagger.view.specs import generate_specs, get_specs_for_module

app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/specifications")
def get_specs():
    return generate_specs()

@app.route("/specification")
def get_specs_for():
    return get_specs_for_module(request.args.get('name'))