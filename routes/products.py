from flask import Blueprint, request, jsonify
from database import db
from models import Products as Product
from flask_jwt_extended import jwt_required
from decorators import admin_required

product_bp = Blueprint('products', __name__)

@product_bp.route('', methods=['GET'])
def get_products():
    """
    Fetches catalog products with optional search, category, and stock filtering.
    """
    search_query = request.args.get('search', '').strip()
    category = request.args.get('category', '').strip()
    in_stock_only = request.args.get('in_stock', '').lower() == 'true'

    query = Product.query

    if search_query:
        query = query.filter(Product.name.ilike(f'%{search_query}%'))

    if category:
        query = query.filter(Product.category.ilike(category))

    if in_stock_only:
        query = query.filter(Product.stock > 0)

    products = query.order_by(Product.id.desc()).all()
    
    # Safe serialization fallback if to_dict() isn't implemented on model
    return jsonify([
        p.to_dict() if hasattr(p, 'to_dict') else {
            'id': p.id,
            'name': p.name,
            'description': getattr(p, 'description', ''),
            'cost': float(p.cost) if p.cost else 0.0,
            'category': getattr(p, 'category', 'Uncategorized'),
            'image_url': getattr(p, 'image_url', ''),
            'stock': getattr(p, 'stock', 0)
        } for p in products
    ]), 200


@product_bp.route('/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """
    Fetches details for a single product.
    """
    product = Product.query.get_or_404(product_id)
    if hasattr(product, 'to_dict'):
        return jsonify(product.to_dict()), 200

    return jsonify({
        'id': product.id,
        'name': product.name,
        'description': getattr(product, 'description', ''),
        'cost': float(product.cost) if product.cost else 0.0,
        'category': getattr(product, 'category', 'Uncategorized'),
        'image_url': getattr(product, 'image_url', ''),
        'stock': getattr(product, 'stock', 0)
    }), 200


@product_bp.route('', methods=['POST'])
@jwt_required()
@admin_required
def add_product():
    """
    Admin endpoint: Adds a new product to inventory.
    """
    data = request.get_json() or {}
    name = str(data.get('name', '')).strip()
    cost = data.get('cost')

    if not name or cost is None:
        return jsonify({'message': 'Product name and cost are required'}), 400

    try:
        parsed_cost = float(cost)
        parsed_stock = int(data.get('stock', 0))
        if parsed_cost < 0 or parsed_stock < 0:
            return jsonify({'message': 'Cost and stock must be non-negative numbers'}), 400
    except (ValueError, TypeError):
        return jsonify({'message': 'Invalid numeric value for cost or stock'}), 400

    new_product = Product(
        name=name,
        description=data.get('description', ''),
        cost=parsed_cost,
        category=data.get('category', 'General'),
        image_url=data.get('image_url', ''),
        stock=parsed_stock
    )

    db.session.add(new_product)
    db.session.commit()

    res_dict = new_product.to_dict() if hasattr(new_product, 'to_dict') else {'id': new_product.id, 'name': new_product.name}
    return jsonify(res_dict), 201


@product_bp.route('/<int:product_id>', methods=['PUT', 'PATCH'])
@jwt_required()
@admin_required
def update_product(product_id):
    """
    Admin endpoint: Updates product details.
    """
    product = Product.query.get_or_404(product_id)
    data = request.get_json() or {}

    if 'name' in data:
        product.name = str(data['name']).strip()
    if 'description' in data:
        product.description = data['description']
    if 'category' in data:
        product.category = data['category']
    if 'image_url' in data:
        product.image_url = data['image_url']
        
    if 'cost' in data:
        try:
            val = float(data['cost'])
            if val < 0:
                return jsonify({'message': 'Cost cannot be negative'}), 400
            product.cost = val
        except (ValueError, TypeError):
            return jsonify({'message': 'Invalid cost value'}), 400

    if 'stock' in data:
        try:
            val = int(data['stock'])
            if val < 0:
                return jsonify({'message': 'Stock cannot be negative'}), 400
            product.stock = val
        except (ValueError, TypeError):
            return jsonify({'message': 'Invalid stock value'}), 400

    db.session.commit()

    res_dict = product.to_dict() if hasattr(product, 'to_dict') else {'id': product.id, 'name': product.name}
    return jsonify(res_dict), 200


@product_bp.route('/<int:product_id>', methods=['DELETE'])
@jwt_required()
@admin_required
def delete_product(product_id):
    """
    Admin endpoint: Removes a product from the database.
    """
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()

    return jsonify({'message': f"Product '{product.name}' deleted successfully"}), 200