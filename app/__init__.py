from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager


db=SQLAlchemy()
login_manager=LoginManager()
login_manager.login_view = 'auth.login'

def create_app():
    app=Flask(__name__)

    app.config.from_object('config.Config')

    db.init_app(app)
    login_manager.init_app(app)

    from app.models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from .routes.auth import auth
    from .routes.main import main
    from .routes.dashboard import dashboard

    app.register_blueprint(auth)
    app.register_blueprint(main)
    app.register_blueprint(dashboard)

    return app