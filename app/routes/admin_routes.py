from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy.orm import joinedload
from sqlalchemy import or_, func, distinct
import datetime

# --- Importaciones de Modelos y DB ---
from app.models.doctor import Doctor
from app.models.user import User
from app.models.especialidad import Especialidad
from app.models.paciente import Paciente
from app.models.turno import Turno
from app import db 


admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# --- Seguridad para todo el Blueprint de Admin ---
@admin_bp.before_request
@login_required
def check_admin_role():
    if not current_user.is_authenticated or current_user.rol != 'admin':
        flash('No tienes permisos para acceder a esta página.', 'danger')
        return redirect(url_for('main.index'))

# --- Dashboard de Admin ---
@admin_bp.route('/dashboard')
@login_required
def dashboard():
    """Dashboard específico del admin con estadísticas."""
    
    # 1. Tarjetas de Estadísticas Principales
    total_doctores = Doctor.query.count()
    total_pacientes = Paciente.query.count()
    total_especialidades = Especialidad.query.count()
    
    # 2. Turnos Hoy (de todo el sistema)
    today = datetime.date.today()
    turnos_hoy_admin = Turno.query.filter(func.date(Turno.fecha_hora) == today).count()

    # 3. Turnos por Estado (Gráfico/Lista)
    turnos_por_estado = db.session.query(
        Turno.estado, func.count(Turno.id)
    ).group_by(Turno.estado).all()

    # 4. Especialidades Más Solicitadas (Gráfico/Lista)
    especialidades_populares = db.session.query(
        Especialidad.nombre, func.count(Turno.id).label('total_turnos')
    ).join(Doctor, Turno.doctor_id == Doctor.id)\
     .join(Especialidad, Doctor.especialidad_id == Especialidad.id)\
     .group_by(Especialidad.nombre)\
     .order_by(func.count(Turno.id).desc())\
     .limit(5).all()

    # 5. Actividad Reciente (Últimos 5 turnos creados)
    actividad_reciente = Turno.query.options(
        joinedload(Turno.doctor).joinedload(Doctor.user),
        joinedload(Turno.paciente).joinedload(Paciente.user)
    ).order_by(Turno.id.desc()).limit(5).all()

    stats = {
        'total_doctores': total_doctores,
        'total_pacientes': total_pacientes,
        'total_especialidades': total_especialidades,
        'turnos_hoy_admin': turnos_hoy_admin,
        'turnos_por_estado': dict(turnos_por_estado), # Convertir a dict para fácil acceso
        'especialidades_populares': especialidades_populares,
        'actividad_reciente': actividad_reciente
    }

    return render_template('admin/dashboard.html', stats=stats)

# --- Gestión de Doctores (Completo) ---
@admin_bp.route('/doctores', methods=['GET'])
def doctores_index():
    doctores = Doctor.query.options(joinedload(Doctor.user), joinedload(Doctor.especialidad)).all()
    return render_template('admin/doctores/index.html', doctores=doctores)

@admin_bp.route('/doctores/crear', methods=['GET'])
def doctores_crear():
    especialidades = Especialidad.query.order_by(Especialidad.nombre).all()
    return render_template('admin/doctores/form.html', especialidades=especialidades, doctor=None)

@admin_bp.route('/doctores', methods=['POST'])
def doctores_guardar():
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')
    telefono = request.form.get('telefono')
    dni = request.form.get('dni')
    especialidad_id = request.form.get('especialidad_id')
    existing_user_email = User.query.filter_by(email=email).first()
    existing_user_dni = User.query.filter_by(dni=dni).first()
    if existing_user_email or existing_user_dni:
        flash('El email o DNI ya están registrados.', 'danger')
        especialidades = Especialidad.query.order_by(Especialidad.nombre).all()
        return render_template('admin/doctores/form.html', especialidades=especialidades, doctor=None, old_name=name, old_email=email, old_telefono=telefono, old_dni=dni)
    nuevo_usuario = User(name=name, email=email, rol='doctor', telefono=telefono, dni=dni)
    nuevo_usuario.set_password(password)
    db.session.add(nuevo_usuario)
    db.session.flush() 
    nuevo_doctor = Doctor(user_id=nuevo_usuario.id, especialidad_id=especialidad_id)
    db.session.add(nuevo_doctor)
    db.session.commit()
    flash('Doctor creado exitosamente.', 'success')
    return redirect(url_for('admin.doctores_index'))

