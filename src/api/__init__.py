"""API blueprints initialization."""

from flask import Blueprint
from api.auth import auth_bp
from api.resumes import resumes_bp
from api.jobs import jobs_bp
from api.match import match_bp
from api.admin import admin_bp

# Create main API blueprint
api_bp = Blueprint('api', __name__, url_prefix='/api')

# Register sub-blueprints
api_bp.register_blueprint(auth_bp)
api_bp.register_blueprint(resumes_bp)
api_bp.register_blueprint(jobs_bp)
api_bp.register_blueprint(match_bp)
api_bp.register_blueprint(admin_bp)
