from flask import Blueprint, render_template, jsonify, request, flash, redirect, url_for
from flask_login import login_required, current_user
import datetime
import json
from sqlalchemy import or_, func, cast, Date, distinct
from sqlalchemy.orm import joinedload

# --- Importaciones de Modelos y DB ---
from app.models.horario_disponible import HorarioDisponible
from app.models.configuracion_horario import ConfiguracionHorario
from app.models.turno import Turno
from app.models.paciente import Paciente
from app.models.user import User
from app.models.doctor import Doctor
from app import db

# --- 1. DEFINICIÓN DEL BLUEPRINT ---
doctor_bp = Blueprint('doctor', __name__, url_prefix='/doctor')


# --- 2. SEGURIDAD DEL BLUEPRINT ---
@doctor_bp.before_request
@login_required
def check_doctor_role():
    if request.endpoint not in ['doctor.obtener_horarios']:
        if not current_user.is_authenticated or current_user.rol != 'doctor':
            flash('Acceso no autorizado.', 'danger')
            return redirect(url_for('main.index'))


# --- 3. RUTAS DEL DOCTOR ---

@doctor_bp.route('/dashboard')
def dashboard():
    """Dashboard específico del doctor con estadísticas."""
    doctor_id = current_user.doctor_perfil.id
    today = datetime.date.today()
    start_of_week = today - datetime.timedelta(days=today.weekday())
    end_of_week = start_of_week + datetime.timedelta(days=6)
    
    turnos_hoy_count = Turno.query.filter(Turno.doctor_id == doctor_id, func.date(Turno.fecha_hora) == today).count()
    turnos_semana_count = Turno.query.filter(Turno.doctor_id == doctor_id, Turno.fecha_hora.between(datetime.datetime.combine(start_of_week, datetime.time.min), datetime.datetime.combine(end_of_week, datetime.time.max))).count()
    turnos_pendientes_count = Turno.query.filter(Turno.doctor_id == doctor_id, Turno.estado == 'pendiente', Turno.fecha_hora >= datetime.datetime.now()).count()
    pacientes_count = db.session.query(func.count(distinct(Turno.paciente_id))).filter_by(doctor_id=doctor_id).scalar()

    stats = {
        'turnos_hoy': turnos_hoy_count,
        'turnos_semana': turnos_semana_count,
        'turnos_pendientes': turnos_pendientes_count,
        'pacientes': pacientes_count
    }
    return render_template('doctor/dashboard.html', stats=stats)


@doctor_bp.route('/mis-turnos')
def mis_turnos():
    
    fecha_str = request.args.get('fecha') 
    vista = request.args.get('vista', 'dia')
    estado = request.args.get('estado', 'todos')
    
    query = Turno.query.options(
        db.joinedload(Turno.paciente).joinedload(Paciente.user)
    ).filter(
        Turno.doctor_id == current_user.doctor_perfil.id
    )

    if estado != 'todos':
        query = query.filter(Turno.estado == estado)

    if fecha_str:
        fecha_obj = datetime.date.fromisoformat(fecha_str)
        if vista == 'dia':
            query = query.filter(db.func.date(Turno.fecha_hora) == fecha_obj)
        else: # vista == 'semana'
            inicio_semana = fecha_obj - datetime.timedelta(days=fecha_obj.weekday())
            fin_semana = inicio_semana + datetime.timedelta(days=6)
            query = query.filter(Turno.fecha_hora.between(
                datetime.datetime.combine(inicio_semana, datetime.time.min),
                datetime.datetime.combine(fin_semana, datetime.time.max)
            ))
    else:
        if estado == 'todos' or estado == 'pendiente':
             query = query.filter(Turno.estado == 'pendiente', Turno.fecha_hora >= datetime.datetime.now())
    
    turnos = query.order_by(Turno.fecha_hora.asc()).all()
    return render_template('doctor/mis-turnos.html', turnos=turnos)


