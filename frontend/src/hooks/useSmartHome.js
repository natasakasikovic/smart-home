import { useState, useEffect } from 'react';
import { io } from 'socket.io-client';
import { getState } from '../api';

export const useSmartHome = () => {
  const [state, setState] = useState({
    sensors: {},
    actuators: {},
    alarm_active: false,
    security_armed: false,
    person_count: 0,
  });
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    getState()
      .then(res => setState(res.data))
      .catch(err => console.error('Failed to fetch state:', err));

    const socket = io('http://localhost:5000');

    socket.on('connect', () => {
      console.log('✅ WebSocket connected');
      setConnected(true);
    });

    socket.on('state', (data) => {
      setState(data);
    });

    socket.on('update', () => {
      getState().then(res => setState(res.data));
    });

    socket.on('disconnect', () => {
      console.log('❌ WebSocket disconnected');
      setConnected(false);
    });

    return () => socket.disconnect();
  }, []);

  return { state, connected };
};