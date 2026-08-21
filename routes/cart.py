from flask import Blueprint, request, jsonify
from database import db
from models import Products

cart_bp = Blueprint('cart', __name__, url_prefix='/api/cart')


@cart_bp.route('/validate', methods=['POST'])
def validate_cart():
    """
    Validates cart items sent from the client (guest or logged-in).
    Batch-fetches products to check stock availability, current pricing, and calculates subtotal.
    Expected Payload: { "items": [{ "product_id": 1, "quantity": 2 }] }
    """
    try:
        data = request.get_json() or {}
        cart_items = data.get('items', [])

        if not cart_items:
            return jsonify({
                'success': True,
                'items': [],
                'subtotal': 0.0,
                'item_count': 0
            }), 200

        # Map requested quantities by product_id
        requested_qty_map = {}
        for item in cart_items:
            p_id = item.get('product_id')
            qty = item.get('quantity', 1)
            if p_id and isinstance(qty, int) and qty > 0:
                requested_qty_map[p_id] = qty

        if not requested_qty_map:
            return jsonify({
                'success': True,
                'items': [],
                'subtotal': 0.0,
                'item_count': 0
            }), 200

        # Batch query all requested products in a single database roundtrip
        products = Products.query.filter(Products.id.in_(requested_qty_map.keys())).all()

        validated_items = []
        subtotal = 0.0
        total_quantity = 0

        for product in products:
            requested_qty = requested_qty_map.get(product.id, 1)
            stock = product.stock if product.stock is not None else 0
            
            # Allocate quantity based on available stock
            allocated_qty = min(requested_qty, stock) if stock > 0 else 0
            is_in_stock = stock >= requested_qty

            unit_cost = float(product.cost) if product.cost else 0.0
            item_total = unit_cost * allocated_qty

            validated_items.append({
                'product_id': product.id,
                'name': product.name,
                'unit_cost': unit_cost,
                'requested_quantity': requested_qty,
                'allocated_quantity': allocated_qty,
                'available_stock': stock,
                'in_stock': is_in_stock,
                'image_url': product.image_url or 'assets/placeholder.png',
                'item_total': round(item_total, 2)
            })

            subtotal += item_total
            total_quantity += allocated_qty

        return jsonify({
            'success': True,
            'items': validated_items,
            'subtotal': round(subtotal, 2),
            'item_count': total_quantity
        }), 200

    except Exception as e:
        return jsonify({
            'success': False, 
            'message': 'Failed to validate cart items.',
            'error': str(e)
        }), 500


@cart_bp.route('/check-item/<int:product_id>', methods=['GET'])
def check_item_availability(product_id):
    """
    Checks real-time stock and price for a single product.
    """
    product = Products.query.get_or_404(product_id)
    stock = product.stock if product.stock is not None else 0

    return jsonify({
        'success': True,
        'product_id': product.id,
        'name': product.name,
        'cost': float(product.cost) if product.cost else 0.0,
        'stock': stock,
        'in_stock': stock > 0
    }), 200