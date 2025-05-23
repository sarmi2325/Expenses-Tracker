import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-fallback-key')  
    SQLALCHEMY_DATABASE_URI='sqlite:///expense_tracker.db'
    SQLALCHEMY_TRACK_MODIFICATIONS=False

    