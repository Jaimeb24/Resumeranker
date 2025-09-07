"""LLM integration services for resume analysis and matching."""

import os
import json
import re
from typing import Dict, List, Optional
from openai import OpenAI

def suggest_resume_additions(resume_text: str, job_json: Dict, model: str = None) -> Dict:
    """
    Use OpenAI to analyze resume against job requirements and provide suggestions.
    
    Args:
        resume_text: The extracted text from the resume
        job_json: Job posting data with title, description, skills, requirements
        model: OpenAI model to use (defaults to env var or gpt-4o-mini)
    
    Returns:
        Dict with score (0-100), missing_keywords, and suggestions
    """
    # Get model from parameter or environment
    if not model:
        model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
    
    # Check if OpenAI API key is available
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        # Return fallback response if no API key
        return get_fallback_response(resume_text, job_json)
    
    try:
        client = OpenAI(api_key=api_key)
        
        # Build the system prompt
        system_prompt = """You are a resume analysis expert. Analyze the provided resume against the job requirements and return a JSON response with exactly this structure:

{
  "score": 0-100 integer (overall match score),
  "missing_keywords": ["keyword1", "keyword2", ...],
  "suggestions": ["suggestion1", "suggestion2", ...]
}

Focus on:
- Technical skills alignment
- Experience relevance
- Missing qualifications
- Actionable improvement suggestions

Be specific and practical in your suggestions."""

        # Build the user prompt
        job_title = job_json.get('title', 'Unknown Position')
        job_description = job_json.get('description', '')
        job_skills = job_json.get('skills', [])
        job_requirements = job_json.get('requirements', [])
        
        user_prompt = f"""Job Title: {job_title}
Job Description: {job_description}
Required Skills: {', '.join(job_skills) if job_skills else 'Not specified'}
Requirements: {', '.join(job_requirements) if job_requirements else 'Not specified'}

Resume Text:
{resume_text}

Please analyze this resume against the job requirements and provide your assessment in the exact JSON format specified."""

        # Make the API call
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=1000
        )
        
        # Extract and parse the response
        content = response.choices[0].message.content.strip()
        
        # Try to extract JSON from the response
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            result = json.loads(json_str)
            
            # Validate and clean the response
            return validate_and_clean_response(result)
        else:
            # If no JSON found, return fallback
            return get_fallback_response(resume_text, job_json)
            
    except Exception as e:
        print(f"Error calling OpenAI API: {e}")
        return get_fallback_response(resume_text, job_json)

def get_fallback_response(resume_text: str, job_json: Dict) -> Dict:
    """
    Provide a fallback response when OpenAI API is not available.
    Uses basic keyword matching for a baseline score.
    """
    # Basic keyword matching for fallback
    job_text = f"{job_json.get('title', '')} {job_json.get('description', '')}"
    job_skills = job_json.get('skills', [])
    job_requirements = job_json.get('requirements', [])
    
    # Convert to lowercase for comparison
    resume_lower = resume_text.lower()
    job_lower = job_text.lower()
    
    # Count matching skills
    matching_skills = 0
    missing_skills = []
    
    for skill in job_skills:
        if skill.lower() in resume_lower:
            matching_skills += 1
        else:
            missing_skills.append(skill)
    
    # Calculate basic score
    total_skills = len(job_skills) if job_skills else 1
    skill_score = (matching_skills / total_skills) * 50  # Skills contribute 50% to score
    
    # Basic keyword matching for other terms
    job_keywords = re.findall(r'\b\w{4,}\b', job_lower)
    resume_keywords = re.findall(r'\b\w{4,}\b', resume_lower)
    
    matching_keywords = set(job_keywords) & set(resume_keywords)
    keyword_score = (len(matching_keywords) / max(len(job_keywords), 1)) * 50  # Keywords contribute 50% to score
    
    total_score = min(int(skill_score + keyword_score), 100)
    
    # Generate basic suggestions
    suggestions = []
    if missing_skills:
        suggestions.append(f"Consider highlighting experience with: {', '.join(missing_skills[:3])}")
    
    if total_score < 70:
        suggestions.append("Add more relevant experience and skills to improve match")
    
    if not suggestions:
        suggestions.append("Resume looks well-aligned with job requirements")
    
    return {
        "score": total_score,
        "missing_keywords": missing_skills[:5],  # Limit to 5 missing keywords
        "suggestions": suggestions[:3]  # Limit to 3 suggestions
    }

def validate_and_clean_response(response: Dict) -> Dict:
    """Validate and clean the LLM response to ensure proper format."""
    # Ensure score is an integer between 0-100
    score = response.get('score', 0)
    if isinstance(score, str):
        try:
            score = int(score)
        except ValueError:
            score = 0
    score = max(0, min(100, int(score)))
    
    # Ensure missing_keywords is a list
    missing_keywords = response.get('missing_keywords', [])
    if not isinstance(missing_keywords, list):
        missing_keywords = []
    
    # Ensure suggestions is a list
    suggestions = response.get('suggestions', [])
    if not isinstance(suggestions, list):
        suggestions = []
    
    return {
        "score": score,
        "missing_keywords": missing_keywords[:10],  # Limit to 10 keywords
        "suggestions": suggestions[:5]  # Limit to 5 suggestions
    }
