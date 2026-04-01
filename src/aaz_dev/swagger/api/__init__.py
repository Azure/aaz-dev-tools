from flask.app import Flask

def register_blueprints(app: Flask) -> None:
    from . import specs, _cmds
    app.register_blueprint(_cmds.bp)
    app.register_blueprint(specs.bp)
