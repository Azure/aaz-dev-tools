def register_blueprints(app):
    from . import specs, _cmds
    app.register_blueprint(_cmds.bp)
    app.register_blueprint(specs.bp)
