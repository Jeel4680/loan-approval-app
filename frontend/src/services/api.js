import axios from 'axios';

// Base URL — points to our FastAPI backend
const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({ baseURL: API_BASE });

// Automatically attach JWT token to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Auth
export const register = (data) => api.post('/auth/register', data);
export const login = (data) => api.post('/auth/login', data);
export const getMe = () => api.get('/auth/me');

// Loans
export const applyForLoan = (data) => api.post('/loans/apply', data);
export const getMyApplications = () => api.get('/loans/my-applications');
export const getApplicationDetails = (id) => api.get(`/loans/application/${id}`);

// Decisions
export const evaluateLoan = (id) => api.post(`/decisions/evaluate/${id}`);
export const getDecision = (id) => api.get(`/decisions/result/${id}`);
export const mlEvaluate = (id) => api.post(`/decisions/ml-evaluate/${id}`);

export default api;