@doctor_bp.route('/horarios')
def horarios():
    doctor_id = current_user.doctor_perfil.id
    config_obj = ConfiguracionHorario.query.filter_by(doctor_id=doctor_id).first()
    if not config_obj:
        config_obj = ConfiguracionHorario(doctor_id=doctor_id)
        db.session.add(config_obj)
        db.session.commit()
    config_json = json.dumps(config_obj.to_dict())
    horarios_db = HorarioDisponible.query.filter_by(doctor_id=doctor_id).all()
    bloques_por_dia = {i: [] for i in range(7)}
    for h in horarios_db:
        if 0 <= h.dia_semana <= 6:
            bloques_por_dia[h.dia_semana].append({'inicio': h.hora_inicio.strftime('%H:%M'), 'fin': h.hora_fin.strftime('%H:%M')})
    dias_semana_data = [
        {'codigo': 'lunes', 'nombre': 'Lunes', 'activo': False, 'bloques': []},
        {'codigo': 'martes', 'nombre': 'Martes', 'activo': False, 'bloques': []},
        {'codigo': 'miercoles', 'nombre': 'Miércoles', 'activo': False, 'bloques': []},
        {'codigo': 'jueves', 'nombre': 'Jueves', 'activo': False, 'bloques': []},
        {'codigo': 'viernes', 'nombre': 'Viernes', 'activo': False, 'bloques': []},
        {'codigo': 'sabado', 'nombre': 'Sábado', 'activo': False, 'bloques': []},
        {'codigo': 'domingo', 'nombre': 'Domingo', 'activo': False, 'bloques': []}
    ]
    default_bloque = [{'inicio': '09:00', 'fin': '17:00'}]
    for i, dia in enumerate(dias_semana_data):
        bloques = bloques_por_dia.get(i)
        if bloques:
            dia['activo'] = True
            dia['bloques'] = bloques
        else:
            dia['activo'] = False
            dia['bloques'] = default_bloque
    horarios_json = json.dumps(dias_semana_data)
    return render_template('doctor/horarios.html', config_json=config_json, horarios_json=horarios_json)


@doctor_bp.route('/pacientes')
def pacientes():
    doctor_id = current_user.doctor_perfil.id
    paciente_ids_query = db.session.query(distinct(Turno.paciente_id)).filter_by(doctor_id=doctor_id)
    paciente_ids = [id_tupla[0] for id_tupla in paciente_ids_query.all()]
    pacientes = Paciente.query.options(
        joinedload(Paciente.user)
    ).filter(
        Paciente.id.in_(paciente_ids)
    ).all()
    return render_template('doctor/pacientes.html', pacientes=pacientes)


@doctor_bp.route('/perfil', methods=['GET', 'POST'])
@login_required
def perfil():
    doctor = current_user.doctor_perfil
    if not doctor:
        flash('No se encontró el perfil de doctor.', 'danger')
        return redirect(url_for('doctor.dashboard'))
    if request.method == 'POST':
        user = current_user
        user.name = request.form.get('name')
        user.email = request.form.get('email')
        user.telefono = request.form.get('telefono')
        user.dni = request.form.get('dni')
        doctor.matricula = request.form.get('matricula') 
        existing_email = User.query.filter(User.email == user.email, User.id != user.id).first()
        existing_dni = User.query.filter(User.dni == user.dni, User.id != user.id).first()
        existing_matricula = Doctor.query.filter(Doctor.matricula == doctor.matricula, Doctor.id != doctor.id).first()
        if existing_email:
            flash('Ese email ya está en uso por otra cuenta.', 'danger')
        if existing_dni:
            flash('Ese DNI ya está en uso por otra cuenta.', 'danger')
        if existing_matricula and doctor.matricula:
            flash('Esa matrícula ya está en uso por otro doctor.', 'danger')
        if existing_email or existing_dni or (existing_matricula and doctor.matricula):
             return render_template('doctor/perfil.html', doctor=doctor)
        password = request.form.get('password')
        if password:
            user.set_password(password)
        db.session.commit()
        flash('Perfil actualizado exitosamente.', 'success')
        return redirect(url_for('doctor.perfil'))
    return render_template('doctor/perfil.html', doctor=doctor)


# --- 4. RUTAS API (Llamadas por el JavaScript) ---

@doctor_bp.route('/api/guardar-configuracion', methods=['POST'])
def guardar_configuracion():
    config = ConfiguracionHorario.query.filter_by(doctor_id=current_user.doctor_perfil.id).first()
    if not config: return jsonify({'success': False, 'message': 'Configuración no encontrada'}), 404
    data = request.json
    config.duracion_turno = int(data.get('duracion_turno', 30))
    config.modalidad = data.get('modalidad', 'presencial')
    config.precio_consulta = float(data.get('precio_consulta', 0))
    db.session.commit()
    return jsonify({'success': True, 'message': 'Configuración guardada'})

@doctor_bp.route('/api/guardar-horarios', methods=['POST'])
def guardar_horarios():
    doctor_id = current_user.doctor_perfil.id
    data = request.json
    MAPA_DIAS_STR_INT = {'lunes': 0, 'martes': 1, 'miercoles': 2, 'jueves': 3, 'viernes': 4, 'sabado': 5, 'domingo': 6}
    try:
        HorarioDisponible.query.filter_by(doctor_id=doctor_id).delete()
        nuevos_horarios = []
        for dia in data.get('horarios', []):
            if dia.get('activo'):
                dia_int = MAPA_DIAS_STR_INT.get(dia.get('codigo'))
                if dia_int is None: continue
                for bloque in dia.get('bloques', []):
                    if not bloque.get('inicio') or not bloque.get('fin'):
                        continue
                    hora_inicio_obj = datetime.time.fromisoformat(bloque.get('inicio'))
                    hora_fin_obj = datetime.time.fromisoformat(bloque.get('fin'))
                    if hora_fin_obj <= hora_inicio_obj:
                        continue 
                    nuevo_bloque = HorarioDisponible(dia_semana=dia_int, hora_inicio=hora_inicio_obj, hora_fin=hora_fin_obj, doctor_id=doctor_id)
                    nuevos_horarios.append(nuevo_bloque)
        db.session.add_all(nuevos_horarios)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Horarios guardados'})
    except Exception as e:
        db.session.rollback()
        print(f"Error al guardar horarios: {e}")
        return jsonify({'success': False, 'message': 'Error al guardar horarios'}), 500

