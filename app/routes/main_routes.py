from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

# Creamos el Blueprint para las rutas principales
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Página de bienvenida pública."""
    if current_user.is_authenticated:
        # Si ya está logueado, redirigir a su dashboard correspondiente
        return redirect(url_for('main.dashboard'))

    return render_template('welcome.html')

# --- DASHBOARD HUB ---

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """
    Ruta genérica de dashboard.
    Redirige al blueprint de dashboard correcto según el rol del usuario.
    
    ¡ESTA ES LA CORRECCIÓN CLAVE!
    Ahora redirige a los blueprints correctos (ej: 'admin.dashboard')
    en lugar de a otras rutas en 'main' (ej: 'main.admin_dashboard').
    """
    if current_user.rol == 'admin':
        return redirect(url_for('admin.dashboard'))
    elif current_user.rol == 'doctor':
        return redirect(url_for('doctor.dashboard'))
    else:
        # Asumimos que el rol por defecto es 'paciente'
        return redirect(url_for('paciente.dashboard'))

# --- NOTA ---
# Las funciones 'paciente_dashboard', 'doctor_dashboard' y 'admin_dashboard'
# han sido MOVIDAS a sus respectivos archivos de rutas (paciente_routes.py, etc.)