@admin_bp.route('/doctores/<int:doctor_id>/editar', methods=['GET'])
def doctores_editar(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    especialidades = Especialidad.query.order_by(Especialidad.nombre).all()
    return render_template('admin/doctores/form.html', doctor=doctor, especialidades=especialidades)

@admin_bp.route('/doctores/<int:doctor_id>/actualizar', methods=['POST'])
def doctores_actualizar(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    user = doctor.user
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')
    telefono = request.form.get('telefono')
    dni = request.form.get('dni')
    especialidad_id = request.form.get('especialidad_id')
    existing_user_email = User.query.filter(User.email == email, User.id != user.id).first()
    existing_user_dni = User.query.filter(User.dni == dni, User.id != user.id).first()
    if existing_user_email or existing_user_dni:
        flash('El email o DNI ya están en uso por otra cuenta.', 'danger')
        especialidades = Especialidad.query.order_by(Especialidad.nombre).all()
        return render_template('admin/doctores/form.html', especialidades=especialidades, doctor=doctor)
    user.name = name
    user.email = email
    user.telefono = telefono
    user.dni = dni
    doctor.especialidad_id = especialidad_id
    if password:
        user.set_password(password)
    db.session.commit()
    flash('Doctor actualizado exitosamente.', 'success')
    return redirect(url_for('admin.doctores_index'))

@admin_bp.route('/doctores/<int:doctor_id>/eliminar', methods=['POST'])
def doctores_eliminar(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    user = doctor.user
    db.session.delete(doctor)
    if user:
        db.session.delete(user)
    db.session.commit()
    flash('Doctor eliminado exitosamente.', 'danger')
    return redirect(url_for('admin.doctores_index'))

# --- Gestión de Especialidades (Completo) ---
@admin_bp.route('/especialidades', methods=['GET'])
def especialidades_index():
    especialidades = Especialidad.query.order_by(Especialidad.nombre).all()
    return render_template('admin/especialidades/index.html', especialidades=especialidades)

@admin_bp.route('/especialidades/crear', methods=['GET'])
def especialidades_crear():
    return render_template('admin/especialidades/form.html', especialidad=None)

@admin_bp.route('/especialidades', methods=['POST'])
def especialidades_guardar():
    nombre = request.form.get('nombre')
    if not nombre:
        flash('El nombre es obligatorio.', 'danger')
        return render_template('admin/especialidades/form.html', especialidad=None)
    nueva_esp = Especialidad(nombre=nombre)
    db.session.add(nueva_esp)
    db.session.commit()
    flash('Especialidad creada exitosamente.', 'success')
    return redirect(url_for('admin.especialidades_index'))

@admin_bp.route('/especialidades/<int:esp_id>/editar', methods=['GET'])
def especialidades_editar(esp_id):
    especialidad = Especialidad.query.get_or_404(esp_id)
    return render_template('admin/especialidades/form.html', especialidad=especialidad)

@admin_bp.route('/especialidades/<int:esp_id>/actualizar', methods=['POST'])
def especialidades_actualizar(esp_id):
    especialidad = Especialidad.query.get_or_404(esp_id)
    nombre = request.form.get('nombre')
    if not nombre:
        flash('El nombre es obligatorio.', 'danger')
        return render_template('admin/especialidades/form.html', especialidad=especialidad)
    especialidad.nombre = nombre
    db.session.commit()
    flash('Especialidad actualizada exitosamente.', 'success')
    return redirect(url_for('admin.especialidades_index'))

@admin_bp.route('/especialidades/<int:esp_id>/eliminar', methods=['POST'])
def especialidades_eliminar(esp_id):
    especialidad = Especialidad.query.get_or_404(esp_id)
    if especialidad.doctores:
        flash('No se puede eliminar la especialidad porque tiene doctores asignados.', 'danger')
        return redirect(url_for('admin.especialidades_index'))
    db.session.delete(especialidad)
    db.session.commit()
    flash('Especialidad eliminada exitosamente.', 'danger')
    return redirect(url_for('admin.especialidades_index'))

# --- Gestión de Pacientes (Completo) ---
@admin_bp.route('/pacientes', methods=['GET'])
def pacientes_index():
    pacientes = Paciente.query.options(joinedload(Paciente.user)).all()
    return render_template('admin/pacientes/index.html', pacientes=pacientes)

@admin_bp.route('/pacientes/crear', methods=['GET'])
def pacientes_crear():
    return render_template('admin/pacientes/form.html', paciente=None)

@admin_bp.route('/pacientes', methods=['POST'])
def pacientes_guardar():
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')
    telefono = request.form.get('telefono')
    dni = request.form.get('dni')
    obra_social = request.form.get('obra_social')
    existing_user_email = User.query.filter_by(email=email).first()
    existing_user_dni = User.query.filter_by(dni=dni).first()
    if existing_user_email or existing_user_dni:
        flash('El email o DNI ya están registrados.', 'danger')
        return render_template('admin/pacientes/form.html', paciente=None, old_name=name, old_email=email, old_telefono=telefono, old_dni=dni, old_obra_social=obra_social)
    nuevo_usuario = User(name=name, email=email, rol='paciente', telefono=telefono, dni=dni)
    nuevo_usuario.set_password(password)
    db.session.add(nuevo_usuario)
    db.session.flush() 
    nuevo_paciente = Paciente(user_id=nuevo_usuario.id, obra_social=obra_social)
    db.session.add(nuevo_paciente)
    db.session.commit()
    flash('Paciente creado exitosamente.', 'success')
    return redirect(url_for('admin.pacientes_index'))

@admin_bp.route('/pacientes/<int:pac_id>/editar', methods=['GET'])
def pacientes_editar(pac_id):
    paciente = Paciente.query.get_or_404(pac_id)
    return render_template('admin/pacientes/form.html', paciente=paciente)

@admin_bp.route('/pacientes/<int:pac_id>/actualizar', methods=['POST'])
def pacientes_actualizar(pac_id):
    paciente = Paciente.query.get_or_404(pac_id)
    user = paciente.user
    name = request.form.get('name')
    email = request.form.get('email')
    password = request.form.get('password')
    telefono = request.form.get('telefono')
    dni = request.form.get('dni')
    obra_social = request.form.get('obra_social')
    existing_user_email = User.query.filter(User.email == email, User.id != user.id).first()
    existing_user_dni = User.query.filter(User.dni == dni, User.id != user.id).first()
    if existing_user_email or existing_user_dni:
        flash('El email o DNI ya están en uso por otra cuenta.', 'danger')
        return render_template('admin/pacientes/form.html', paciente=paciente)
    user.name = name
    user.email = email
    user.telefono = telefono
    user.dni = dni
    if password:
        user.set_password(password)
    paciente.obra_social = obra_social
    db.session.commit()
    flash('Paciente actualizado exitosamente.', 'success')
    return redirect(url_for('admin.pacientes_index'))

@admin_bp.route('/pacientes/<int:pac_id>/eliminar', methods=['POST'])
def pacientes_eliminar(pac_id):
    paciente = Paciente.query.get_or_404(pac_id)
    user = paciente.user
    if paciente.turnos:
        flash('No se puede eliminar el paciente porque tiene turnos asignados.', 'danger')
        return redirect(url_for('admin.pacientes_index'))
    db.session.delete(paciente)
    if user:
        db.session.delete(user)
    db.session.commit()
    flash('Paciente eliminado exitosamente.', 'danger')
    return redirect(url_for('admin.pacientes_index'))


# --- Gestión de Turnos (Completo) ---
@admin_bp.route('/turnos')
def turnos_index():
    turnos = Turno.query.options(
        joinedload(Turno.doctor).joinedload(Doctor.user),
        joinedload(Turno.paciente).joinedload(Paciente.user)
    ).order_by(Turno.fecha_hora.desc()).all()
    return render_template('admin/turnos/index.html', turnos=turnos) 

# --- Gestión de Reportes (Placeholder) ---
@admin_bp.route('/reportes')
def reportes_index():
    # Placeholder - La lógica de reportes puede ser compleja
    return render_template('admin/reportes/index.html')

