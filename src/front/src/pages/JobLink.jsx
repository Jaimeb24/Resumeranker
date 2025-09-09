import React, { useState, useEffect } from 'react'
import { useAuth } from '../context/AuthContext'
import { jobsAPI } from '../api/client'
import { useSockets } from '../hooks/useSockets'

const JobLink = () => {
  const [url, setUrl] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')
  const [jobData, setJobData] = useState(null)
  const [parseStatus, setParseStatus] = useState('')
  
  const { isAuthenticated } = useAuth()
  const { onParseStarted, onParseFinished } = useSockets()

  useEffect(() => {
    if (!isAuthenticated) return

    // Set up socket listeners
    onParseStarted((data) => {
      if (data.job_url === url) {
        setParseStatus('Parsing job posting...')
        setMessage('')
        setError('')
      }
    })

    onParseFinished((data) => {
      if (data.success) {
        setJobData(data.job_data)
        setParseStatus('')
        setMessage('Job posting parsed successfully!')
        setError('')
      } else {
        setParseStatus('')
        setError(data.message || 'Failed to parse job posting')
      }
    })

    return () => {
      // Cleanup listeners
    }
  }, [isAuthenticated, url, onParseStarted, onParseFinished])

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!url.trim()) {
      setError('Please enter a job URL')
      return
    }

    // Basic URL validation
    try {
      new URL(url)
    } catch {
      setError('Please enter a valid URL')
      return
    }

    setLoading(true)
    setError('')
    setMessage('')
    setJobData(null)
    setParseStatus('')

    try {
      const response = await jobsAPI.parse({ url })
      setJobData(response.data.job_posting)
      setMessage('Job posting parsed successfully!')
    } catch (error) {
      setError(error.response?.data?.error || 'Failed to parse job posting')
    } finally {
      setLoading(false)
    }
  }

  if (!isAuthenticated) {
    return (
      <div className="text-center">
        <h2>Please log in to parse job postings</h2>
      </div>
    )
  }

  return (
    <div>
      <div className="mb-4">
        <h2 className="text-2xl font-bold mb-2">Parse Job Posting</h2>
        <p className="text-gray-600">Paste a job posting URL to extract requirements and details</p>
      </div>

      <div className="card mb-4">
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="url" className="form-label">
              Job Posting URL
            </label>
            <input
              type="url"
              id="url"
              className="form-input"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://example.com/job-posting"
              required
              disabled={loading}
            />
          </div>

          <button
            type="submit"
            className="btn btn-primary"
            disabled={loading}
          >
            {loading ? 'Parsing...' : 'Parse Job Posting'}
          </button>
        </form>
      </div>

      {parseStatus && (
        <div className="alert alert-info">
          {parseStatus}
        </div>
      )}

      {error && (
        <div className="alert alert-error">
          {error}
        </div>
      )}

      {message && (
        <div className="alert alert-success">
          {message}
        </div>
      )}

      {jobData && (
        <div className="card">
          <div className="card-header">
            <h3 className="card-title">{jobData.title}</h3>
            {jobData.company && (
              <p className="text-gray-600">{jobData.company}</p>
            )}
          </div>

          <div className="mb-3">
            <h4 className="font-semibold mb-2">Job Description:</h4>
            <div className="text-gray-700 whitespace-pre-wrap max-h-60 overflow-y-auto">
              {jobData.description}
            </div>
          </div>

          {jobData.skills && jobData.skills.length > 0 && (
            <div className="mb-3">
              <h4 className="font-semibold mb-2">Skills:</h4>
              <div className="flex flex-wrap gap-1">
                {jobData.skills.map((skill, index) => (
                  <span 
                    key={index}
                    className="px-2 py-1 bg-blue-100 text-blue-800 text-sm rounded"
                  >
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          )}

          {jobData.requirements && jobData.requirements.length > 0 && (
            <div className="mb-3">
              <h4 className="font-semibold mb-2">Requirements:</h4>
              <ul className="list-disc list-inside space-y-1">
                {jobData.requirements.map((req, index) => (
                  <li key={index} className="text-sm text-gray-700">
                    {req}
                  </li>
                ))}
              </ul>
            </div>
          )}

          <div className="text-sm text-gray-500">
            Parsed: {new Date(jobData.created_at).toLocaleString()}
          </div>
        </div>
      )}
    </div>
  )
}

export default JobLink