@doctor_bp.route('/api/obtener-excepciones', methods=['GET'])
def obtener_excepciones():
    return jsonify({'excepciones': []}) 

@doctor_bp.route('/api/guardar-excepciones', methods=['POST'])
def guardar_excepciones():
    return jsonify({'success': True, 'message': 'Excepciones no implementadas'})


@doctor_bp.route('/api/horarios', methods=['GET'])
def obtener_horarios():
    try:
        doctor_id = request.args.get('doctor_id')
        fecha_str = request.args.get('fecha')
        
        if not doctor_id or not fecha_str:
            return jsonify({'error': 'Faltan parámetros'}), 400
        
        fecha_obj = datetime.date.fromisoformat(fecha_str)
        dia_semana = fecha_obj.weekday()
        
        horarios_base = HorarioDisponible.query.filter_by(doctor_id=doctor_id, dia_semana=dia_semana).all()
        if not horarios_base:
            return jsonify({'horarios': []}), 200
        
        config = ConfiguracionHorario.query.filter_by(doctor_id=doctor_id).first()
        duracion_min = config.duracion_turno if config else 30
        duracion_turno = datetime.timedelta(minutes=duracion_min)
        
        turnos_reservados = Turno.query.filter(
            Turno.doctor_id == doctor_id, 
            db.func.date(Turno.fecha_hora) == fecha_obj,
            Turno.estado.in_(['pendiente', 'confirmado']) 
        ).all()
        horas_reservadas = {turno.fecha_hora.time() for turno in turnos_reservados}
        
        horarios_disponibles_final = []
        now = datetime.datetime.now()
        
        for bloque in horarios_base:
            hora_actual = datetime.datetime.combine(fecha_obj, bloque.hora_inicio)
            hora_fin_bloque = datetime.datetime.combine(fecha_obj, bloque.hora_fin)
            
            while hora_actual < hora_fin_bloque:
                slot_reservado = hora_actual.time() in horas_reservadas
                es_futuro = fecha_obj > now.date() or hora_actual > now
                
                if not slot_reservado and es_futuro:
                    horarios_disponibles_final.append({'hora': hora_actual.strftime('%H:%M')})
                
                hora_actual += duracion_turno
                
        return jsonify({'horarios': horarios_disponibles_final}), 200
    except Exception as e:
        print(f"Error en obtener_horarios: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500
    
@doctor_bp.route('/turno/<int:turno_id>/completar', methods=['POST'])
@login_required
def completar_turno(turno_id):
    turno = Turno.query.get_or_404(turno_id)
    if turno.doctor_id != current_user.doctor_perfil.id:
        return jsonify({'success': False, 'message': 'No autorizado'}), 403
    
    turno.estado = 'completado'
    db.session.commit()
    return jsonify({'success': True, 'message': 'Turno completado'})

@doctor_bp.route('/turno/<int:turno_id>/cancelar', methods=['POST'])
@login_required
def cancelar_turno(turno_id):
    turno = Turno.query.get_or_404(turno_id)
    if turno.doctor_id != current_user.doctor_perfil.id:
        return jsonify({'success': False, 'message': 'No autorizado'}), 403
        
    turno.estado = 'cancelado'
    db.session.commit()
    return jsonify({'success': True, 'message': 'Turno cancelado'})

@doctor_bp.route('/turno/<int:turno_id>/notas', methods=['POST'])
@login_required
def guardar_notas(turno_id):
    turno = Turno.query.get_or_404(turno_id)
    if turno.doctor_id != current_user.doctor_perfil.id:
        return jsonify({'success': False, 'message': 'No autorizado'}), 403

    data = request.json
    turno.notas_doctor = data.get('notas')
    db.session.commit()
    return jsonify({'success': True, 'message': 'Notas guardadas'})

@doctor_bp.route('/turno/<int:turno_id>/videollamada', methods=['GET'])
@login_required
def iniciar_videollamada(turno_id):
    turno = Turno.query.get_or_404(turno_id)
    if turno.doctor_id != current_user.doctor_perfil.id:
        flash('No autorizado', 'danger')
        return redirect(url_for('doctor.mis_turnos'))
    
    # Placeholder: En un futuro, aquí se generaría un link único
    return f"Iniciando videollamada para el turno {turno.id}... (Placeholder)"

