# app/__init__.py

from flask import Flask
from config import Config
from .models import db
from .routes import main_routes, feedback_routes, upload_routes


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    app.register_blueprint(main_routes.bp)
    app.register_blueprint(feedback_routes.bp)
    app.register_blueprint(upload_routes.bp)

    with app.app_context():
        db.create_all()

    return app
