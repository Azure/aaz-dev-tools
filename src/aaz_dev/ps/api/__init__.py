
def register_blueprints(app):
    from . import _cmds, autorest, powershell
    app.register_blueprint(_cmds.bp)
    app.register_blueprint(autorest.bp)
    app.register_blueprint(powershell.bp)
