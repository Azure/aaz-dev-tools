def register_blueprints(app):
    from . import _cmds
    app.register_blueprint(_cmds.bp)
    # app.register_blueprint(az.bp)
    # app.register_blueprint(portal.bp)
