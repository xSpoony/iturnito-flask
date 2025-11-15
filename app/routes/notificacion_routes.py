from app import Blueprint, jsonify, request, db
import importlib.util, os, sys

noti_bp = Blueprint('notificaciones', __name__)

def _load_models():
    base = os.path.join(os.getcwd(), 'flask', 'models')
    models = {}
    for name in ('user', 'paciente'):
        mod_name = f'local_models.{name}'
        if mod_name in sys.modules:
            mod = sys.modules[mod_name]
        else:
            path = os.path.join(base, f'{name}.py')
            spec = importlib.util.spec_from_file_location(mod_name, path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)  # type: ignore
            sys.modules[mod_name] = mod
        models[name] = mod
    return models.get('user'), models.get('paciente')


@noti_bp.route('/', methods=['GET'])
def listar_notificaciones():
    user_id = request.args.get('user_id') or request.args.get('paciente_id')
    if not user_id:
        return jsonify([{'id': 1, 'title': 'Bienvenido', 'read': False}])
    return jsonify([])


@noti_bp.route('/create', methods=['POST'])
def crear_notificacion():
    data = request.get_json() or {}
    return jsonify({'ok': True, 'notificacion': {'title': data.get('title'), 'body': data.get('body')}})


@noti_bp.route('/mark-read', methods=['POST'])
def marcar_leida():
    data = request.get_json() or {}
    noti_id = data.get('id')
    if not noti_id:
        return jsonify({'ok': False, 'msg': 'id required'}), 400
    return jsonify({'ok': True, 'id': noti_id})
