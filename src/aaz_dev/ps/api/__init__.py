
def register_blueprints(app):
    from . import _cmds, autorest, powershell, editor
    app.register_blueprint(_cmds.bp)
    app.register_blueprint(autorest.bp)
    app.register_blueprint(powershell.bp)
    app.register_blueprint(editor.bp)
