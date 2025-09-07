"""Admin API endpoints for backend management."""

import os
from flask import Blueprint, request, jsonify, render_template_string
from models import db, User, Resume, JobPosting, MatchResult
from api.auth import require_auth
from datetime import datetime, timedelta

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Simple admin template
ADMIN_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>ResumeRanker Admin Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .header { border-bottom: 2px solid #2563eb; padding-bottom: 10px; margin-bottom: 20px; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .stat-card { background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; }
        .stat-number { font-size: 2em; font-weight: bold; color: #2563eb; }
        .stat-label { color: #666; margin-top: 5px; }
        .section { margin-bottom: 30px; }
        .section h3 { color: #333; border-bottom: 1px solid #eee; padding-bottom: 10px; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background-color: #f8f9fa; font-weight: bold; }
        .btn { padding: 8px 16px; margin: 4px; border: none; border-radius: 4px; cursor: pointer; text-decoration: none; display: inline-block; }
        .btn-danger { background: #dc3545; color: white; }
        .btn-primary { background: #2563eb; color: white; }
        .btn:hover { opacity: 0.8; }
        .search-box { padding: 8px; margin: 10px 0; width: 300px; border: 1px solid #ddd; border-radius: 4px; }
        .filter-section { margin: 20px 0; padding: 15px; background: #f8f9fa; border-radius: 8px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔧 ResumeRanker Admin Dashboard</h1>
            <p>Backend Management & Analytics</p>
        </div>

        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">{{ stats.total_users }}</div>
                <div class="stat-label">Total Users</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ stats.total_resumes }}</div>
                <div class="stat-label">Resumes Uploaded</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ stats.total_jobs }}</div>
                <div class="stat-label">Jobs Parsed</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{{ stats.total_matches }}</div>
                <div class="stat-label">Matches Performed</div>
            </div>
        </div>

        <div class="section">
            <h3>👥 Recent Users</h3>
            <div class="filter-section">
                <input type="text" class="search-box" placeholder="Search users by email..." id="userSearch">
            </div>
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Email</th>
                        <th>Created</th>
                        <th>Resumes</th>
                        <th>Matches</th>
                    </tr>
                </thead>
                <tbody>
                    {% for user_data in recent_users %}
                    <tr>
                        <td>{{ user_data.User.id }}</td>
                        <td>{{ user_data.User.email }}</td>
                        <td>{{ user_data.User.created_at.strftime('%Y-%m-%d %H:%M') }}</td>
                        <td>{{ user_data.resume_count }}</td>
                        <td>{{ user_data.match_count }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>

        <div class="section">
            <h3>📄 Recent Resumes</h3>
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>User</th>
                        <th>Filename</th>
                        <th>Size</th>
                        <th>Uploaded</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {% for resume_data in recent_resumes %}
                    <tr>
                        <td>{{ resume_data.Resume.id }}</td>
                        <td>{{ resume_data.User.email }}</td>
                        <td>{{ resume_data.Resume.filename }}</td>
                        <td>{{ resume_data.Resume.text|length if resume_data.Resume.text else 0 }} chars</td>
                        <td>{{ resume_data.Resume.created_at.strftime('%Y-%m-%d %H:%M') }}</td>
                        <td>
                            <button class="btn btn-danger" onclick="deleteResume({{ resume_data.Resume.id }})">Delete</button>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>

        <div class="section">
            <h3>💼 Job Postings</h3>
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Title</th>
                        <th>Company</th>
                        <th>Skills</th>
                        <th>Parsed</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {% for job in recent_jobs %}
                    <tr>
                        <td>{{ job.id }}</td>
                        <td>{{ job.title[:50] }}{% if job.title|length > 50 %}...{% endif %}</td>
                        <td>{{ job.company or 'N/A' }}</td>
                        <td>{{ job.skills|length }} skills</td>
                        <td>{{ job.created_at.strftime('%Y-%m-%d %H:%M') }}</td>
                        <td>
                            <button class="btn btn-danger" onclick="deleteJob({{ job.id }})">Delete</button>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>

        <div class="section">
            <h3>🎯 Recent Matches</h3>
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>User</th>
                        <th>Score</th>
                        <th>Missing Keywords</th>
                        <th>Matched</th>
                    </tr>
                </thead>
                <tbody>
                    {% for match_data in recent_matches %}
                    <tr>
                        <td>{{ match_data.MatchResult.id }}</td>
                        <td>{{ match_data.User.email }}</td>
                        <td>{{ match_data.MatchResult.score }}/100</td>
                        <td>{{ match_data.MatchResult.missing_keywords|length }}</td>
                        <td>{{ match_data.MatchResult.created_at.strftime('%Y-%m-%d %H:%M') }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>

        <div class="section">
            <h3>🔧 System Info</h3>
            <div class="filter-section">
                <p><strong>Database:</strong> SQLite ({{ stats.db_size }} MB)</p>
                <p><strong>Uploads Directory:</strong> {{ stats.uploads_count }} files</p>
                <p><strong>Last Updated:</strong> {{ stats.last_updated }}</p>
                <p><strong>OpenAI API:</strong> {{ 'Configured' if stats.openai_configured else 'Not Configured (Using Fallback)' }}</p>
            </div>
        </div>
    </div>

    <script>
        function deleteResume(id) {
            if (confirm('Are you sure you want to delete this resume?')) {
                fetch(`/api/admin/resumes/${id}`, {method: 'DELETE'})
                    .then(() => location.reload());
            }
        }
        
        function deleteJob(id) {
            if (confirm('Are you sure you want to delete this job posting?')) {
                fetch(`/api/admin/jobs/${id}`, {method: 'DELETE'})
                    .then(() => location.reload());
            }
        }
        
        // Auto-refresh every 30 seconds
        setTimeout(() => location.reload(), 30000);
    </script>
</body>
</html>
"""

@admin_bp.route('/')
def admin_dashboard():
    """Admin dashboard with system overview."""
    try:
        # Get statistics
        stats = {
            'total_users': User.query.count(),
            'total_resumes': Resume.query.count(),
            'total_jobs': JobPosting.query.count(),
            'total_matches': MatchResult.query.count(),
            'db_size': 0,  # Would need to calculate actual DB size
            'uploads_count': 0,  # Would need to count uploads directory
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'openai_configured': bool(os.getenv('OPENAI_API_KEY'))
        }
        
        # Get recent data
        recent_users = db.session.query(
            User,
            db.func.count(Resume.id).label('resume_count'),
            db.func.count(MatchResult.id).label('match_count')
        ).outerjoin(Resume, User.id == Resume.user_id).outerjoin(MatchResult, User.id == MatchResult.user_id).group_by(User.id).order_by(User.created_at.desc()).limit(10).all()
        
        recent_resumes = db.session.query(Resume, User).join(User).order_by(Resume.created_at.desc()).limit(10).all()
        recent_jobs = JobPosting.query.order_by(JobPosting.created_at.desc()).limit(10).all()
        recent_matches = db.session.query(MatchResult, User).join(User).order_by(MatchResult.created_at.desc()).limit(10).all()
        
        return render_template_string(ADMIN_TEMPLATE, 
                                    stats=stats,
                                    recent_users=recent_users,
                                    recent_resumes=recent_resumes,
                                    recent_jobs=recent_jobs,
                                    recent_matches=recent_matches)
    except Exception as e:
        return f"Error loading admin dashboard: {str(e)}", 500

@admin_bp.route('/resumes/<int:resume_id>', methods=['DELETE'])
def delete_resume_admin(resume_id):
    """Delete a resume from admin panel."""
    try:
        resume = Resume.query.get(resume_id)
        if not resume:
            return jsonify({'error': 'Resume not found'}), 404
        
        # Delete file from filesystem
        import os
        if os.path.exists(resume.filepath):
            os.remove(resume.filepath)
        
        # Delete from database
        db.session.delete(resume)
        db.session.commit()
        
        return jsonify({'message': 'Resume deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete resume', 'detail': str(e)}), 500

@admin_bp.route('/jobs/<int:job_id>', methods=['DELETE'])
def delete_job_admin(job_id):
    """Delete a job posting from admin panel."""
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

@admin_bp.route('/stats')
def get_stats():
    """Get system statistics as JSON."""
    try:
        stats = {
            'total_users': User.query.count(),
            'total_resumes': Resume.query.count(),
            'total_jobs': JobPosting.query.count(),
            'total_matches': MatchResult.query.count(),
            'recent_activity': {
                'users_today': User.query.filter(User.created_at >= datetime.now().date()).count(),
                'resumes_today': Resume.query.filter(Resume.created_at >= datetime.now().date()).count(),
                'matches_today': MatchResult.query.filter(MatchResult.created_at >= datetime.now().date()).count(),
            }
        }
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({'error': 'Failed to get stats', 'detail': str(e)}), 500
