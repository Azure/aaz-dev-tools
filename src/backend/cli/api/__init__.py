
def register_blueprints(app):
    from . import az
    app.register_blueprint(az.bp)
