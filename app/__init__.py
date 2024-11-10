# app/__init__.py

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
from .routes import main_routes, feedback_routes, upload_routes

# Initialize the database
db = SQLAlchemy()


def create_app():
    # Initialize Flask app
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)

    # Register blueprints
    app.register_blueprint(main_routes.bp)
    app.register_blueprint(feedback_routes.bp)
    app.register_blueprint(upload_routes.bp)

    # Create tables if they don't exist
    with app.app_context():
        db.create_all()

    return app
