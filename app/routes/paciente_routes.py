from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from sqlalchemy.orm import joinedload
from sqlalchemy import distinct
import datetime

from app.models.user import User
from app.models.doctor import Doctor
from app.models.turno import Turno
from app.models.paciente import Paciente
from app.models.horario_disponible import HorarioDisponible
from app import db


paciente_bp = Blueprint('paciente', __name__, url_prefix='/paciente')

# --- Seguridad para todo el Blueprint de Paciente ---
@paciente_bp.before_request
@login_required
def check_paciente_role():
    if not current_user.is_authenticated or current_user.rol != 'paciente':
        flash('No tienes permisos para acceder a esta página.', 'danger')
        if current_user.rol == 'admin':
            return redirect(url_for('admin.dashboard'))
        if current_user.rol == 'doctor':
            return redirect(url_for('doctor.dashboard'))
        return redirect(url_for('main.index'))


# --- Dashboard de Paciente ---
@paciente_bp.route('/dashboard')
@login_required
def dashboard():
    paciente = current_user.paciente_perfil
    proximos_turnos = []
    show_videocall_button = False
    if paciente:
        proximos_turnos = Turno.query.options(
            joinedload(Turno.doctor).joinedload(Doctor.user)
        ).filter(
            Turno.paciente_id == paciente.id,
            Turno.fecha_hora >= datetime.datetime.now(),
            Turno.estado == 'pendiente'
        ).order_by(Turno.fecha_hora.asc()).all()
    if proximos_turnos:
        proximo_turno = proximos_turnos[0]
        now = datetime.datetime.now()
        if proximo_turno.fecha_hora.date() == now.date():
            time_diff_minutes = (proximo_turno.fecha_hora - now).total_seconds() / 60
            if 0 < time_diff_minutes <= 30:
                show_videocall_button = True
    return render_template(
        'paciente/dashboard.html',
        proximos_turnos=proximos_turnos,
        show_videocall_button=show_videocall_button
    )

# --- Gestión del Perfil (Formulario 1) ---
@paciente_bp.route('/perfil', methods=['GET', 'POST'])
@login_required
def perfil():
    if request.method == 'POST':
        user = current_user
        user.name = request.form.get('name')
        user.email = request.form.get('email')
        user.telefono = request.form.get('telefono')
        user.dni = request.form.get('dni')
        existing_email = User.query.filter(User.email == user.email, User.id != user.id).first()
        existing_dni = User.query.filter(User.dni == user.dni, User.id != user.id).first()
        if existing_email:
            flash('Ese email ya está en uso por otra cuenta.', 'danger')
            return render_template('paciente/perfil.html')
        if existing_dni:
            flash('Ese DNI ya está en uso por otra cuenta.', 'danger')
            return render_template('paciente/perfil.html')
        if user.paciente_perfil:
            user.paciente_perfil.obra_social = request.form.get('obra_social')
        db.session.commit()
        flash('Datos del perfil actualizados exitosamente.', 'success')
        return redirect(url_for('paciente.perfil'))
    return render_template('paciente/perfil.html')


# --- Cambiar Contraseña (Formulario 2) ---
@paciente_bp.route('/cambiar-password', methods=['POST'])
@login_required
def cambiar_password():
    current_password = request.form.get('current_password')
    new_password = request.form.get('password')
    confirm_password = request.form.get('password_confirmation')
    if not current_user.check_password(current_password):
        flash('La contraseña actual es incorrecta.', 'danger')
        return redirect(url_for('paciente.perfil'))
    if new_password != confirm_password:
        flash('La nueva contraseña y la confirmación no coinciden.', 'danger')
        return redirect(url_for('paciente.perfil'))
    current_user.set_password(new_password)
    db.session.commit()
    flash('Contraseña actualizada exitosamente.', 'success')
    return redirect(url_for('paciente.perfil'))


# --- Mis Turnos ---
@paciente_bp.route('/mis-turnos')
@login_required
def mis_turnos():
    paciente_id = current_user.paciente_perfil.id
    
    # Cargar turnos con la info del doctor y el user del doctor
    turnos = Turno.query.options(
        joinedload(Turno.doctor).joinedload(Doctor.user)
    ).filter(
        Turno.paciente_id == paciente_id
    ).order_by(Turno.fecha_hora.desc()).all() # Ordenar del más nuevo al más viejo

    # Separar en próximos y pasados
    now = datetime.datetime.now()
    turnos_proximos = [t for t in turnos if t.fecha_hora >= now and t.estado == 'pendiente']
    turnos_pasados = [t for t in turnos if t.fecha_hora < now or t.estado != 'pendiente']
    
    # Re-ordenar los próximos para que el más cercano esté primero
    turnos_proximos.reverse()

    return render_template('paciente/mis-turnos.html', 
                           turnos_proximos=turnos_proximos,
                           turnos_pasados=turnos_pasados)


