from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import json

db = SQLAlchemy()

class User(db.Model):
    """User model for authentication and user management."""
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    resumes = db.relationship('Resume', backref='user', lazy=True, cascade='all, delete-orphan')
    match_results = db.relationship('MatchResult', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set the user's password."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if the provided password matches the user's password."""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert user to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'email': self.email,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Resume(db.Model):
    """Resume model for storing uploaded resume files and extracted text."""
    
    __tablename__ = 'resumes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    filepath = db.Column(db.String(500), nullable=False)
    text = db.Column(db.Text, nullable=True)  # Extracted text content
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    match_results = db.relationship('MatchResult', backref='resume', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert resume to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'filename': self.filename,
            'text': self.text,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class JobPosting(db.Model):
    """Job posting model for storing parsed job information."""
    
    __tablename__ = 'job_postings'
    
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(1000), nullable=False, index=True)
    title = db.Column(db.String(500), nullable=False)
    company = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text, nullable=True)
    skills_json = db.Column(db.Text, nullable=True)  # JSON string of skills array
    requirements_json = db.Column(db.Text, nullable=True)  # JSON string of requirements array
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    match_results = db.relationship('MatchResult', backref='job_posting', lazy=True, cascade='all, delete-orphan')
    
    @property
    def skills(self):
        """Get skills as a Python list."""
        if self.skills_json:
            try:
                return json.loads(self.skills_json)
            except json.JSONDecodeError:
                return []
        return []
    
    @skills.setter
    def skills(self, value):
        """Set skills from a Python list."""
        self.skills_json = json.dumps(value) if value else None
    
    @property
    def requirements(self):
        """Get requirements as a Python list."""
        if self.requirements_json:
            try:
                return json.loads(self.requirements_json)
            except json.JSONDecodeError:
                return []
        return []
    
    @requirements.setter
    def requirements(self, value):
        """Set requirements from a Python list."""
        self.requirements_json = json.dumps(value) if value else None
    
    def to_dict(self):
        """Convert job posting to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'url': self.url,
            'title': self.title,
            'company': self.company,
            'description': self.description,
            'skills': self.skills,
            'requirements': self.requirements,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class MatchResult(db.Model):
    """Match result model for storing resume-job matching results."""
    
    __tablename__ = 'match_results'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    resume_id = db.Column(db.Integer, db.ForeignKey('resumes.id'), nullable=True)
    job_posting_id = db.Column(db.Integer, db.ForeignKey('job_postings.id'), nullable=True)
    score = db.Column(db.Integer, nullable=False)  # 0-100 match score
    missing_keywords_json = db.Column(db.Text, nullable=True)  # JSON string of missing keywords
    suggestions_json = db.Column(db.Text, nullable=True)  # JSON string of suggestions
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    @property
    def missing_keywords(self):
        """Get missing keywords as a Python list."""
        if self.missing_keywords_json:
            try:
                return json.loads(self.missing_keywords_json)
            except json.JSONDecodeError:
                return []
        return []
    
    @missing_keywords.setter
    def missing_keywords(self, value):
        """Set missing keywords from a Python list."""
        self.missing_keywords_json = json.dumps(value) if value else None
    
    @property
    def suggestions(self):
        """Get suggestions as a Python list."""
        if self.suggestions_json:
            try:
                return json.loads(self.suggestions_json)
            except json.JSONDecodeError:
                return []
        return []
    
    @suggestions.setter
    def suggestions(self, value):
        """Set suggestions from a Python list."""
        self.suggestions_json = json.dumps(value) if value else None
    
    def to_dict(self):
        """Convert match result to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'resume_id': self.resume_id,
            'job_posting_id': self.job_posting_id,
            'score': self.score,
            'missing_keywords': self.missing_keywords,
            'suggestions': self.suggestions,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
