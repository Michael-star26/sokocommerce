import uuid
from flask import Blueprint, request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity, jwt_required
from database import db
from models import Order, OrderItem, Products, User
from werkzeug.security import generate_password_hash
from decorators import admin_required

orders_bp = Blueprint('orders', __name__)

@orders_bp.route('', methods=['POST'])
def create_order():
    """
    Creates a new order for both logged-in users and guests.
    """
    try:
        current_user_id = None
        try:
            verify_jwt_in_request(optional=True)
            current_user_id = get_jwt_identity()
        except Exception:
            current_user_id = None

        data = request.get_json() or {}
        phone = str(data.get('phone', '')).strip()
        items = data.get('items', [])  # Expected: [{'product_id': 1, 'quantity': 2}]

        if not items:
            return jsonify({'success': False, 'message': 'Cart items are required to place an order.'}), 400

        # Sanitize phone number (Kenya format 254...)
        if phone.startswith('+'):
            phone = phone[1:]
        if phone.startswith('0'):
            phone = '254' + phone[1:]

        # Resolve guest account creation if not authenticated
        if not current_user_id:
            if not phone:
                return jsonify({'success': False, 'message': 'Phone number is required for guest checkout'}), 400

            user = User.query.filter_by(phone=phone).first()
            if not user:
                user = User(
                    username=f"guest_{phone[-4:]}",
                    email=f"guest_{phone}@sokocommerce.local",
                    phone=phone,
                    password_hash=generate_password_hash(uuid.uuid4().hex),
                    is_admin=False,
                    role='GUEST'
                )
                db.session.add(user)
                db.session.flush()
            
            current_user_id = user.id

        # Validate stock availability and calculate total server-side
        calculated_total = 0.0
        order_items_to_create = []

        for item in items:
            p_id = item.get('product_id')
            requested_qty = item.get('quantity', 1)

            if not p_id or not isinstance(requested_qty, int) or requested_qty <= 0:
                continue

            product = Products.query.get(p_id)
            if not product:
                db.session.rollback()
                return jsonify({'success': False, 'message': f'Product ID {p_id} not found'}), 404

            stock = product.stock if product.stock is not None else 0
            if stock < requested_qty:
                db.session.rollback()
                return jsonify({
                    'success': False, 
                    'message': f"Insufficient stock for '{product.name}'. Only {stock} available."
                }), 400

            # Deduct inventory stock securely
            product.stock = stock - requested_qty
            unit_price = float(product.cost) if product.cost else 0.0
            calculated_total += unit_price * requested_qty

            order_items_to_create.append({
                'product_id': product.id,
                'quantity': requested_qty,
                'price': unit_price
            })

        # Generate tracking code (e.g. SKC-8F3A2B)
        tracking_code = f"SKC-{uuid.uuid4().hex[:6].upper()}"

        new_order = Order(
            user_id=current_user_id,
            total_amount=round(calculated_total, 2),
            status='PENDING',
            tracking_number=tracking_code
        )

        db.session.add(new_order)
        db.session.flush()

        # Save order items
        for item_data in order_items_to_create:
            order_item = OrderItem(
                order_id=new_order.id,
                product_id=item_data['product_id'],
                quantity=item_data['quantity'],
                price=item_data['price']
            )
            db.session.add(order_item)

        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Order created successfully',
            'order_id': new_order.id,
            'tracking_number': new_order.tracking_number,
            'total_amount': new_order.total_amount,
            'status': new_order.status
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'An error occurred while creating order', 'error': str(e)}), 500


@orders_bp.route('/track/<identifier>', methods=['GET'])
def track_order(identifier):
    """
    Public endpoint: Tracks order status using Order ID or Tracking Code.
    """
    identifier = identifier.strip()

    if identifier.isdigit():
        order = Order.query.filter((Order.id == int(identifier)) | (Order.tracking_number == identifier)).first()
    else:
        order = Order.query.filter_by(tracking_number=identifier).first()

    if not order:
        return jsonify({'success': False, 'message': 'Order not found'}), 404

    items_summary = []
    if hasattr(order, 'items') and order.items:
        items_summary = [{
            'product_id': item.product_id,
            'quantity': item.quantity,
            'price': float(item.price)
        } for item in order.items]

    return jsonify({
        'success': True,
        'order_id': order.id,
        'status': order.status if order.status else 'PENDING',
        'tracking_number': getattr(order, 'tracking_number', 'N/A'),
        'carrier': getattr(order, 'carrier', 'Standard Delivery'),
        'total_amount': float(order.total_amount) if order.total_amount else 0.0,
        'items': items_summary,
        'created_at': order.created_at.strftime('%Y-%m-%d %H:%M:%S') if hasattr(order, 'created_at') and order.created_at else None
    }), 200


@orders_bp.route('/<int:order_id>/status', methods=['PATCH'])
@jwt_required()
@admin_required
def update_order_status(order_id):
    """
    Admin / Super Admin endpoint to update order status and delivery carrier.
    """
    order = Order.query.get_or_404(order_id)
    data = request.get_json() or {}
    
    new_status = data.get('status')
    carrier = data.get('carrier')

    valid_statuses = ['PENDING', 'PROCESSING', 'SHIPPED', 'DELIVERED', 'CANCELLED']
    if new_status:
        if new_status.upper() not in valid_statuses:
            return jsonify({'success': False, 'message': f'Invalid status. Allowed values: {valid_statuses}'}), 400
        order.status = new_status.upper()

    if carrier and hasattr(order, 'carrier'):
        order.carrier = carrier

    db.session.commit()

    return jsonify({
        'success': True,
        'message': f'Order #{order.id} status updated to {order.status}',
        'order_id': order.id,
        'status': order.status,
        'carrier': getattr(order, 'carrier', 'N/A')
    }), 200