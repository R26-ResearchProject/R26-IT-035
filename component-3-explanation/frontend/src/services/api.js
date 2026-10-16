import axios from "axios"

const API_BASE = "http://127.0.0.1:8000"

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    "Content-Type": "application/json"
  }
})

// Add this — logs exact error from backend
api.interceptors.response.use(
  response => response,
  error => {
    console.log("API Error details:", error.response?.data)
    return Promise.reject(error)
  }
)

export default api