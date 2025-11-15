from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, current_user
from ..models.user import User
from ..models.paciente import Paciente # Para crear el perfil de paciente
from ..extensions import db, bcrypt

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# --- RUTAS DE LOGIN ---
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Maneja el inicio de sesión del usuario (antes 'iniciar-sesion')"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = request.form.get('remember') == 'true'

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user, remember=remember)
            flash('Inicio de sesión exitoso', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            flash('Correo electrónico o contraseña incorrectos.', 'danger')
            return redirect(url_for('auth.login'))

    return render_template('auth/login.html')

@auth_bp.route('/logout', methods=['GET'])
def logout():
    """Cierra la sesión del usuario (antes 'cerrar-sesion')"""
    logout_user()
    flash('Has cerrado la sesión.', 'success')
    return redirect(url_for('main.index'))

# --- RUTAS DE REGISTRO ---
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Maneja el registro de un nuevo paciente (antes 'registro')"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        password_confirmation = request.form.get('password_confirmation')

        if password != password_confirmation:
            flash('Las contraseñas no coinciden.', 'danger')
            return redirect(url_for('auth.register'))

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Ya existe un usuario con ese correo electrónico.', 'danger')
            return redirect(url_for('auth.register'))

        # Crear el nuevo usuario
        new_user = User(
            name=name,
            email=email,
            rol='paciente' # Todos los registros son pacientes por defecto
        )
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit() # Guardamos el usuario para obtener un user.id

        # Crear el perfil de paciente asociado
        new_paciente_perfil = Paciente(
            user_id=new_user.id
            # otros campos como 'obra_social' se pueden añadir aquí
        )
        db.session.add(new_paciente_perfil)
        db.session.commit()

        flash('Registro exitoso. Por favor, inicia sesión.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')

# --- ¡RUTA CORREGIDA! ---
# Esta es la función que faltaba y que causaba el error 'BuildError'
@auth_bp.route('/password/request', methods=['GET', 'POST'])
def password_request():
    """Maneja la solicitud de reseteo de contraseña."""
    if request.method == 'POST':
        # Aquí iría la lógica real para buscar el email
        # y enviar un correo de reseteo.
        email = request.form.get('email')
        flash('Si tu correo está en nuestro sistema, recibirás un enlace de reseteo.', 'success')
        return redirect(url_for('auth.login'))

    # Muestra la plantilla que ya traducimos
    return render_template('auth/passwords/email.html')

