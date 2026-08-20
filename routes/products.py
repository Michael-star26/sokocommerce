from flask import Blueprint, request,jsonify
from models import Products
from database import db

product_bp=Blueprint('products',__name__,url_prefix="/api/products")
@product_bp.route('/',methods=['GET'])
def get_products():
    category=request.args.get('category')
    if category:
        products=Products.query.filter_by(category=category).all()
    else:
        products=Products.query.all()
    return jsonify([p.to_dict for p in products]),200

@product_bp.route('/<int:product_id>', methods=['GET'])
def get_single_product(product_id):
    Product=Products.query.get_or_404(product_id)
    return jsonify(Product.to_dict()), 200

@product_bp.route('', methods=['POST'], strict_slashes=False)
def create_product():
    data = request.get_json()
    
    new_product = Products(
        name=data['name'],
        description=data.get('description', ''),
        cost=data['cost'],
        category=data['category'],
        image_url=data.get('image_url', '')
    )
    
    db.session.add(new_product)
    db.session.commit() 
    
    return jsonify(new_product.to_dict()), 201