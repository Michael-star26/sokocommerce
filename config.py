# import os
# from dotenv import load_dotenv

# Load variables from .env into os.environ
# load_dotenv()

# class Config:
#     SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')
#     JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-dev-secret-key')
#     SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///sokocommerce.db')
#     SQLALCHEMY_TRACK_MODIFICATIONS = False

    # M-Pesa / Daraja Configurations
    # DARAJA_CONSUMER_KEY = os.environ.get('DARAJA_CONSUMER_KEY')
    # DARAJA_CONSUMER_SECRET = os.environ.get('DARAJA_CONSUMER_SECRET')
    # DARAJA_PASSKEY = os.environ.get('DARAJA_PASSKEY')
    # DARAJA_BUSINESS_SHORT_CODE = os.environ.get('DARAJA_BUSINESS_SHORT_CODE', '174379')
    # DARAJA_CALLBACK_URL = os.environ.get('DARAJA_CALLBACK_URL')


# prod
import os
from dotenv import load_dotenv

# Load variables from .env into os.environ
load_dotenv()

class Config:
    # Flask & Security Settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-dev-secret-key')
    
    # Environment Mode
    ENV = os.environ.get('FLASK_ENV', 'development')
    DEBUG = os.environ.get('FLASK_DEBUG', 'True').lower() in ['true', '1']

    # Database Configuration & SQLAlchemy Fix for Render/Railway
    db_url = os.environ.get('DATABASE_URL', 'sqlite:///sokocommerce.db')
    if db_url and db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    
    SQLALCHEMY_DATABASE_URI = db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # M-Pesa / Daraja Configurations
    DARAJA_CONSUMER_KEY = os.environ.get('DARAJA_CONSUMER_KEY')
    DARAJA_CONSUMER_SECRET = os.environ.get('DARAJA_CONSUMER_SECRET')
    DARAJA_PASSKEY = os.environ.get('DARAJA_PASSKEY')
    DARAJA_BUSINESS_SHORT_CODE = os.environ.get('DARAJA_BUSINESS_SHORT_CODE', '174379')
    DARAJA_CALLBACK_URL = os.environ.get('DARAJA_CALLBACK_URL')

    # Daraja Environment Endpoints
    IS_PRODUCTION = os.environ.get('DARAJA_ENV', 'sandbox').lower() == 'production'
    DARAJA_BASE_URL = (
        'https://api.safaricom.co.ke' if IS_PRODUCTION 
        else 'https://sandbox.safaricom.co.ke'
    )

    @classmethod
    def validate_production_secrets(cls):
        """Ensures essential production secrets are set prior to spinning up live."""
        if cls.ENV == 'production':
            missing = []
            if cls.SECRET_KEY == 'dev-secret-key':
                missing.append('SECRET_KEY')
            if cls.JWT_SECRET_KEY == 'jwt-dev-secret-key':
                missing.append('JWT_SECRET_KEY')
            if not cls.DARAJA_CONSUMER_KEY:
                missing.append('DARAJA_CONSUMER_KEY')
            if not cls.DARAJA_CONSUMER_SECRET:
                missing.append('DARAJA_CONSUMER_SECRET')
            if not cls.DARAJA_CALLBACK_URL:
                missing.append('DARAJA_CALLBACK_URL')
                
            if missing:
                raise ValueError(f"CRITICAL: Missing environment variables in production: {', '.join(missing)}")