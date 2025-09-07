import React from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

const Home = () => {
  const { isAuthenticated } = useAuth()

  return (
    <div>
      <div className="text-center mb-4">
        <h1 className="text-4xl font-bold mb-2">ResumeRanker</h1>
        <p className="text-xl text-gray-600 mb-4">
          AI-powered resume and job matching platform
        </p>
      </div>

      <div className="grid grid-3 mb-4">
        <div className="card text-center">
          <h3 className="card-title mb-2">Upload Resumes</h3>
          <p className="text-gray-600 mb-3">
            Upload your resume files (PDF, DOC, DOCX) and extract text automatically
          </p>
          {isAuthenticated ? (
            <Link to="/resumes" className="btn btn-primary">
              Manage Resumes
            </Link>
          ) : (
            <Link to="/signup" className="btn btn-primary">
              Get Started
            </Link>
          )}
        </div>

        <div className="card text-center">
          <h3 className="card-title mb-2">Parse Job Postings</h3>
          <p className="text-gray-600 mb-3">
            Paste a job URL and automatically extract requirements, skills, and details
          </p>
          {isAuthenticated ? (
            <Link to="/job" className="btn btn-primary">
              Parse Job
            </Link>
          ) : (
            <Link to="/signup" className="btn btn-primary">
              Get Started
            </Link>
          )}
        </div>

        <div className="card text-center">
          <h3 className="card-title mb-2">AI Matching</h3>
          <p className="text-gray-600 mb-3">
            Get AI-powered analysis of how well your resume matches job requirements
          </p>
          {isAuthenticated ? (
            <Link to="/compare" className="btn btn-primary">
              Compare Now
            </Link>
          ) : (
            <Link to="/signup" className="btn btn-primary">
              Get Started
            </Link>
          )}
        </div>
      </div>

      <div className="card">
        <h2 className="card-title mb-2">How It Works</h2>
        <div className="grid grid-2">
          <div>
            <h4 className="font-semibold mb-2">1. Upload Your Resume</h4>
            <p className="text-gray-600">
              Upload your resume in PDF, DOC, or DOCX format. Our system will automatically extract and analyze the text content.
            </p>
          </div>
          <div>
            <h4 className="font-semibold mb-2">2. Parse Job Postings</h4>
            <p className="text-gray-600">
              Paste any job posting URL and we'll extract the key requirements, skills, and job details automatically.
            </p>
          </div>
          <div>
            <h4 className="font-semibold mb-2">3. Get AI Analysis</h4>
            <p className="text-gray-600">
              Our AI analyzes your resume against job requirements and provides a match score with specific suggestions.
            </p>
          </div>
          <div>
            <h4 className="font-semibold mb-2">4. Improve Your Resume</h4>
            <p className="text-gray-600">
              Use our suggestions to identify missing keywords and skills to improve your resume for better job matches.
            </p>
          </div>
        </div>
      </div>

      {!isAuthenticated && (
        <div className="text-center mt-4">
          <p className="text-gray-600 mb-2">Ready to get started?</p>
          <div className="flex gap-2 justify-center">
            <Link to="/signup" className="btn btn-primary">
              Sign Up
            </Link>
            <Link to="/login" className="btn btn-secondary">
              Login
            </Link>
          </div>
        </div>
      )}
    </div>
  )
}

export default Home
