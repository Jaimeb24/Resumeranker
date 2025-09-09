"""Resume matching API endpoints."""

from flask import Blueprint, request, jsonify
from models import db, Resume, JobPosting, MatchResult
from services.llm import suggest_resume_additions
from sockets.events import emit_match_finished
from api.auth import require_auth

match_bp = Blueprint('match', __name__, url_prefix='/match')

@match_bp.route('', methods=['POST'])
@require_auth
def match_resume():
    """Match a resume against a job posting."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        resume_id = data.get('resumeId')
        resume_text = data.get('resumeText')
        job_posting_id = data.get('jobPostingId')
        job_data = data.get('jobData')
        
        # Validate input - need either resumeId or resumeText
        if not resume_id and not resume_text:
            return jsonify({'error': 'Either resumeId or resumeText is required'}), 400
        
        # Validate input - need either jobPostingId or jobData
        if not job_posting_id and not job_data:
            return jsonify({'error': 'Either jobPostingId or jobData is required'}), 400
        
        # Get resume text
        if resume_id:
            resume = Resume.query.filter_by(id=resume_id, user_id=request.user_id).first()
            if not resume:
                return jsonify({'error': 'Resume not found'}), 404
            resume_text = resume.text
            if not resume_text:
                return jsonify({'error': 'Resume text not available'}), 400
        
        # Get job data
        if job_posting_id:
            job_posting = JobPosting.query.get(job_posting_id)
            if not job_posting:
                return jsonify({'error': 'Job posting not found'}), 404
            job_data = job_posting.to_dict()
        
        # Emit match started event
        from flask import current_app
        socketio = current_app.extensions['socketio']
        
        try:
            # Perform matching using LLM
            match_result = suggest_resume_additions(resume_text, job_data)
            
            # Create match result record
            match_record = MatchResult(
                user_id=request.user_id,
                resume_id=resume_id,
                job_posting_id=job_posting_id,
                score=match_result['score'],
                missing_keywords=match_result['missing_keywords'],
                suggestions=match_result['suggestions']
            )
            
            db.session.add(match_record)
            db.session.commit()
            
            # Prepare response data
            response_data = {
                'id': match_record.id,
                'score': match_record.score,
                'missing_keywords': match_record.missing_keywords,
                'suggestions': match_record.suggestions,
                'created_at': match_record.created_at.isoformat()
            }
            
            # Emit match finished event
            emit_match_finished(socketio, request.user_id, response_data, success=True)
            
            return jsonify({
                'message': 'Resume matching completed successfully',
                'match_result': response_data
            }), 200
            
        except Exception as match_error:
            db.session.rollback()
            # Emit match finished event with error
            emit_match_finished(socketio, request.user_id, None, success=False, error=str(match_error))
            raise match_error
        
    except Exception as e:
        return jsonify({'error': 'Failed to match resume', 'detail': str(e)}), 500

@match_bp.route('/history', methods=['GET'])
@require_auth
def get_match_history():
    """Get user's match history."""
    try:
        matches = MatchResult.query.filter_by(user_id=request.user_id).order_by(MatchResult.created_at.desc()).all()
        
        return jsonify({
            'match_results': [match.to_dict() for match in matches]
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch match history', 'detail': str(e)}), 500

@match_bp.route('/<int:match_id>', methods=['GET'])
@require_auth
def get_match_result(match_id):
    """Get a specific match result."""
    try:
        match = MatchResult.query.filter_by(id=match_id, user_id=request.user_id).first()
        
        if not match:
            return jsonify({'error': 'Match result not found'}), 404
        
        return jsonify({
            'match_result': match.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch match result', 'detail': str(e)}), 500

@match_bp.route('/bulk', methods=['POST'])
@require_auth
def bulk_match_resumes():
    """Match multiple resumes against a job posting."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        resume_ids = data.get('resumeIds', [])
        job_posting_id = data.get('jobPostingId')
        job_data = data.get('jobData')
        
        # Validate input
        if not resume_ids:
            return jsonify({'error': 'resumeIds is required'}), 400
        
        if not job_posting_id and not job_data:
            return jsonify({'error': 'Either jobPostingId or jobData is required'}), 400
        
        # Get job data
        if job_posting_id:
            job_posting = JobPosting.query.get(job_posting_id)
            if not job_posting:
                return jsonify({'error': 'Job posting not found'}), 404
            job_data = job_posting.to_dict()
        
        # Get all resumes for the user
        resumes = Resume.query.filter(
            Resume.id.in_(resume_ids),
            Resume.user_id == request.user_id
        ).all()
        
        if len(resumes) != len(resume_ids):
            return jsonify({'error': 'Some resumes not found or not owned by user'}), 404
        
        # Emit bulk match started event
        from flask import current_app
        socketio = current_app.extensions['socketio']
        
        results = []
        
        try:
            for i, resume in enumerate(resumes):
                # Emit progress update
                socketio.emit('bulk_match_progress', {
                    'user_id': request.user_id,
                    'current': i + 1,
                    'total': len(resumes),
                    'resume_name': resume.filename,
                    'message': f'Matching resume {i + 1} of {len(resumes)}...'
                }, room=f'user_{request.user_id}')
                
                # Perform matching
                match_result = suggest_resume_additions(resume.text, job_data)
                
                # Create match result record
                match_record = MatchResult(
                    user_id=request.user_id,
                    resume_id=resume.id,
                    job_posting_id=job_posting_id,
                    score=match_result['score'],
                    missing_keywords=match_result['missing_keywords'],
                    suggestions=match_result['suggestions']
                )
                
                db.session.add(match_record)
                db.session.flush()  # Get the ID
                
                results.append({
                    'resume_id': resume.id,
                    'resume_name': resume.filename,
                    'match_result': match_record.to_dict()
                })
            
            db.session.commit()
            
            # Emit bulk match finished event
            socketio.emit('bulk_match_finished', {
                'user_id': request.user_id,
                'success': True,
                'message': f'Successfully matched {len(resumes)} resumes!',
                'results': results
            }, room=f'user_{request.user_id}')
            
            return jsonify({
                'message': f'Bulk matching completed for {len(resumes)} resumes',
                'results': results
            }), 200
            
        except Exception as match_error:
            db.session.rollback()
            # Emit bulk match finished event with error
            socketio.emit('bulk_match_finished', {
                'user_id': request.user_id,
                'success': False,
                'message': f'Bulk matching failed: {str(match_error)}'
            }, room=f'user_{request.user_id}')
            raise match_error
        
    except Exception as e:
        return jsonify({'error': 'Failed to perform bulk matching', 'detail': str(e)}), 500
