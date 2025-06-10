// src/api.js
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:5000',
  withCredentials: true  // crucial for cookies/session
});


export const logout = async () => {
  return await api.post('/logout');
};


export default api;
