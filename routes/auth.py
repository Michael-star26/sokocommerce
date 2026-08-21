from functools import wraps
from flask import Blueprint, request, jsonify
from database import db
from models import User
from decorators import admin_required
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import (
    create_access_token, 
    get_jwt_identity, 
    verify_jwt_in_request, 
    get_jwt, 
    jwt_required
)

auth_bp = Blueprint('auth', __name__)

# ----------------------------------------------------
# DECORATORS
# ----------------------------------------------------

def super_admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt()
        if claims.get('role') != 'SUPER_ADMIN' and not claims.get('is_super_admin'):
            return jsonify({'message': 'Super Admin privileges required'}), 403
        return f(*args, **kwargs)
    return decorated


# ----------------------------------------------------
# AUTHENTICATION ENDPOINTS
# ----------------------------------------------------

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    username = str(data.get('username', '')).strip()
    email = str(data.get('email', '')).strip().lower()
    phone = str(data.get('phone', '')).strip()
    password = str(data.get('password', ''))

    if not username or not email or not phone or not password:
        return jsonify({'message': 'Username, email, phone, and password are required'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'message': 'User with this email already exists'}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({'message': 'Username is already taken'}), 400

    hashed_pw = generate_password_hash(password)
    
    # First user automatically gets SUPER_ADMIN privileges
    is_first_user = User.query.count() == 0
    role = 'SUPER_ADMIN' if is_first_user else 'USER'
    is_admin = is_first_user

    new_user = User(
        username=username,
        email=email,
        phone=phone,
        password_hash=hashed_pw,
        is_admin=is_admin,
        role=role
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        'message': 'User created successfully',
        'role': role
    }), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    email = str(data.get('email', '')).strip().lower()
    password = str(data.get('password', ''))

    if not email or not password:
        return jsonify({'message': 'Email and password are required'}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({'message': 'Invalid credentials'}), 401

    user_role = getattr(user, 'role', None) or ('ADMIN' if user.is_admin else 'USER')
    is_super_admin = (user_role == 'SUPER_ADMIN')
    is_admin_flag = bool(user.is_admin or user_role in ['ADMIN', 'SUPER_ADMIN'])

    additional_claims = {
        'is_admin': is_admin_flag,
        'is_super_admin': is_super_admin,
        'role': user_role
    }

    access_token = create_access_token(
        identity=str(user.id),
        additional_claims=additional_claims
    )

    return jsonify({
        'token': access_token,
        'access_token': access_token,
        'is_admin': is_admin_flag,
        'role': user_role,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'phone': user.phone,
            'role': user_role,
            'is_admin': is_admin_flag
        }
    }), 200


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    current_user_id = get_jwt_identity()
    user = User.query.get_or_404(int(current_user_id))
    
    user_role = getattr(user, 'role', None) or ('ADMIN' if user.is_admin else 'USER')
    is_admin_flag = bool(user.is_admin or user_role in ['ADMIN', 'SUPER_ADMIN'])

    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'phone': user.phone,
        'role': user_role,
        'is_admin': is_admin_flag
    }), 200


# ----------------------------------------------------
# USER & ROLE MANAGEMENT
# ----------------------------------------------------

@auth_bp.route('/users', methods=['GET'])
@jwt_required()
@admin_required
def get_users():
    users = User.query.order_by(User.id.asc()).all()
    return jsonify([{
        'id': u.id,
        'username': u.username,
        'email': u.email,
        'phone': u.phone,
        'is_admin': u.is_admin,
        'role': getattr(u, 'role', None) or ('ADMIN' if u.is_admin else 'USER')
    } for u in users]), 200


@auth_bp.route('/users/<int:user_id>/toggle-admin', methods=['PATCH'])
@jwt_required()
@admin_required
def toggle_admin(user_id):
    current_user_id = get_jwt_identity()
    if str(user_id) == str(current_user_id):
        return jsonify({'message': 'You cannot change your own admin status'}), 400

    user = User.query.get_or_404(user_id)
    
    # Prevent demoting SUPER_ADMIN via toggle
    if getattr(user, 'role', None) == 'SUPER_ADMIN':
        return jsonify({'message': 'Cannot modify status of a SUPER_ADMIN'}), 403

    user.is_admin = not user.is_admin
    user.role = 'ADMIN' if user.is_admin else 'USER'

    db.session.commit()
    return jsonify({
        'message': f"Updated {user.username}'s admin status",
        'is_admin': user.is_admin,
        'role': user.role
    }), 200


@auth_bp.route('/users/<int:user_id>/promote-super-admin', methods=['PATCH'])
@jwt_required()
@super_admin_required
def promote_super_admin(user_id):
    user = User.query.get_or_404(user_id)
    user.is_admin = True
    user.role = 'SUPER_ADMIN'

    db.session.commit()
    return jsonify({
        'message': f"Promoted {user.username} to SUPER_ADMIN",
        'is_admin': True,
        'role': 'SUPER_ADMIN'
    }), 200