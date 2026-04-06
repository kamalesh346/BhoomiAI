import axios from 'axios';

const API_URL = 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const login = (email, password) => api.post('/auth/login', { email, password });
export const register = (data) => api.post('/auth/register', data);
export const updateProfile = (farmer_id, data) => api.put(`/auth/profile/${farmer_id}`, data);

export const getPestHistory = (farmer_id) => api.get(`/auth/pest-history/${farmer_id}`);
export const addPestHistory = (farmer_id, data) => api.post(`/auth/pest-history/${farmer_id}`, data);

export const startChat = (farmer_id, language = "en") => api.post('/chat/start', { farmer_id, language });
export const sendChatMessage = (farmer_id, chat_session_id, message, language = "en") => 
  api.post('/chat/message', { farmer_id, chat_session_id, message, language });
export const sendChatChoice = (farmer_id, chat_session_id, message_id, selected_option, language = "en") => 
  api.post('/chat/choice', { farmer_id, chat_session_id, message_id, selected_option, language });

export const getChatHistory = (session_id, language = "en") => api.get(`/chat/history/${session_id}`, { params: { language } });

export const getFarmHistory = (farmer_id) => api.get(`/recommendations/history/${farmer_id}`);
export const addFarmHistory = (data) => api.post('/recommendations/history', data);
