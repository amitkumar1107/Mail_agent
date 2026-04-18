import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || (import.meta.env.PROD ? '/api' : 'http://localhost:8000/api')

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Add token to requests
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export const authService = {
  login: (username, password) =>
    apiClient.post('/auth/login/', { username, password }),
  signup: (email, username, password) =>
    apiClient.post('/auth/signup/', { email, username, password }),
  requestOtp: (email) =>
    apiClient.post('/auth/otp/request/', { email }),
  verifyOtp: (email, code) =>
    apiClient.post('/auth/otp/verify/', { email, code }),
}

export const mailService = {
  parseCommand: (commandText) =>
    apiClient.post('/mail/commands/parse/', { command_text: commandText }),
  generatePreview: (commandText) =>
    apiClient.post('/mail/drafts/preview/', { command_text: commandText }),
  confirmDraft: (draftId, action, subject = null, body = null) =>
    apiClient.post('/mail/drafts/confirm/', { draft_id: draftId, action, subject, body }),
  getDashboard: () =>
    apiClient.get('/mail/insights/dashboard/'),
}

export const contactsService = {
  getContacts: () =>
    apiClient.get('/contacts/'),
  createContact: (data) =>
    apiClient.post('/contacts/', data),
}

export const remindersService = {
  getReminders: () =>
    apiClient.get('/reminders/'),
  createReminder: (data) =>
    apiClient.post('/reminders/', data),
}

export const voiceService = {
  transcribe: (audioFile) => {
    const formData = new FormData()
    formData.append('audio', audioFile)
    return apiClient.post('/voice/transcribe/', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
}

export default apiClient
