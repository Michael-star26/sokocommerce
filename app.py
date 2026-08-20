from flask import Flask
from config import Config
from database import db
from routes.products import product_bp
from flask_cors import CORS

def create_app():
    app=Flask(__name__)
    app.config.from_object(Config)
    CORS(app)
    
    db.init_app(app)

    app.register_blueprint(product_bp)

    with app.app_context():
        db.create_all()
    return app

if __name__=='__main__':
    app=create_app()
    app.run(debug=True)