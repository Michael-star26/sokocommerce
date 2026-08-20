import os

class Config:
    Secret_Key=os.getenv('SECRET_KEY','default_dev_key')
    SQLALCHEMY_DATABASE_URI=os.getenv('DATABASE_URL','sqlite:///app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS=False