import axios from 'axios';

const API_BASE = 'http://localhost:5000/api';

export const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const getState = () => api.get('/state');

export const controlActuator = (code, action, params = {}) => 
  api.post(`/actuator/${code}`, { action, params });

export const armAlarm = (pin) => api.post('/alarm/arm', { pin }, {
  headers: { 'Content-Type': 'application/json' }
});
export const disarmAlarm = (pin) => api.post('/alarm/disarm', { pin });

export const updatePersonCount = (action, value = 0) => 
  api.post('/person_count', { action, value });