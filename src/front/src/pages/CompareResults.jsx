import React, { useState, useEffect } from 'react'
import { useAuth } from '../context/AuthContext'
import { resumesAPI, jobsAPI, matchAPI } from '../api/client'
import { useSockets } from '../hooks/useSockets'
import MatchSummary from '../components/MatchSummary'

const CompareResults = () => {
  const [resumes, setResumes] = useState([])
  const [jobs, setJobs] = useState([])
  const [selectedResume, setSelectedResume] = useState('')
  const [selectedJob, setSelectedJob] = useState('')
  const [customResumeText, setCustomResumeText] = useState('')
  const [customJobData, setCustomJobData] = useState('')
  const [useCustomResume, setUseCustomResume] = useState(false)
  const [useCustomJob, setUseCustomJob] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')
  const [matchResult, setMatchResult] = useState(null)
  const [matchStatus, setMatchStatus] = useState('')
  
  const { isAuthenticated } = useAuth()
  const { onMatchFinished } = useSockets()

  useEffect(() => {
    if (isAuthenticated) {
      fetchData()
    }
  }, [isAuthenticated])

  useEffect(() => {
    if (!isAuthenticated) return

    // Set up socket listener for match completion
    onMatchFinished((data) => {
      if (data.success) {
        setMatchResult(data.match_result)
        setMatchStatus('')
        setMessage('Resume matching completed successfully!')
        setError('')
      } else {
        setMatchStatus('')
        setError(data.message || 'Failed to match resume')
      }
    })

    return () => {
      // Cleanup listeners
    }
  }, [isAuthenticated, onMatchFinished])

  const fetchData = async () => {
    try {
      const [resumesResponse, jobsResponse] = await Promise.all([
        resumesAPI.list(),
        jobsAPI.list()
      ])
      setResumes(resumesResponse.data.resumes)
      setJobs(jobsResponse.data.job_postings)
    } catch (error) {
      setError('Failed to fetch data')
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setMessage('')
    setMatchResult(null)
    setMatchStatus('')

    // Validate inputs
    if (!useCustomResume && !selectedResume) {
      setError('Please select a resume or enter custom resume text')
      return
    }

    if (!useCustomJob && !selectedJob) {
      setError('Please select a job posting or enter custom job data')
      return
    }

    if (useCustomResume && !customResumeText.trim()) {
      setError('Please enter custom resume text')
      return
    }

    if (useCustomJob && !customJobData.trim()) {
      setError('Please enter custom job data')
      return
    }

    setLoading(true)

    try {
      const matchData = {
        resumeId: useCustomResume ? null : selectedResume,
        resumeText: useCustomResume ? customResumeText : null,
        jobPostingId: useCustomJob ? null : selectedJob,
        jobData: useCustomJob ? JSON.parse(customJobData) : null
      }

      const response = await matchAPI.match(matchData)
      setMatchResult(response.data.match_result)
      setMessage('Resume matching completed successfully!')
    } catch (error) {
      if (error.response?.data?.error?.includes('JSON')) {
        setError('Invalid JSON format for custom job data')
      } else {
        setError(error.response?.data?.error || 'Failed to match resume')
      }
    } finally {
      setLoading(false)
    }
  }

  if (!isAuthenticated) {
    return (
      <div className="text-center">
        <h2>Please log in to compare resumes</h2>
      </div>
    )
  }

  return (
    <div>
      <div className="mb-4">
        <h2 className="text-2xl font-bold mb-2">Compare Resume vs Job</h2>
        <p className="text-gray-600">Get AI-powered analysis of how well your resume matches job requirements</p>
      </div>

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

      {matchStatus && (
        <div className="alert alert-info">
          {matchStatus}
        </div>
      )}

      <div className="grid grid-2 gap-4 mb-4">
        {/* Resume Selection */}
        <div className="card">
          <h3 className="card-title mb-3">Select Resume</h3>
          
          <div className="form-group">
            <label className="flex items-center gap-2">
              <input
                type="radio"
                checked={!useCustomResume}
                onChange={() => setUseCustomResume(false)}
              />
              Use uploaded resume
            </label>
          </div>

          {!useCustomResume && (
            <div className="form-group">
              <label className="form-label">Choose Resume:</label>
              <select
                className="form-input"
                value={selectedResume}
                onChange={(e) => setSelectedResume(e.target.value)}
                disabled={loading}
              >
                <option value="">Select a resume...</option>
                {resumes.map(resume => (
                  <option key={resume.id} value={resume.id}>
                    {resume.filename}
                  </option>
                ))}
              </select>
            </div>
          )}

          <div className="form-group">
            <label className="flex items-center gap-2">
              <input
                type="radio"
                checked={useCustomResume}
                onChange={() => setUseCustomResume(true)}
              />
              Use custom resume text
            </label>
          </div>

          {useCustomResume && (
            <div className="form-group">
              <label className="form-label">Resume Text:</label>
              <textarea
                className="form-textarea"
                value={customResumeText}
                onChange={(e) => setCustomResumeText(e.target.value)}
                placeholder="Paste your resume text here..."
                disabled={loading}
              />
            </div>
          )}
        </div>

        {/* Job Selection */}
        <div className="card">
          <h3 className="card-title mb-3">Select Job Posting</h3>
          
          <div className="form-group">
            <label className="flex items-center gap-2">
              <input
                type="radio"
                checked={!useCustomJob}
                onChange={() => setUseCustomJob(false)}
              />
              Use parsed job posting
            </label>
          </div>

          {!useCustomJob && (
            <div className="form-group">
              <label className="form-label">Choose Job:</label>
              <select
                className="form-input"
                value={selectedJob}
                onChange={(e) => setSelectedJob(e.target.value)}
                disabled={loading}
              >
                <option value="">Select a job posting...</option>
                {jobs.map(job => (
                  <option key={job.id} value={job.id}>
                    {job.title} - {job.company || 'Unknown Company'}
                  </option>
                ))}
              </select>
            </div>
          )}

          <div className="form-group">
            <label className="flex items-center gap-2">
              <input
                type="radio"
                checked={useCustomJob}
                onChange={() => setUseCustomJob(true)}
              />
              Use custom job data
            </label>
          </div>

          {useCustomJob && (
            <div className="form-group">
              <label className="form-label">Job Data (JSON):</label>
              <textarea
                className="form-textarea"
                value={customJobData}
                onChange={(e) => setCustomJobData(e.target.value)}
                placeholder='{"title": "Job Title", "description": "Job description...", "skills": ["skill1", "skill2"], "requirements": ["req1", "req2"]}'
                disabled={loading}
              />
            </div>
          )}
        </div>
      </div>

      <div className="text-center mb-4">
        <button
          onClick={handleSubmit}
          className="btn btn-primary"
          disabled={loading}
        >
          {loading ? 'Analyzing...' : 'Compare Resume vs Job'}
        </button>
      </div>

      {matchResult && (
        <MatchSummary matchResult={matchResult} />
      )}
    </div>
  )
}

export default CompareResults
