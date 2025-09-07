import React from 'react'

const ResumeCard = ({ resume, onDelete }) => {
  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString()
  }

  const getFileSize = (text) => {
    if (!text) return 'Unknown'
    const sizeInKB = Math.round(text.length / 1024)
    return `${sizeInKB} KB`
  }

  return (
    <div className="card">
      <div className="card-header">
        <h3 className="card-title">{resume.filename}</h3>
        <p className="text-sm text-gray-600">
          Uploaded: {formatDate(resume.created_at)}
        </p>
      </div>
      
      <div className="mb-2">
        <p className="text-sm">
          <strong>File Size:</strong> {getFileSize(resume.text)}
        </p>
        <p className="text-sm">
          <strong>Text Length:</strong> {resume.text ? resume.text.length : 0} characters
        </p>
      </div>
      
      {resume.text && (
        <div className="mb-2">
          <p className="text-sm">
            <strong>Preview:</strong>
          </p>
          <p className="text-sm text-gray-600">
            {resume.text.substring(0, 200)}...
          </p>
        </div>
      )}
      
      <div className="flex gap-2">
        <button
          onClick={() => onDelete(resume.id)}
          className="btn btn-danger"
        >
          Delete
        </button>
      </div>
    </div>
  )
}

export default ResumeCard
