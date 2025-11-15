import os
from flask import Flask
from .extensions import db, migrate, login_manager, bcrypt
from .models.user import User 

def create_app():
    app = Flask(__name__)

    # --- Configuración ---
    app.config.from_object('app.configs.config.Config')

    # --- Inicializar Extensiones ---
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bcrypt.init_app(app)

    # --- Configuración de Flask-Login ---
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @login_manager.unauthorized_handler
    def unauthorized():
        flash('Debes iniciar sesión para ver esta página.', 'danger')
        return redirect(url_for('auth.login'))

    # --- Registrar Blueprints (Rutas) ---
    with app.app_context():
        from .routes.main_routes import main_bp
        from .routes.auth_routes import auth_bp
        from .routes.paciente_routes import paciente_bp
        from .routes.doctor_routes import doctor_bp
        from .routes.admin_routes import admin_bp
        from .routes.api_routes import api_bp

        app.register_blueprint(main_bp)
        app.register_blueprint(auth_bp)
        app.register_blueprint(paciente_bp)
        app.register_blueprint(doctor_bp)
        app.register_blueprint(admin_bp)
        app.register_blueprint(api_bp)

    return app

