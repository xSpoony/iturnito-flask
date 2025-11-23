from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, current_user
from ..models.user import User
from ..models.paciente import Paciente 
from ..extensions import db, limiter

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# --- RUTAS DE LOGIN ---
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = request.form.get('remember') 

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
    logout_user()
    flash('Has cerrado la sesión.', 'success')
    return redirect(url_for('main.index'))

# --- RUTAS DE REGISTRO ---
@auth_bp.route('/register', methods=['GET', 'POST'])
@limiter.limit("5 per second")
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        dni = request.form.get('dni')
        telefono = request.form.get('telefono')
        password = request.form.get('password')
        password_confirmation = request.form.get('password_confirmation')
        
        # Validar DNI 
        if not dni.isdigit():
            flash('El DNI debe contener solo números.', 'danger')
            return redirect(url_for('auth.register'))
        
        if len(dni) < 6 or len(dni) > 11: 
            flash('El DNI no tiene una longitud válida.', 'danger')
            return redirect(url_for('auth.register'))

        # Validar Teléfono 
        telefono_limpio = telefono.replace(' ', '').replace('-', '').replace('+', '')
        if not telefono_limpio.isdigit():
            flash('El teléfono contiene caracteres no válidos.', 'danger')
            return redirect(url_for('auth.register'))
        
        if len(password) < 8:
            flash('La contraseña debe tener al menos 8 digitos.', 'danger')
            return redirect(url_for('auth.register'))

        if password != password_confirmation:
            flash('Las contraseñas no coinciden.', 'danger')
            return redirect(url_for('auth.register'))

        # Verificar Email existente
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            flash('Ya existe un usuario con ese correo electrónico.', 'danger')
            return redirect(url_for('auth.register'))

        # Verificar DNI existente
        existing_dni = User.query.filter_by(dni=dni).first()
        if existing_dni:
            flash('Ya existe un usuario registrado con ese DNI.', 'danger')
            return redirect(url_for('auth.register'))

        # Crear el nuevo usuario
        new_user = User(
            name=name,
            email=email,
            rol='paciente', # Todos los registros son pacientes por defecto
            dni=dni,
            telefono=telefono,
        )
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.flush() 

        # Crear el perfil de paciente asociado
        new_paciente_perfil = Paciente(
            user_id=new_user.id
        )
        db.session.add(new_paciente_perfil)
        
        # Confirmar todo junto
        db.session.commit() 

        flash('Registro exitoso. Por favor, inicia sesión.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')

#@auth_bp.route('/password/request', methods=['GET', 'POST'])
# def password_request():
#    """Maneja la solicitud de reseteo de contraseña."""
#    if request.method == 'POST':
#        email = request.form.get('email')
#        flash('Si tu correo está en nuestro sistema, recibirás un enlace de reseteo.', 'success')
#        return redirect(url_for('auth.login'))

#    return render_template('auth/passwords/email.html')
