import axios from 'axios'

const client = axios.create({
  // In production (Vercel), set VITE_API_URL to your Render backend URL.
  // In development, Vite proxies /api to localhost:8000.
  baseURL: import.meta.env.VITE_API_URL ? `${import.meta.env.VITE_API_URL}/api` : '/api',
  headers: { 'Content-Type': 'application/json' },
})

// Attach JWT from localStorage on every request
client.interceptors.request.use((config) => {
  const token = localStorage.getItem('medichat_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// On 401 — clear token and redirect to login
client.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('medichat_token')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

export default client
