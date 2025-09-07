"""Resume management API endpoints."""

import os
import uuid
from werkzeug.utils import secure_filename
from flask import Blueprint, request, jsonify, current_app
from models import db, Resume, User
from services.extract import extract_text_from_file
from api.auth import require_auth

resumes_bp = Blueprint('resumes', __name__, url_prefix='/resumes')

ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@resumes_bp.route('', methods=['POST'])
@require_auth
def upload_resume():
    """Upload a resume file."""
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed. Please upload PDF, DOC, or DOCX files.'}), 400
        
        # Check file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > MAX_FILE_SIZE:
            return jsonify({'error': 'File too large. Maximum size is 5MB.'}), 400
        
        # Create uploads directory if it doesn't exist
        upload_dir = os.path.join(current_app.root_path, '..', 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generate unique filename
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        filepath = os.path.join(upload_dir, unique_filename)
        
        # Save file
        file.save(filepath)
        
        # Extract text from file
        extracted_text = extract_text_from_file(filepath)
        
        # Create resume record
        resume = Resume(
            user_id=request.user_id,
            filename=filename,
            filepath=filepath,
            text=extracted_text
        )
        
        db.session.add(resume)
        db.session.commit()
        
        return jsonify({
            'message': 'Resume uploaded successfully',
            'resume': resume.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        # Clean up file if it was saved
        if 'filepath' in locals() and os.path.exists(filepath):
            os.remove(filepath)
        return jsonify({'error': 'Failed to upload resume', 'detail': str(e)}), 500

@resumes_bp.route('', methods=['GET'])
@require_auth
def list_resumes():
    """List user's resumes."""
    try:
        resumes = Resume.query.filter_by(user_id=request.user_id).order_by(Resume.created_at.desc()).all()
        
        return jsonify({
            'resumes': [resume.to_dict() for resume in resumes]
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch resumes', 'detail': str(e)}), 500

@resumes_bp.route('/<int:resume_id>', methods=['DELETE'])
@require_auth
def delete_resume(resume_id):
    """Delete a resume."""
    try:
        resume = Resume.query.filter_by(id=resume_id, user_id=request.user_id).first()
        
        if not resume:
            return jsonify({'error': 'Resume not found'}), 404
        
        # Delete file from filesystem
        if os.path.exists(resume.filepath):
            os.remove(resume.filepath)
        
        # Delete from database
        db.session.delete(resume)
        db.session.commit()
        
        return jsonify({'message': 'Resume deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete resume', 'detail': str(e)}), 500

@resumes_bp.route('/<int:resume_id>', methods=['GET'])
@require_auth
def get_resume(resume_id):
    """Get a specific resume."""
    try:
        resume = Resume.query.filter_by(id=resume_id, user_id=request.user_id).first()
        
        if not resume:
            return jsonify({'error': 'Resume not found'}), 404
        
        return jsonify({
            'resume': resume.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch resume', 'detail': str(e)}), 500
