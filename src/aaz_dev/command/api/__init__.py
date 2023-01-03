
def register_blueprints(app):
    from . import _cmds, editor, specs
    app.register_blueprint(_cmds.bp)
    app.register_blueprint(editor.bp)
    app.register_blueprint(specs.bp)
