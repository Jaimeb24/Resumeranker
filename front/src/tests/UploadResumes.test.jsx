import React from 'react'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { AuthProvider } from '../context/AuthContext'
import UploadResumes from '../pages/UploadResumes'
import { resumesAPI } from '../api/client'

// Mock the API client
jest.mock('../api/client', () => ({
  resumesAPI: {
    list: jest.fn(),
    upload: jest.fn(),
    delete: jest.fn(),
  }
}))

// Mock the useAuth hook
const mockAuth = {
  isAuthenticated: true,
  user: { id: 1, email: 'test@example.com' }
}

jest.mock('../context/AuthContext', () => ({
  ...jest.requireActual('../context/AuthContext'),
  useAuth: () => mockAuth
}))

const renderWithProviders = (component) => {
  return render(
    <BrowserRouter>
      <AuthProvider>
        {component}
      </AuthProvider>
    </BrowserRouter>
  )
}

describe('UploadResumes', () => {
  beforeEach(() => {
    jest.clearAllMocks()
  })

  test('renders upload form and file input', async () => {
    resumesAPI.list.mockResolvedValue({
      data: { resumes: [] }
    })

    renderWithProviders(<UploadResumes />)

    await waitFor(() => {
      expect(screen.getByText('My Resumes')).toBeInTheDocument()
      expect(screen.getByText('Upload New Resume')).toBeInTheDocument()
      expect(screen.getByText('Supported formats: PDF, DOC, DOCX (max 5MB)')).toBeInTheDocument()
    })

    const fileInput = screen.getByRole('textbox', { name: /file/i })
    expect(fileInput).toBeInTheDocument()
  })

  test('displays uploaded resumes', async () => {
    const mockResumes = [
      {
        id: 1,
        filename: 'resume1.pdf',
        created_at: '2023-01-01T00:00:00Z',
        text: 'Sample resume text content...'
      },
      {
        id: 2,
        filename: 'resume2.docx',
        created_at: '2023-01-02T00:00:00Z',
        text: 'Another resume text content...'
      }
    ]

    resumesAPI.list.mockResolvedValue({
      data: { resumes: mockResumes }
    })

    renderWithProviders(<UploadResumes />)

    await waitFor(() => {
      expect(screen.getByText('resume1.pdf')).toBeInTheDocument()
      expect(screen.getByText('resume2.docx')).toBeInTheDocument()
    })

    expect(screen.getByText('Your Resumes (2)')).toBeInTheDocument()
  })

  test('handles file upload', async () => {
    resumesAPI.list.mockResolvedValue({
      data: { resumes: [] }
    })

    const mockFile = new File(['resume content'], 'resume.pdf', {
      type: 'application/pdf'
    })

    const mockUploadResponse = {
      data: {
        resume: {
          id: 1,
          filename: 'resume.pdf',
          created_at: '2023-01-01T00:00:00Z',
          text: 'resume content'
        }
      }
    }

    resumesAPI.upload.mockResolvedValue(mockUploadResponse)

    renderWithProviders(<UploadResumes />)

    await waitFor(() => {
      expect(screen.getByText('My Resumes')).toBeInTheDocument()
    })

    const fileInput = screen.getByRole('textbox', { name: /file/i })
    
    fireEvent.change(fileInput, {
      target: { files: [mockFile] }
    })

    await waitFor(() => {
      expect(resumesAPI.upload).toHaveBeenCalledWith(mockFile)
    })
  })

  test('handles delete resume', async () => {
    const mockResumes = [
      {
        id: 1,
        filename: 'resume1.pdf',
        created_at: '2023-01-01T00:00:00Z',
        text: 'Sample resume text content...'
      }
    ]

    resumesAPI.list.mockResolvedValue({
      data: { resumes: mockResumes }
    })

    resumesAPI.delete.mockResolvedValue({})

    // Mock window.confirm
    window.confirm = jest.fn(() => true)

    renderWithProviders(<UploadResumes />)

    await waitFor(() => {
      expect(screen.getByText('resume1.pdf')).toBeInTheDocument()
    })

    const deleteButton = screen.getByText('Delete')
    fireEvent.click(deleteButton)

    await waitFor(() => {
      expect(window.confirm).toHaveBeenCalledWith('Are you sure you want to delete this resume?')
      expect(resumesAPI.delete).toHaveBeenCalledWith(1)
    })
  })

  test('displays error message when upload fails', async () => {
    resumesAPI.list.mockResolvedValue({
      data: { resumes: [] }
    })

    resumesAPI.upload.mockRejectedValue({
      response: {
        data: { error: 'File too large' }
      }
    })

    const mockFile = new File(['resume content'], 'resume.pdf', {
      type: 'application/pdf'
    })

    renderWithProviders(<UploadResumes />)

    await waitFor(() => {
      expect(screen.getByText('My Resumes')).toBeInTheDocument()
    })

    const fileInput = screen.getByRole('textbox', { name: /file/i })
    
    fireEvent.change(fileInput, {
      target: { files: [mockFile] }
    })

    await waitFor(() => {
      expect(screen.getByText('File too large')).toBeInTheDocument()
    })
  })

  test('shows loading state during upload', async () => {
    resumesAPI.list.mockResolvedValue({
      data: { resumes: [] }
    })

    // Mock a slow upload
    resumesAPI.upload.mockImplementation(() => 
      new Promise(resolve => setTimeout(resolve, 100))
    )

    const mockFile = new File(['resume content'], 'resume.pdf', {
      type: 'application/pdf'
    })

    renderWithProviders(<UploadResumes />)

    await waitFor(() => {
      expect(screen.getByText('My Resumes')).toBeInTheDocument()
    })

    const fileInput = screen.getByRole('textbox', { name: /file/i })
    
    fireEvent.change(fileInput, {
      target: { files: [mockFile] }
    })

    // Should show loading state
    expect(screen.getByText('Uploading and processing resume...')).toBeInTheDocument()
  })

  test('validates file type', async () => {
    resumesAPI.list.mockResolvedValue({
      data: { resumes: [] }
    })

    const mockFile = new File(['content'], 'document.txt', {
      type: 'text/plain'
    })

    renderWithProviders(<UploadResumes />)

    await waitFor(() => {
      expect(screen.getByText('My Resumes')).toBeInTheDocument()
    })

    const fileInput = screen.getByRole('textbox', { name: /file/i })
    
    fireEvent.change(fileInput, {
      target: { files: [mockFile] }
    })

    await waitFor(() => {
      expect(screen.getByText('Please upload a PDF, DOC, or DOCX file')).toBeInTheDocument()
    })

    expect(resumesAPI.upload).not.toHaveBeenCalled()
  })
})
