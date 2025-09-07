"""Job parsing API endpoints."""

from flask import Blueprint, request, jsonify
from models import db, JobPosting
from services.scraper import scrape_job_posting
from sockets.events import emit_parse_started, emit_parse_finished
from api.auth import require_auth

jobs_bp = Blueprint('jobs', __name__, url_prefix='/jobs')

@jobs_bp.route('/parse', methods=['POST'])
@require_auth
def parse_job():
    """Parse a job posting from URL."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        url = data.get('url', '').strip()
        
        if not url:
            return jsonify({'error': 'URL is required'}), 400
        
        # Emit parse started event
        from flask import current_app
        socketio = current_app.extensions['socketio']
        emit_parse_started(socketio, request.user_id, url)
        
        try:
            # Scrape the job posting
            job_data = scrape_job_posting(url)
            
            # Check if job already exists
            existing_job = JobPosting.query.filter_by(url=url).first()
            if existing_job:
                # Update existing job
                existing_job.title = job_data['title']
                existing_job.company = job_data['company']
                existing_job.description = job_data['description']
                existing_job.skills = job_data['skills']
                existing_job.requirements = job_data['requirements']
                job_posting = existing_job
            else:
                # Create new job posting
                job_posting = JobPosting(
                    url=url,
                    title=job_data['title'],
                    company=job_data['company'],
                    description=job_data['description'],
                    skills=job_data['skills'],
                    requirements=job_data['requirements']
                )
                db.session.add(job_posting)
            
            db.session.commit()
            
            # Emit parse finished event
            emit_parse_finished(socketio, request.user_id, job_posting.to_dict(), success=True)
            
            return jsonify({
                'message': 'Job posting parsed successfully',
                'job_posting': job_posting.to_dict()
            }), 200
            
        except Exception as scrape_error:
            db.session.rollback()
            # Emit parse finished event with error
            emit_parse_finished(socketio, request.user_id, None, success=False, error=str(scrape_error))
            raise scrape_error
        
    except Exception as e:
        return jsonify({'error': 'Failed to parse job posting', 'detail': str(e)}), 500

@jobs_bp.route('', methods=['GET'])
@require_auth
def list_jobs():
    """List all job postings."""
    try:
        jobs = JobPosting.query.order_by(JobPosting.created_at.desc()).all()
        
        return jsonify({
            'job_postings': [job.to_dict() for job in jobs]
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch job postings', 'detail': str(e)}), 500

@jobs_bp.route('/<int:job_id>', methods=['GET'])
@require_auth
def get_job(job_id):
    """Get a specific job posting."""
    try:
        job = JobPosting.query.get(job_id)
        
        if not job:
            return jsonify({'error': 'Job posting not found'}), 404
        
        return jsonify({
            'job_posting': job.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to fetch job posting', 'detail': str(e)}), 500

@jobs_bp.route('/<int:job_id>', methods=['DELETE'])
@require_auth
def delete_job(job_id):
    """Delete a job posting."""
    try:
        job = JobPosting.query.get(job_id)
        
        if not job:
            return jsonify({'error': 'Job posting not found'}), 404
        
        # Delete from database
        db.session.delete(job)
        db.session.commit()
        
        return jsonify({'message': 'Job posting deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete job posting', 'detail': str(e)}), 500
