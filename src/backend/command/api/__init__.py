
def register_blueprints(app):
    from . import config, editor
    app.register_blueprint(config.bp)
    app.register_blueprint(editor.bp)
