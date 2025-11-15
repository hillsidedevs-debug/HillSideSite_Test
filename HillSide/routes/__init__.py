from .main_routes import main_bp
from .auth_routes import auth_bp
from .admin_routes import admin_bp
from .courses_routes import courses_bp
from .staff_routes import staff_bp

def register_blueprints(app):
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(courses_bp)
    app.register_blueprint(staff_bp)
