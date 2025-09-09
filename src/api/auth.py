"""Authentication API endpoints."""

import jwt
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import generate_password_hash
from models import db, User
from config import Config

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

def generate_token(user_id: int) -> str:
    """Generate JWT token for user."""
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(days=7)  # Token expires in 7 days
    }
    return jwt.encode(payload, Config.JWT_SECRET, algorithm='HS256')

def verify_token(token: str) -> dict:
    """Verify JWT token and return payload."""
    try:
        payload = jwt.decode(token, Config.JWT_SECRET, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token")

@auth_bp.route('/signup', methods=['POST'])
def signup():
    """User registration endpoint."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        # Validate input
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        if len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters long'}), 400
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({'error': 'User with this email already exists'}), 409
        
        # Create new user
        user = User(email=email)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        # Generate token
        token = generate_token(user.id)
        
        return jsonify({
            'message': 'User created successfully',
            'token': token,
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create user', 'detail': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """User login endpoint."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        # Validate input
        if not email or not password:
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Find user
        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Generate token
        token = generate_token(user.id)
        
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Login failed', 'detail': str(e)}), 500

@auth_bp.route('/request-password-reset', methods=['POST'])
def request_password_reset():
    """Request password reset endpoint (stub implementation)."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        email = data.get('email', '').strip().lower()
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        # Check if user exists
        user = User.query.filter_by(email=email).first()
        if not user:
            # Don't reveal if user exists or not for security
            return jsonify({'message': 'If the email exists, a password reset link has been sent'}), 200
        
        # TODO: In a real implementation, you would:
        # 1. Generate a secure reset token
        # 2. Store it in the database with expiration
        # 3. Send an email with the reset link
        
        return jsonify({'message': 'If the email exists, a password reset link has been sent'}), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to process password reset request', 'detail': str(e)}), 500

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """Reset password endpoint (stub implementation)."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        token = data.get('token', '')
        new_password = data.get('password', '')
        
        if not token or not new_password:
            return jsonify({'error': 'Token and new password are required'}), 400
        
        if len(new_password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters long'}), 400
        
        # TODO: In a real implementation, you would:
        # 1. Verify the reset token
        # 2. Check if it's not expired
        # 3. Update the user's password
        # 4. Invalidate the reset token
        
        return jsonify({'message': 'Password reset functionality not implemented yet'}), 501
        
    except Exception as e:
        return jsonify({'error': 'Failed to reset password', 'detail': str(e)}), 500

def require_auth(f):
    """Decorator to require authentication for protected routes."""
    from functools import wraps
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({'error': 'Authorization header is required'}), 401
        
        try:
            # Extract token from "Bearer <token>" format
            token = auth_header.split(' ')[1] if auth_header.startswith('Bearer ') else auth_header
            payload = verify_token(token)
            user_id = payload['user_id']
            
            # Add user_id to request context
            request.user_id = user_id
            
        except ValueError as e:
            return jsonify({'error': str(e)}), 401
        except Exception as e:
            return jsonify({'error': 'Invalid token'}), 401
        
        return f(*args, **kwargs)
    
    return decorated_function
