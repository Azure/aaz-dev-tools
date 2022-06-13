
def register_blueprints(app):
    from . import config, editor, specs
    app.register_blueprint(config.bp)
    app.register_blueprint(editor.bp)
    app.register_blueprint(specs.bp)
