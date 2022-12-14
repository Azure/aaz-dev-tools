
def register_blueprints(app):
    from . import az, portal
    app.register_blueprint(az.bp)
    app.register_blueprint(portal.bp)
