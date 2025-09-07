import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

const Header = () => {
  const { user, isAuthenticated, logout } = useAuth()
  const location = useLocation()

  const isActive = (path) => {
    return location.pathname === path
  }

  return (
    <header className="header">
      <div className="container">
        <div className="header-content">
          <Link to="/" className="logo">
            ResumeRanker
          </Link>
          
          <nav className="nav">
            {isAuthenticated ? (
              <>
                <Link 
                  to="/resumes" 
                  className={isActive('/resumes') ? 'active' : ''}
                >
                  My Resumes
                </Link>
                <Link 
                  to="/job" 
                  className={isActive('/job') ? 'active' : ''}
                >
                  Parse Job
                </Link>
                <Link 
                  to="/compare" 
                  className={isActive('/compare') ? 'active' : ''}
                >
                  Compare
                </Link>
                <Link 
                  to="/bulk" 
                  className={isActive('/bulk') ? 'active' : ''}
                >
                  Bulk Compare
                </Link>
                <span className="text-sm text-gray-600">
                  {user?.email}
                </span>
                <button 
                  onClick={logout}
                  className="btn btn-secondary"
                >
                  Logout
                </button>
              </>
            ) : (
              <>
                <Link 
                  to="/login" 
                  className={isActive('/login') ? 'active' : ''}
                >
                  Login
                </Link>
                <Link 
                  to="/signup" 
                  className={isActive('/signup') ? 'active' : ''}
                >
                  Sign Up
                </Link>
              </>
            )}
          </nav>
        </div>
      </div>
    </header>
  )
}

export default Header
