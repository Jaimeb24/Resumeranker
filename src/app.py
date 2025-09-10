"""Flask application factory and main entry point."""

import os
from flask import Flask, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room
from config import config
from db import init_db
from api import api_bp
from models import db

def create_app(config_name=None):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Load configuration
    config_name = config_name or os.getenv('FLASK_ENV', 'default')
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    
    # Initialize extensions
    CORS(app, origins=app.config['CORS_ORIGINS'])
    
    # Initialize database
    init_db(app)git 
    
    # Register blueprints
    app.register_blueprint(api_bp)
    
    # Initialize SocketIO
    socketio = SocketIO(app, cors_allowed_origins=app.config['CORS_ORIGINS'], async_mode='threading')
    app.extensions['socketio'] = socketio
    
    # SocketIO event handlers
    @socketio.on('connect')
    def handle_connect(auth=None):
        """Handle client connection."""
        print(f"Client connected: {request.sid}")
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnection."""
        print(f"Client disconnected: {request.sid}")
    
    @socketio.on('join_user_room')
    def handle_join_user_room(data):
        """Handle user joining their personal room for updates."""
        user_id = data.get('user_id')
        if user_id:
            room = f'user_{user_id}'
            join_room(room)
            print(f"User {user_id} joined room {room}")
    
    @socketio.on('leave_user_room')
    def handle_leave_user_room(data):
        """Handle user leaving their personal room."""
        user_id = data.get('user_id')
        if user_id:
            room = f'user_{user_id}'
            leave_room(room)
            print(f"User {user_id} left room {room}")
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        """Handle 404 errors."""
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors."""
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500
    
    @app.errorhandler(413)
    def too_large(error):
        """Handle file too large errors."""
        return jsonify({'error': 'File too large'}), 413
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        """Health check endpoint."""
        return jsonify({'status': 'healthy', 'message': 'ResumeRanker API is running'}), 200
    
    # Root endpoint
    @app.route('/')
    def root():
        """Root endpoint."""
        return jsonify({
            'message': 'ResumeRanker API',
            'version': '1.0.0',
            'endpoints': {
                'health': '/health',
                'api': '/api',
                'auth': '/api/auth',
                'resumes': '/api/resumes',
                'jobs': '/api/jobs',
                'match': '/api/match'
            }
        }), 200
    
    return app, socketio

def run_app():
    """Run the Flask application."""
    app, socketio = create_app()
    
    # Create uploads directory
    uploads_dir = os.path.join(app.root_path, '..', 'uploads')
    os.makedirs(uploads_dir, exist_ok=True)
    
    print("Starting ResumeRanker API server...")
    print(f"Database: {app.config['DATABASE_URL']}")
    print(f"CORS Origins: {app.config['CORS_ORIGINS']}")
    
    # Run with SocketIO
    socketio.run(app, host='0.0.0.0', port=3001, debug=app.config.get('DEBUG', False))

if __name__ == '__main__':
    run_app()
