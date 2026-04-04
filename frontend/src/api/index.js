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

export const startChat = (farmer_id) => api.post('/chat/start', { farmer_id });
export const sendChatMessage = (farmer_id, chat_session_id, message) => 
  api.post('/chat/message', { farmer_id, chat_session_id, message });
export const sendChatChoice = (farmer_id, chat_session_id, message_id, selected_option) =>
  api.post('/chat/choice', { farmer_id, chat_session_id, message_id, selected_option });

export const getChatHistory = (session_id) => api.get(`/chat/history/${session_id}`);
export const getFarmHistory = (farmer_id) => api.get(`/recommendations/history/${farmer_id}`);
export const addFarmHistory = (data) => api.post('/recommendations/history', data);
