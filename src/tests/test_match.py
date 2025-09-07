"""Tests for resume matching functionality."""

import pytest
from unittest.mock import patch, MagicMock
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app import create_app
from models import db, User, Resume, JobPosting

@pytest.fixture
def app():
    """Create test application."""
    app, socketio = create_app('testing')
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()

@pytest.fixture
def test_user(app):
    """Create a test user."""
    with app.app_context():
        user = User(email='test@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        return user

@pytest.fixture
def test_resume(app, test_user):
    """Create a test resume."""
    with app.app_context():
        resume = Resume(
            user_id=test_user.id,
            filename='test_resume.pdf',
            filepath='/tmp/test_resume.pdf',
            text='Experienced software engineer with Python, JavaScript, and React skills. 5+ years of experience in web development.'
        )
        db.session.add(resume)
        db.session.commit()
        return resume

@pytest.fixture
def test_job(app):
    """Create a test job posting."""
    with app.app_context():
        job = JobPosting(
            url='https://example.com/job',
            title='Senior Software Engineer',
            company='TechCorp',
            description='Looking for a senior software engineer with Python and React experience.',
            skills=['Python', 'JavaScript', 'React', 'SQL'],
            requirements=['5+ years experience', 'Bachelor degree', 'Team leadership']
        )
        db.session.add(job)
        db.session.commit()
        return job

@pytest.fixture
def auth_headers(client, test_user):
    """Get authentication headers for testing."""
    response = client.post('/api/auth/login', json={
        'email': 'test@example.com',
        'password': 'password123'
    })
    
    token = response.json['token']
    return {'Authorization': f'Bearer {token}'}

@patch('services.llm.suggest_resume_additions')
def test_match_resume_with_job(mock_llm, client, auth_headers, test_resume, test_job):
    """Test matching a resume with a job posting."""
    # Mock the LLM response
    mock_llm.return_value = {
        'score': 85,
        'missing_keywords': ['SQL', 'Team leadership'],
        'suggestions': [
            'Add SQL experience to your resume',
            'Highlight any team leadership experience'
        ]
    }
    
    response = client.post('/api/match', 
                          json={
                              'resumeId': test_resume.id,
                              'jobPostingId': test_job.id
                          },
                          headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json
    
    # Verify the response structure
    assert 'match_result' in data
    match_result = data['match_result']
    
    assert match_result['score'] == 85
    assert 'SQL' in match_result['missing_keywords']
    assert 'Team leadership' in match_result['missing_keywords']
    assert len(match_result['suggestions']) == 2
    
    # Verify the LLM was called with correct parameters
    mock_llm.assert_called_once()
    call_args = mock_llm.call_args[0]
    assert test_resume.text in call_args[0]  # resume_text
    assert call_args[1]['title'] == test_job.title  # job_json

@patch('services.llm.suggest_resume_additions')
def test_match_custom_resume_text(mock_llm, client, auth_headers, test_job):
    """Test matching with custom resume text."""
    # Mock the LLM response
    mock_llm.return_value = {
        'score': 70,
        'missing_keywords': ['React'],
        'suggestions': ['Add React experience to your resume']
    }
    
    custom_resume_text = 'Software engineer with Python and JavaScript experience.'
    
    response = client.post('/api/match',
                          json={
                              'resumeText': custom_resume_text,
                              'jobPostingId': test_job.id
                          },
                          headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json
    
    match_result = data['match_result']
    assert match_result['score'] == 70
    assert 'React' in match_result['missing_keywords']
    
    # Verify the LLM was called with custom resume text
    mock_llm.assert_called_once()
    call_args = mock_llm.call_args[0]
    assert call_args[0] == custom_resume_text

@patch('services.llm.suggest_resume_additions')
def test_match_custom_job_data(mock_llm, client, auth_headers, test_resume):
    """Test matching with custom job data."""
    # Mock the LLM response
    mock_llm.return_value = {
        'score': 60,
        'missing_keywords': ['Docker', 'AWS'],
        'suggestions': ['Add Docker and AWS experience']
    }
    
    custom_job_data = {
        'title': 'DevOps Engineer',
        'description': 'Looking for DevOps engineer with Docker and AWS experience.',
        'skills': ['Docker', 'AWS', 'Kubernetes'],
        'requirements': ['3+ years DevOps experience']
    }
    
    response = client.post('/api/match',
                          json={
                              'resumeId': test_resume.id,
                              'jobData': custom_job_data
                          },
                          headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json
    
    match_result = data['match_result']
    assert match_result['score'] == 60
    assert 'Docker' in match_result['missing_keywords']
    assert 'AWS' in match_result['missing_keywords']
    
    # Verify the LLM was called with custom job data
    mock_llm.assert_called_once()
    call_args = mock_llm.call_args[0]
    assert call_args[1]['title'] == 'DevOps Engineer'

def test_match_missing_parameters(client, auth_headers):
    """Test matching with missing parameters."""
    # Missing both resumeId and resumeText
    response = client.post('/api/match',
                          json={'jobPostingId': 1},
                          headers=auth_headers)
    
    assert response.status_code == 400
    assert 'resumeId or resumeText is required' in response.json['error']
    
    # Missing both jobPostingId and jobData
    response = client.post('/api/match',
                          json={'resumeId': 1},
                          headers=auth_headers)
    
    assert response.status_code == 400
    assert 'jobPostingId or jobData is required' in response.json['error']

def test_match_nonexistent_resume(client, auth_headers, test_job):
    """Test matching with nonexistent resume."""
    response = client.post('/api/match',
                          json={
                              'resumeId': 99999,
                              'jobPostingId': test_job.id
                          },
                          headers=auth_headers)
    
    assert response.status_code == 404
    assert 'Resume not found' in response.json['error']

def test_match_nonexistent_job(client, auth_headers, test_resume):
    """Test matching with nonexistent job posting."""
    response = client.post('/api/match',
                          json={
                              'resumeId': test_resume.id,
                              'jobPostingId': 99999
                          },
                          headers=auth_headers)
    
    assert response.status_code == 404
    assert 'Job posting not found' in response.json['error']

def test_match_unauthorized(client, test_resume, test_job):
    """Test matching without authentication."""
    response = client.post('/api/match',
                          json={
                              'resumeId': test_resume.id,
                              'jobPostingId': test_job.id
                          })
    
    assert response.status_code == 401

@patch('services.llm.suggest_resume_additions')
def test_match_fallback_without_openai(mock_llm, client, auth_headers, test_resume, test_job):
    """Test matching fallback when OpenAI API is not available."""
    # Mock the LLM to return fallback response (simulating no API key)
    mock_llm.return_value = {
        'score': 45,
        'missing_keywords': ['React', 'SQL'],
        'suggestions': ['Consider highlighting experience with: React, SQL']
    }
    
    response = client.post('/api/match',
                          json={
                              'resumeId': test_resume.id,
                              'jobPostingId': test_job.id
                          },
                          headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json
    
    match_result = data['match_result']
    assert match_result['score'] == 45
    assert len(match_result['missing_keywords']) > 0
    assert len(match_result['suggestions']) > 0
