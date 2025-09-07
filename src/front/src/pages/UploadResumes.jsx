import React, { useState, useEffect } from 'react'
import { useAuth } from '../context/AuthContext'
import { resumesAPI } from '../api/client'
import ResumeCard from '../components/ResumeCard'

const UploadResumes = () => {
  const [resumes, setResumes] = useState([])
  const [loading, setLoading] = useState(true)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')
  const { isAuthenticated } = useAuth()

  useEffect(() => {
    if (isAuthenticated) {
      fetchResumes()
    }
  }, [isAuthenticated])

  const fetchResumes = async () => {
    try {
      const response = await resumesAPI.list()
      setResumes(response.data.resumes)
    } catch (error) {
      setError('Failed to fetch resumes')
    } finally {
      setLoading(false)
    }
  }

  const handleFileUpload = async (e) => {
    const file = e.target.files[0]
    if (!file) return

    // Validate file type
    const allowedTypes = ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
    if (!allowedTypes.includes(file.type)) {
      setError('Please upload a PDF, DOC, or DOCX file')
      return
    }

    // Validate file size (5MB)
    if (file.size > 5 * 1024 * 1024) {
      setError('File size must be less than 5MB')
      return
    }

    setUploading(true)
    setError('')
    setMessage('')

    try {
      const response = await resumesAPI.upload(file)
      setResumes([response.data.resume, ...resumes])
      setMessage('Resume uploaded successfully!')
      e.target.value = '' // Clear the input
    } catch (error) {
      setError(error.response?.data?.error || 'Failed to upload resume')
    } finally {
      setUploading(false)
    }
  }

  const handleDelete = async (resumeId) => {
    if (!window.confirm('Are you sure you want to delete this resume?')) {
      return
    }

    try {
      await resumesAPI.delete(resumeId)
      setResumes(resumes.filter(r => r.id !== resumeId))
      setMessage('Resume deleted successfully!')
    } catch (error) {
      setError(error.response?.data?.error || 'Failed to delete resume')
    }
  }

  if (!isAuthenticated) {
    return (
      <div className="text-center">
        <h2>Please log in to manage your resumes</h2>
      </div>
    )
  }

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
      </div>
    )
  }

  return (
    <div>
      <div className="mb-4">
        <h2 className="text-2xl font-bold mb-2">My Resumes</h2>
        <p className="text-gray-600">Upload and manage your resume files</p>
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

      <div className="card mb-4">
        <h3 className="card-title mb-2">Upload New Resume</h3>
        <p className="text-gray-600 mb-3">
          Supported formats: PDF, DOC, DOCX (max 5MB)
        </p>
        
        <div className="form-group">
          <input
            type="file"
            accept=".pdf,.doc,.docx"
            onChange={handleFileUpload}
            disabled={uploading}
            className="form-input"
          />
        </div>
        
        {uploading && (
          <div className="flex items-center gap-2">
            <div className="spinner"></div>
            <span>Uploading and processing resume...</span>
          </div>
        )}
      </div>

      <div>
        <h3 className="text-xl font-semibold mb-3">
          Your Resumes ({resumes.length})
        </h3>
        
        {resumes.length === 0 ? (
          <div className="card text-center">
            <p className="text-gray-600">No resumes uploaded yet.</p>
            <p className="text-sm text-gray-500 mt-1">
              Upload your first resume using the form above.
            </p>
          </div>
        ) : (
          <div className="grid grid-2">
            {resumes.map(resume => (
              <ResumeCard
                key={resume.id}
                resume={resume}
                onDelete={handleDelete}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default UploadResumes
