"""Tests for job parsing functionality."""

import pytest
import os
from unittest.mock import patch, mock_open
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app import create_app
from models import db, JobPosting

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
def auth_headers(client):
    """Get authentication headers for testing."""
    # Create a test user
    response = client.post('/api/auth/signup', json={
        'email': 'test@example.com',
        'password': 'password123'
    })
    
    token = response.json['token']
    return {'Authorization': f'Bearer {token}'}

def test_parse_job_static_html(client, auth_headers):
    """Test parsing a job posting from static HTML."""
    # Read the static HTML fixture
    fixture_path = os.path.join(os.path.dirname(__file__), 'fixtures', 'job_static.html')
    
    with open(fixture_path, 'r') as f:
        html_content = f.read()
    
    # Mock the requests.get to return our static HTML
    with patch('services.scraper.requests.get') as mock_get:
        mock_response = mock_get.return_value
        mock_response.content = html_content.encode('utf-8')
        mock_response.raise_for_status.return_value = None
        
        # Test the job parsing endpoint
        response = client.post('/api/jobs/parse', 
                             json={'url': 'https://example.com/job-posting'},
                             headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json
        
        # Verify the response structure
        assert 'job_posting' in data
        job_posting = data['job_posting']
        
        # Verify extracted data
        assert job_posting['title'] == 'Senior Software Engineer'
        assert job_posting['company'] == 'TechCorp Inc.'
        assert 'Python' in job_posting['skills']
        assert 'JavaScript' in job_posting['skills']
        assert 'React' in job_posting['skills']
        assert len(job_posting['requirements']) > 0
        assert '5+ years of experience' in str(job_posting['requirements'])

def test_parse_job_invalid_url(client, auth_headers):
    """Test parsing with invalid URL."""
    response = client.post('/api/jobs/parse',
                         json={'url': 'not-a-valid-url'},
                         headers=auth_headers)
    
    assert response.status_code == 500
    assert 'error' in response.json

def test_parse_job_missing_url(client, auth_headers):
    """Test parsing without URL."""
    response = client.post('/api/jobs/parse',
                         json={},
                         headers=auth_headers)
    
    assert response.status_code == 400
    assert 'URL is required' in response.json['error']

def test_parse_job_unauthorized(client):
    """Test parsing without authentication."""
    response = client.post('/api/jobs/parse',
                         json={'url': 'https://example.com/job'})
    
    assert response.status_code == 401

def test_list_jobs(client, auth_headers):
    """Test listing job postings."""
    # First, create a job posting
    with patch('services.scraper.requests.get') as mock_get:
        mock_response = mock_get.return_value
        mock_response.content = b'<html><h1>Test Job</h1></html>'
        mock_response.raise_for_status.return_value = None
        
        client.post('/api/jobs/parse',
                   json={'url': 'https://example.com/test-job'},
                   headers=auth_headers)
    
    # Now test listing
    response = client.get('/api/jobs', headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json
    assert 'job_postings' in data
    assert len(data['job_postings']) >= 1

def test_get_job_by_id(client, auth_headers):
    """Test getting a specific job posting by ID."""
    # First, create a job posting
    with patch('services.scraper.requests.get') as mock_get:
        mock_response = mock_get.return_value
        mock_response.content = b'<html><h1>Test Job</h1></html>'
        mock_response.raise_for_status.return_value = None
        
        create_response = client.post('/api/jobs/parse',
                                    json={'url': 'https://example.com/test-job'},
                                    headers=auth_headers)
        
        job_id = create_response.json['job_posting']['id']
    
    # Now test getting by ID
    response = client.get(f'/api/jobs/{job_id}', headers=auth_headers)
    
    assert response.status_code == 200
    data = response.json
    assert 'job_posting' in data
    assert data['job_posting']['id'] == job_id

def test_get_nonexistent_job(client, auth_headers):
    """Test getting a job posting that doesn't exist."""
    response = client.get('/api/jobs/99999', headers=auth_headers)
    
    assert response.status_code == 404
    assert 'not found' in response.json['error']
