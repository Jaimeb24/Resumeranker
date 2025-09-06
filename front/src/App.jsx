import React from 'react'
import { Routes, Route } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import Header from './components/Header'
import Home from './pages/Home'
import Login from './pages/Login'
import Signup from './pages/Signup'
import ForgotPassword from './pages/ForgotPassword'
import UploadResumes from './pages/UploadResumes'
import JobLink from './pages/JobLink'
import CompareResults from './pages/CompareResults'
import BulkCompare from './pages/BulkCompare'

function App() {
  return (
    <AuthProvider>
      <div className="App">
        <Header />
        <main className="container">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/login" element={<Login />} />
            <Route path="/signup" element={<Signup />} />
            <Route path="/forgot" element={<ForgotPassword />} />
            <Route path="/resumes" element={<UploadResumes />} />
            <Route path="/job" element={<JobLink />} />
            <Route path="/compare" element={<CompareResults />} />
            <Route path="/bulk" element={<BulkCompare />} />
          </Routes>
        </main>
      </div>
    </AuthProvider>
  )
}

export default App