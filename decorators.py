from functools import wraps
from flask import jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt, current_user


def admin_required(f):
    """
    Decorator to restrict route access to users with ADMIN or SUPER_ADMIN privileges.
    Checks JWT token claims first, falling back to database model attributes if necessary.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt()

        # 1. Check direct claims inside JWT
        is_admin_claim = claims.get('is_admin', False)
        role_claim = claims.get('role', '').upper()

        if is_admin_claim or role_claim in ['ADMIN', 'SUPER_ADMIN']:
            return f(*args, **kwargs)

        # 2. Fallback check via database model if user_lookup_loader is used
        if current_user:
            is_db_admin = getattr(current_user, 'is_admin', False)
            db_role = str(getattr(current_user, 'role', '')).upper()
            if is_db_admin or db_role in ['ADMIN', 'SUPER_ADMIN']:
                return f(*args, **kwargs)

        return jsonify({'success': False, 'message': 'Admin privileges required'}), 403

    return decorated


def super_admin_required(f):
    """
    Decorator to restrict route access strictly to SUPER_ADMIN accounts.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt()

        # 1. Check direct claims inside JWT
        is_super_admin_claim = claims.get('is_super_admin', False)
        role_claim = claims.get('role', '').upper()

        if is_super_admin_claim or role_claim == 'SUPER_ADMIN':
            return f(*args, **kwargs)

        # 2. Fallback check via database model if user_lookup_loader is used
        if current_user:
            db_role = str(getattr(current_user, 'role', '')).upper()
            if db_role == 'SUPER_ADMIN':
                return f(*args, **kwargs)

        return jsonify({'success': False, 'message': 'Super Admin privileges required'}), 403

    return decorated