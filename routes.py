from flask import Blueprint, request, jsonify, Response
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from models import db, Usuario

api_bp = Blueprint('api', __name__)

@api_bp.route('/usuarios/registrar', methods=['POST'])
def registrar_usuario() -> tuple[Response, int]:
    try:
        payload = request.get_json()

        clave_segura = generate_password_hash(payload['password'])

        nuevo_user = Usuario(
            username=payload['username'],
            password=clave_segura, 
            rol=payload.get('rol', 'Operario')
        )

        db.session.add(nuevo_user)
        db.session.commit()

        return jsonify({"mensaje": "Éxito", "data": nuevo_user.serializar()}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Fallo de integridad", "detalle": str(e)}), 400

@api_bp.route('/usuarios', methods=['GET'])
def listar_usuarios() -> tuple[Response, int]:
    pagina = request.args.get('page', 1, type=int)
    paginacion = Usuario.query.paginate(page=pagina, per_page=10, error_out=False)
    resultado = [u.serializar() for u in paginacion.items]

    return jsonify({
        "pagina_actual": paginacion.page,
        "total_paginas": paginacion.pages,
        "usuarios": resultado
    }), 200

@api_bp.route('/login', methods=['POST'])
def login() -> tuple[Response, int]:
    payload = request.get_json()

    usuario = Usuario.query.filter_by(username=payload.get('username')).first()

    if usuario and check_password_hash(usuario.password, payload.get('password')):

        token_acceso = create_access_token(
            identity=usuario.username,
            additional_claims={"rol": usuario.rol}
        )

        return jsonify({"mensaje": "Login exitoso", "token": token_acceso}), 200

    return jsonify({"error": "Credenciales inválidas"}), 401

@api_bp.route('/inventario/critico', methods=['POST'])
@jwt_required()
def modificar_inventario() -> tuple[Response, int]:

    usuario_actual = get_jwt_identity()
    claims = get_jwt()
    rol = claims.get("rol")

    if rol != "Admin":
        return jsonify({"error": "Forbidden: Requiere privilegios de Administrador"}), 403

    return jsonify({
        "mensaje": "Acceso concedido al servidor.",
        "operador": usuario_actual
    }), 200

@api_bp.route('/inventario', methods=['POST'])
@jwt_required()
def insertar_inventario() -> tuple[Response, int]:
    
    datos = request.get_json()

    return jsonify({
        "mensaje": "Producto insertado correctamente",
        "producto": datos
    }), 201    

   