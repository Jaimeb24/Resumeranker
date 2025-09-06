import React, { useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

const ForgotPassword = () => {
  const [email, setEmail] = useState('')
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  
  const { requestPasswordReset } = useAuth()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setMessage('')
    setLoading(true)

    const result = await requestPasswordReset(email)
    
    if (result.success) {
      setMessage('If the email exists, a password reset link has been sent.')
    } else {
      setError(result.error)
    }
    
    setLoading(false)
  }

  return (
    <div className="max-w-md mx-auto">
      <div className="card">
        <div className="card-header text-center">
          <h2 className="card-title">Reset Password</h2>
          <p className="text-gray-600">Enter your email to request a password reset</p>
        </div>

        {error && (
          <div className="alert alert-error">
            {error}
          </div>
        )}

        {message && (
          <div className="alert alert-info">
            {message}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="email" className="form-label">
              Email Address
            </label>
            <input
              type="email"
              id="email"
              className="form-input"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              disabled={loading}
            />
          </div>

          <button
            type="submit"
            className="btn btn-primary w-full"
            disabled={loading}
          >
            {loading ? 'Sending...' : 'Send Reset Link'}
          </button>
        </form>

        <div className="text-center mt-3">
          <p className="text-sm text-gray-600">
            Remember your password?{' '}
            <Link to="/login" className="text-blue-600 hover:underline">
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}

export default ForgotPassword
