from flask import Blueprint, request, jsonify
from database import db
from models import User, Products, Order, Payment
from flask_jwt_extended import jwt_required
from decorators import admin_required

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

# ----------------------------------------------------
# 1. INVENTORY MANAGEMENT
# ----------------------------------------------------

@admin_bp.route('/inventory', methods=['GET'])
@jwt_required()
@admin_required
def get_inventory():
    products = Products.query.order_by(Products.id.desc()).all()
    
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'price': float(p.cost),
        'stock': p.stock,
        'category': p.category,
        'is_low_stock': p.stock < 10
    } for p in products]), 200


@admin_bp.route('/inventory/<int:product_id>/stock', methods=['PATCH'])
@jwt_required()
@admin_required
def update_stock(product_id):
    data = request.get_json() or {}
    new_stock = data.get('stock')

    if new_stock is None or not isinstance(new_stock, int) or new_stock < 0:
        return jsonify({'message': 'Please provide a valid non-negative integer for stock.'}), 400

    product = Products.query.get_or_404(product_id)
    product.stock = new_stock
    db.session.commit()

    return jsonify({
        'message': f"Stock for '{product.name}' updated successfully.",
        'product': product.to_dict()
    }), 200


# ----------------------------------------------------
# 2. ORDER TRACKING
# ----------------------------------------------------

@admin_bp.route('/orders', methods=['GET'])
@jwt_required()
@admin_required
def get_all_orders():
    # Joined load to pull User details in a single query
    orders = db.session.query(Order, User)\
        .outerjoin(User, Order.user_id == User.id)\
        .order_by(Order.id.desc())\
        .all()
    
    response_data = []
    for order, user in orders:
        response_data.append({
            'id': order.id,
            'user_id': order.user_id,
            'customer_username': user.username if user else 'Guest/Unknown',
            'customer_phone': getattr(user, 'phone', 'N/A') if user else 'N/A',
            'status': order.status if order.status else 'PENDING',
            'total_amount': float(order.total_amount) if order.total_amount else 0.0,
            'tracking_number': getattr(order, 'tracking_number', 'N/A'),
            'carrier': getattr(order, 'carrier', 'Standard Delivery'),
            'created_at': order.created_at.isoformat() if hasattr(order, 'created_at') and order.created_at else None,
            'items_count': len(order.items) if hasattr(order, 'items') and order.items else 0
        })

    return jsonify(response_data), 200


@admin_bp.route('/orders/<int:order_id>/status', methods=['PATCH'])
@jwt_required()
@admin_required
def update_order_status(order_id):
    data = request.get_json() or {}
    new_status = data.get('status')
    carrier = data.get('carrier')
    tracking_number = data.get('tracking_number')

    valid_statuses = ['PENDING', 'PROCESSING', 'SHIPPED', 'DELIVERED', 'CANCELLED']
    if not new_status or new_status.upper() not in valid_statuses:
        return jsonify({'message': f'Invalid status. Allowed statuses: {valid_statuses}'}), 400

    order = Order.query.get_or_404(order_id)
    order.status = new_status.upper()

    if carrier and hasattr(order, 'carrier'):
        order.carrier = carrier
    if tracking_number and hasattr(order, 'tracking_number'):
        order.tracking_number = tracking_number

    db.session.commit()

    return jsonify({
        'message': f'Order #{order.id} status updated to {order.status}',
        'order_id': order.id,
        'status': order.status,
        'carrier': getattr(order, 'carrier', 'N/A'),
        'tracking_number': getattr(order, 'tracking_number', 'N/A')
    }), 200


# ----------------------------------------------------
# 3. PAYMENT AUDITING
# ----------------------------------------------------

@admin_bp.route('/payments', methods=['GET'])
@jwt_required()
@admin_required
def get_all_payments():
    payments = Payment.query.order_by(Payment.id.desc()).all()
    
    return jsonify([{
        'id': pay.id,
        'user_id': pay.user_id,
        'order_id': getattr(pay, 'order_id', None),
        'amount': float(pay.amount) if pay.amount else 0.0,
        'phone_number': pay.phone_number,
        'status': pay.status if pay.status else 'PENDING',
        'mpesa_receipt': getattr(pay, 'mpesa_receipt', 'N/A'),
        'created_at': pay.created_at.isoformat() if hasattr(pay, 'created_at') and pay.created_at else None
    } for pay in payments]), 200