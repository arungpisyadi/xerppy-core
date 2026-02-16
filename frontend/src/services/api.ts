import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig } from 'axios'

// Types
export interface User {
  id: string
  email: string
  role: string
  name: string
}

export interface ApiResponse<T> {
  success: boolean
  data?: T
  message?: string
}

export interface LoginCredentials {
  email: string
  password: string
}

export interface AuthTokens {
  accessToken: string
  refreshToken: string
}

// Create axios instance
const api: AxiosInstance = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor to add auth token
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = localStorage.getItem('accessToken')
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error: AxiosError) => {
    return Promise.reject(error)
  }
)

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config

    // Handle 401 Unauthorized
    if (error.response?.status === 401 && originalRequest) {
      // Try to refresh token
      const refreshToken = localStorage.getItem('refreshToken')
      if (refreshToken) {
        try {
          const response = await axios.post('/api/auth/refresh', { refreshToken })
          const { accessToken } = response.data
          localStorage.setItem('accessToken', accessToken)
          
          // Retry original request
          if (originalRequest.headers) {
            originalRequest.headers.Authorization = `Bearer ${accessToken}`
          }
          return api(originalRequest)
        } catch {
          // Refresh failed, clear tokens and redirect
          localStorage.removeItem('accessToken')
          localStorage.removeItem('refreshToken')
          window.location.href = '/login'
        }
      }
    }

    return Promise.reject(error)
  }
)

// Auth API
export const authApi = {
  login: async (credentials: LoginCredentials): Promise<ApiResponse<AuthTokens>> => {
    const response = await api.post('/auth/login', credentials)
    if (response.data.accessToken) {
      localStorage.setItem('accessToken', response.data.accessToken)
      localStorage.setItem('refreshToken', response.data.refreshToken)
    }
    return response.data
  },

  logout: async (): Promise<void> => {
    await api.post('/auth/logout')
    localStorage.removeItem('accessToken')
    localStorage.removeItem('refreshToken')
  },

  refreshToken: async (refreshToken: string): Promise<ApiResponse<AuthTokens>> => {
    const response = await api.post('/auth/refresh', { refreshToken })
    return response.data
  },
}

// User API
export const getCurrentUser = async (): Promise<ApiResponse<User>> => {
  const response = await api.get('/users/me')
  return response.data
}

export const updateUser = async (userData: Partial<User>): Promise<ApiResponse<User>> => {
  const response = await api.put('/users/me', userData)
  return response.data
}

export const updatePassword = async (
  currentPassword: string,
  newPassword: string
): Promise<ApiResponse<void>> => {
  const response = await api.post('/users/me/password', {
    currentPassword,
    newPassword,
  })
  return response.data
}

// Default export
export default api
