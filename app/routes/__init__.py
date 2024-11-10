# app/routes/__init__.py

from flask import Blueprint

# Initialize blueprints for different routes
bp = Blueprint('main', __name__)

# Import individual route modules
from . import main_routes, feedback_routes, upload_routes  # noqa: F401
