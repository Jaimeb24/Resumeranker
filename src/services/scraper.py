"""Web scraping services for job postings."""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import re
from typing import Dict, List, Optional
import os

def is_valid_url(url: str) -> bool:
    """Check if the URL is valid and safe to scrape."""
    try:
        parsed = urlparse(url)
        # Check if it's a valid URL with http/https scheme
        if not parsed.scheme or parsed.scheme not in ['http', 'https']:
            return False
        
        # Check hostname length (basic security check)
        if len(parsed.hostname or '') > 255:
            return False
            
        return True
    except Exception:
        return False

def scrape_job_posting(url: str) -> Dict[str, any]:
    """
    Scrape a job posting from a URL and extract structured information.
    
    Returns:
        Dict with keys: title, company, description, skills, requirements
    """
    if not is_valid_url(url):
        raise ValueError("Invalid URL provided")
    
    try:
        # Set headers to mimic a real browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        # Make request with timeout
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract title
        title = extract_title(soup)
        
        # Extract company
        company = extract_company(soup)
        
        # Extract description
        description = extract_description(soup)
        
        # Extract skills and requirements
        skills = extract_skills(soup, description)
        requirements = extract_requirements(soup, description)
        
        return {
            'title': title,
            'company': company,
            'description': description,
            'skills': skills,
            'requirements': requirements
        }
        
    except requests.RequestException as e:
        raise Exception(f"Failed to fetch URL: {str(e)}")
    except Exception as e:
        raise Exception(f"Failed to parse job posting: {str(e)}")

def extract_title(soup: BeautifulSoup) -> str:
    """Extract job title from the page."""
    # Common selectors for job titles
    title_selectors = [
        'h1.job-title',
        'h1[data-testid="job-title"]',
        '.job-title h1',
        'h1',
        '.title',
        '[data-testid="job-title"]',
        '.job-header h1',
        '.job-details h1'
    ]
    
    for selector in title_selectors:
        element = soup.select_one(selector)
        if element and element.get_text().strip():
            return element.get_text().strip()
    
    # Fallback: use page title
    title_tag = soup.find('title')
    if title_tag:
        return title_tag.get_text().strip()
    
    return "Job Title Not Found"

def extract_company(soup: BeautifulSoup) -> Optional[str]:
    """Extract company name from the page."""
    # Common selectors for company names
    company_selectors = [
        '.company-name',
        '[data-testid="company-name"]',
        '.job-company',
        '.employer-name',
        '.company',
        '.job-header .company',
        '.job-details .company'
    ]
    
    for selector in company_selectors:
        element = soup.select_one(selector)
        if element and element.get_text().strip():
            return element.get_text().strip()
    
    return None

def extract_description(soup: BeautifulSoup) -> str:
    """Extract job description from the page."""
    # Common selectors for job descriptions
    desc_selectors = [
        '.job-description',
        '[data-testid="job-description"]',
        '.job-details',
        '.description',
        '.job-content',
        '.job-body',
        '.job-summary'
    ]
    
    for selector in desc_selectors:
        element = soup.select_one(selector)
        if element:
            # Get text content and clean it up
            text = element.get_text(separator='\n', strip=True)
            if len(text) > 100:  # Only return if substantial content
                return text
    
    # Fallback: get all paragraph text
    paragraphs = soup.find_all('p')
    if paragraphs:
        text = '\n'.join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
        if len(text) > 100:
            return text
    
    return "Job description not found"

def extract_skills(soup: BeautifulSoup, description: str) -> List[str]:
    """Extract skills from the page content."""
    skills = []
    
    # Common skill keywords to look for
    skill_keywords = [
        'python', 'javascript', 'java', 'react', 'angular', 'vue', 'node.js',
        'sql', 'postgresql', 'mysql', 'mongodb', 'redis', 'docker', 'kubernetes',
        'aws', 'azure', 'gcp', 'git', 'jenkins', 'ci/cd', 'agile', 'scrum',
        'machine learning', 'ai', 'data science', 'analytics', 'tableau',
        'power bi', 'excel', 'salesforce', 'crm', 'api', 'rest', 'graphql',
        'microservices', 'devops', 'linux', 'bash', 'powershell'
    ]
    
    # Combine page text for analysis
    page_text = description.lower()
    
    # Look for skills in the text
    for skill in skill_keywords:
        if skill in page_text:
            skills.append(skill.title())
    
    # Remove duplicates and return
    return list(set(skills))

def extract_requirements(soup: BeautifulSoup, description: str) -> List[str]:
    """Extract requirements from the page content."""
    requirements = []
    
    # Look for common requirement patterns
    requirement_patterns = [
        r'(\d+)\+?\s*years?\s*(?:of\s*)?experience',
        r'degree\s*in\s*([^.,]+)',
        r'bachelor\'?s?\s*(?:degree\s*)?in\s*([^.,]+)',
        r'master\'?s?\s*(?:degree\s*)?in\s*([^.,]+)',
        r'phd\s*(?:in\s*)?([^.,]+)',
        r'certification\s*in\s*([^.,]+)',
        r'proficient\s*in\s*([^.,]+)',
        r'experience\s*with\s*([^.,]+)',
        r'knowledge\s*of\s*([^.,]+)'
    ]
    
    text = description.lower()
    
    for pattern in requirement_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            if isinstance(match, tuple):
                match = match[0]
            requirements.append(match.strip().title())
    
    # Remove duplicates and return
    return list(set(requirements))
