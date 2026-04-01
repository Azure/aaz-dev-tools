
from flask.app import Flask

def register_blueprints(app: Flask) -> None:
    from . import az, portal, _cmds
    app.register_blueprint(_cmds.bp)
    app.register_blueprint(az.bp)
    app.register_blueprint(portal.bp)
