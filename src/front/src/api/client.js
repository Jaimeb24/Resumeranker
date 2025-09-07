import axios from 'axios'

// Create axios instance
const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor to handle errors
api.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// API methods
export const authAPI = {
  signup: (data) => api.post('/auth/signup', data),
  login: (data) => api.post('/auth/login', data),
  requestPasswordReset: (data) => api.post('/auth/request-password-reset', data),
  resetPassword: (data) => api.post('/auth/reset-password', data),
}

export const resumesAPI = {
  upload: (file) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/resumes', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
  },
  list: () => api.get('/resumes'),
  get: (id) => api.get(`/resumes/${id}`),
  delete: (id) => api.delete(`/resumes/${id}`),
}

export const jobsAPI = {
  parse: (data) => api.post('/jobs/parse', data),
  list: () => api.get('/jobs'),
  get: (id) => api.get(`/jobs/${id}`),
}

export const matchAPI = {
  match: (data) => api.post('/match', data),
  bulkMatch: (data) => api.post('/match/bulk', data),
  history: () => api.get('/match/history'),
  get: (id) => api.get(`/match/${id}`),
}

export default api