# --- Reservar Turno (GET) ---
@paciente_bp.route('/reservar-turno')
@login_required
def reservar_turno():
    
    hoy = datetime.date.today()
    current_year = hoy.year
    current_month = hoy.month

    doctores = Doctor.query.options(
        joinedload(Doctor.user),
        joinedload(Doctor.especialidad),
        joinedload(Doctor.configuracion),
    ).all()
    
    doctores_con_disponibilidad = []
    for doctor in doctores:
        config = doctor.configuracion
        if config:
            modalidad_final = config.modalidad
            precio_final = config.precio_consulta
        else:
            modalidad_final = 'presencial' 
            precio_final = 0.0
        
        dias_disponibles = obtener_dias_disponibles_del_mes(
            doctor.id, 
            current_year, 
            current_month
        )
        
        doctor.modalidad = modalidad_final
        doctor.precio_consulta = precio_final
        doctor.dias_disponibles_mes_actual = dias_disponibles 
        
        doctores_con_disponibilidad.append(doctor)
    
    return render_template('paciente/reservar-turno.html', doctores=doctores_con_disponibilidad)

# --- Confirmar Turno (POST API) ---
@paciente_bp.route('/confirmar-turno', methods=['POST'])
@login_required
def confirmar_turno():
    try:
        data = request.json
        doctor_id_recibido = data.get('doctor_id')
        
        if isinstance(doctor_id_recibido, dict) and 'id' in doctor_id_recibido:
             doctor_id_final = doctor_id_recibido.get('id')
        else:
             doctor_id_final = doctor_id_recibido 
        
        fecha_str = data.get('fecha')
        hora_str = data.get('hora')
        fecha_hora_str = f"{fecha_str} {hora_str}"
        fecha_hora_obj = datetime.datetime.strptime(fecha_hora_str, '%Y-%m-%d %H:%M')
        
        nuevo_turno = Turno(
            fecha_hora=fecha_hora_obj,
            estado='pendiente',
            doctor_id=doctor_id_final, 
            paciente_id=current_user.paciente_perfil.id
        )
        db.session.add(nuevo_turno)
        db.session.commit()
        return jsonify({'success': True, 'message': '¡Turno reservado exitosamente!'}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Error al reservar turno: {e}")
        return jsonify({'success': False, 'message': 'Error interno al procesar la reserva.'}), 500

@paciente_bp.route('/mis-turnos/<int:turno_id>/cancelar', methods=['POST'])
@login_required
def cancelar_turno(turno_id):
    """Permite a un paciente cancelar su propio turno."""
    turno = Turno.query.get_or_404(turno_id)
    
    # Seguridad: Verificar que el turno pertenece al paciente logueado
    if turno.paciente_id != current_user.paciente_perfil.id:
        flash('No tienes permisos para cancelar este turno.', 'danger')
        return redirect(url_for('paciente.mis_turnos'))
        
    # Solo se pueden cancelar turnos pendientes
    if turno.estado != 'pendiente':
        flash('Este turno ya no puede ser cancelado.', 'warning')
        return redirect(url_for('paciente.mis_turnos'))

    turno.estado = 'cancelado'
    db.session.commit()
    
    flash('Turno cancelado exitosamente.', 'success')
    return redirect(url_for('paciente.mis_turnos'))

def obtener_dias_disponibles_del_mes(doctor_id, year, month):
    #Calcula qué días del mes tienen al menos un horario base configurado.
    
    dias_semana_con_horario = db.session.query(
        distinct(HorarioDisponible.dia_semana)
    ).filter(
        HorarioDisponible.doctor_id == doctor_id
    ).all()
    
    dias_semana_set = {d[0] for d in dias_semana_con_horario} 

    if not dias_semana_set:
        return []
    
    dias_disponibles = set()
    
    try:
        inicio_mes = datetime.date(year, month, 1)
        if month == 12:
            fin_rango = datetime.date(year + 1, 1, 1)
        else:
            fin_rango = datetime.date(year, month + 1, 1)
    except ValueError:
        return []

    fecha_actual = inicio_mes
    hoy = datetime.date.today()
    
    while fecha_actual < fin_rango:
        # Solo incluimos días futuros o el día actual
        if fecha_actual >= hoy: 
            if fecha_actual.weekday() in dias_semana_set:
                dias_disponibles.add(fecha_actual.day)
        
        fecha_actual += datetime.timedelta(days=1)
        
    return sorted(list(dias_disponibles))
