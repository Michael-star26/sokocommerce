import os
import click
from flask import Flask, jsonify, request, make_response
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate

from config import Config
from database import db
from models import User

from routes.products import product_bp
from routes.auth import auth_bp
from routes.payments import payment_bp
from routes.orders import orders_bp
from routes.admin import admin_bp
from routes.cart import cart_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Validate production configuration if method exists
    if hasattr(Config, 'validate_production_secrets'):
        Config.validate_production_secrets()

    # Dynamic CORS Configuration
    raw_origins = [
        "http://localhost:4200",
        "http://127.0.0.1:4200",
        "https://sokofrontend.vercel.app",
        "https://sokofrontend.vercel.app/products"
        "https://sokofrontend-git-main-michaels-projects-a233fb43.vercel.app",
        "https://sokofrontend-git-main-michaels-projects-a233fb43.vercel.app/products",
        os.environ.get("FRONTEND_URL")
    ]
    
    # Clean origins: strip whitespace, remove trailing slashes, filter empties
    allowed_origins = [
        origin.strip().rstrip('/') 
        for origin in raw_origins 
        if origin and origin.strip()
    ]

    CORS(
        app,
        resources={r"/api/*": {"origins": allowed_origins}},
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        supports_credentials=True
    )

    # Global handler to guarantee HTTP 200 responses on OPTIONS preflight
    @app.before_request
    def handle_preflight():
        if request.method == "OPTIONS":
            response = make_response()
            origin = request.headers.get("Origin")
            if origin in allowed_origins:
                response.headers.add("Access-Control-Allow-Origin", origin)
                response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization")
                response.headers.add("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, PATCH, OPTIONS")
                response.headers.add("Access-Control-Allow-Credentials", "true")
            return response, 200

    # Initialize extensions
    db.init_app(app)
    migrate = Migrate(app, db)
    jwt = JWTManager(app)

    # Register Blueprints with consistent API prefixes
    app.register_blueprint(product_bp, url_prefix='/api/products')
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(payment_bp, url_prefix='/api/payments')
    app.register_blueprint(orders_bp, url_prefix='/api/orders')
    app.register_blueprint(cart_bp, url_prefix='/api/cart')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')

    # JWT User Lookup Helper
    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        return User.query.get(identity)

    # JWT Error Responses
    @jwt.invalid_token_loader
    def invalid_token_callback(error_string):
        return jsonify({'success': False, 'message': f'Signature verification failed: {error_string}'}), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error_string):
        return jsonify({'success': False, 'message': f'Request does not contain an access token: {error_string}'}), 401

    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({'success': False, 'message': 'The token has expired'}), 401

    # Global HTTP Error Handlers
    @app.errorhandler(404)
    def handle_not_found(e):
        return jsonify({'success': False, 'message': 'The requested endpoint or resource was not found'}), 404

    @app.errorhandler(500)
    def handle_server_error(e):
        return jsonify({'success': False, 'message': 'An internal server error occurred'}), 500

    # CLI Management Commands
    @app.cli.command("make-admin")
    def make_admin():
        email = click.prompt("Enter user email to make ADMIN", type=str).strip().lower()
        user = User.query.filter_by(email=email).first()
        
        if user:
            user.is_admin = True
            if hasattr(User, 'role'):
                user.role = 'ADMIN'
            db.session.commit()
            click.echo(f"Successfully granted ADMIN privileges to {user.email}")
        else:
            click.echo(f"User with email '{email}' not found.")

    @app.cli.command("make-super-admin")
    def make_super_admin():
        email = click.prompt("Enter user email to make SUPER ADMIN", type=str).strip().lower()
        user = User.query.filter_by(email=email).first()
        
        if user:
            user.is_admin = True
            if hasattr(User, 'role'):
                user.role = 'SUPER_ADMIN'
            db.session.commit()
            click.echo(f"Successfully granted SUPER_ADMIN privileges to {user.email}")
        else:
            click.echo(f"User with email '{email}' not found.")

    with app.app_context():
        db.create_all()
    return app


app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(
        host='0.0.0.0',
        port=port,
        debug=app.config.get('DEBUG', False)
    )