
def register_blueprints(app):
    from . import docs
    app.register_blueprint(docs.bp)
