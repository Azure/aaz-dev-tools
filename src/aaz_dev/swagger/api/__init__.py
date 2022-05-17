def register_blueprints(app):
    from . import specs
    app.register_blueprint(specs.bp)
