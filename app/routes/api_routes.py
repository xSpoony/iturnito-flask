from flask import Blueprint, jsonify, request
from flask_login import login_required

# Prefijo /api. La protección @login_required es opcional
# dependiendo de si tu API es pública o privada.
api_bp = Blueprint('api', __name__, url_prefix='/api')
api_bp.before_request(login_required) # Protegemos todas las rutas de API

@api_bp.route('/especialidades', methods=['GET'])
def api_especialidades():
    # Lógica para buscar especialidades...
    especialidades = [
        {"id": 1, "nombre": "Cardiología"},
        {"id": 2, "nombre": "Dermatología"}
    ] # Placeholder
    return jsonify(especialidades)

@api_bp.route('/especialidad/<int:especialidad_id>/doctores', methods=['GET'])
def api_doctores_por_especialidad(especialidad_id):
   # Lógica para buscar doctores...
    doctores = [
        {"id": 1, "name": "Dr. Juan Pérez"},
        {"id": 2, "name": "Dra. Ana Gómez"}
    ] # Placeholder
    return jsonify(doctores)

@api_bp.route('/doctor/<int:doctor_id>/horarios-disponibles', methods=['GET'])
def api_horarios_disponibles(doctor_id):
   # Lógica para buscar horarios...
    horarios = [
        {"fecha": "2025-11-20", "hora": "10:00"},
        {"fecha": "2025-11-20", "hora": "10:30"}
    ] # Placeholder
    return jsonify(horarios)

# ... (El resto de rutas de API seguiría el mismo patrón)

