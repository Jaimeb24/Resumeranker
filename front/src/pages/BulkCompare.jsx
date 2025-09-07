import React, { useState, useEffect } from 'react'
import { useAuth } from '../context/AuthContext'
import { resumesAPI, jobsAPI, matchAPI } from '../api/client'
import { useSockets } from '../hooks/useSockets'
import MatchSummary from '../components/MatchSummary'

const BulkCompare = () => {
  const [resumes, setResumes] = useState([])
  const [jobs, setJobs] = useState([])
  const [selectedResumes, setSelectedResumes] = useState([])
  const [selectedJob, setSelectedJob] = useState('')
  const [customJobData, setCustomJobData] = useState('')
  const [useCustomJob, setUseCustomJob] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')
  const [bulkResults, setBulkResults] = useState(null)
  const [progress, setProgress] = useState(null)
  
  const { isAuthenticated } = useAuth()
  const { onBulkMatchProgress, onBulkMatchFinished } = useSockets()

  useEffect(() => {
    if (isAuthenticated) {
      fetchData()
    }
  }, [isAuthenticated])

  useEffect(() => {
    if (!isAuthenticated) return

    // Set up socket listeners for bulk matching
    onBulkMatchProgress((data) => {
      setProgress({
        current: data.current,
        total: data.total,
        resumeName: data.resume_name,
        message: data.message
      })
    })

    onBulkMatchFinished((data) => {
      setProgress(null)
      if (data.success) {
        setBulkResults(data.results)
        setMessage(data.message)
        setError('')
      } else {
        setError(data.message)
        setMessage('')
      }
    })

    return () => {
      // Cleanup listeners
    }
  }, [isAuthenticated, onBulkMatchProgress, onBulkMatchFinished])

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

  const handleResumeToggle = (resumeId) => {
    setSelectedResumes(prev => 
      prev.includes(resumeId) 
        ? prev.filter(id => id !== resumeId)
        : [...prev, resumeId]
    )
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setMessage('')
    setBulkResults(null)
    setProgress(null)

    if (selectedResumes.length === 0) {
      setError('Please select at least one resume')
      return
    }

    if (!useCustomJob && !selectedJob) {
      setError('Please select a job posting or enter custom job data')
      return
    }

    if (useCustomJob && !customJobData.trim()) {
      setError('Please enter custom job data')
      return
    }

    setLoading(true)

    try {
      const matchData = {
        resumeIds: selectedResumes,
        jobPostingId: useCustomJob ? null : selectedJob,
        jobData: useCustomJob ? JSON.parse(customJobData) : null
      }

      const response = await matchAPI.bulkMatch(matchData)
      setBulkResults(response.data.results)
      setMessage(response.data.message)
    } catch (error) {
      if (error.response?.data?.error?.includes('JSON')) {
        setError('Invalid JSON format for custom job data')
      } else {
        setError(error.response?.data?.error || 'Failed to perform bulk matching')
      }
    } finally {
      setLoading(false)
    }
  }

  if (!isAuthenticated) {
    return (
      <div className="text-center">
        <h2>Please log in to compare multiple resumes</h2>
      </div>
    )
  }

  return (
    <div>
      <div className="mb-4">
        <h2 className="text-2xl font-bold mb-2">Bulk Resume Comparison</h2>
        <p className="text-gray-600">Compare multiple resumes against a job posting simultaneously</p>
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

      {progress && (
        <div className="alert alert-info">
          <div className="flex items-center gap-2">
            <div className="spinner"></div>
            <div>
              <p>{progress.message}</p>
              <p className="text-sm">Progress: {progress.current}/{progress.total}</p>
            </div>
          </div>
        </div>
      )}

      <div className="grid grid-2 gap-4 mb-4">
        {/* Resume Selection */}
        <div className="card">
          <h3 className="card-title mb-3">Select Resumes ({selectedResumes.length} selected)</h3>
          
          <div className="max-h-60 overflow-y-auto">
            {resumes.map(resume => (
              <div key={resume.id} className="flex items-center gap-2 mb-2 p-2 border rounded">
                <input
                  type="checkbox"
                  checked={selectedResumes.includes(resume.id)}
                  onChange={() => handleResumeToggle(resume.id)}
                  disabled={loading}
                />
                <div className="flex-1">
                  <p className="font-medium">{resume.filename}</p>
                  <p className="text-sm text-gray-500">
                    {resume.text ? resume.text.length : 0} characters
                  </p>
                </div>
              </div>
            ))}
          </div>
          
          {resumes.length === 0 && (
            <p className="text-gray-500 text-center py-4">
              No resumes uploaded yet. Upload some resumes first.
            </p>
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
          disabled={loading || selectedResumes.length === 0}
        >
          {loading ? 'Comparing...' : `Compare ${selectedResumes.length} Resume${selectedResumes.length !== 1 ? 's' : ''}`}
        </button>
      </div>

      {bulkResults && (
        <div className="space-y-4">
          <h3 className="text-xl font-semibold">Comparison Results</h3>
          {bulkResults.map((result, index) => (
            <div key={index} className="card">
              <h4 className="font-semibold mb-2">{result.resume_name}</h4>
              <MatchSummary matchResult={result.match_result} />
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default BulkCompare
