from flask_sqlalchemy import SQLAlchemy

# Initialize the SQLAlchemy database instance
db = SQLAlchemy()


def init_db(app):
    """
    Binds the SQLAlchemy database instance to the Flask application.
    """
    db.init_app(app)
    with app.app_context():
        # Creates database tables for models imported in app context
        db.create_all()