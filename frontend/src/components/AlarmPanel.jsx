import React, { useState } from 'react';
import { armAlarm, disarmAlarm } from '../api';

export default function AlarmPanel({ state }) {
  const [pin, setPin] = useState('');
  const [error, setError] = useState('');

  const handleArm = async () => {
    try {
      await armAlarm();
      setError('');
    } catch (err) {
      setError('Failed to arm');
    }
  };

  const handleDisarm = async () => {
    try {
      await disarmAlarm(pin);
      setPin('');
      setError('');
    } catch (err) {
      setError('❌ Wrong PIN');
    }
  };

  return (
    <div className="bg-gray-800 p-6 rounded-lg border-2 border-red-600 mb-8">
      <h2 className="text-2xl font-bold mb-4">🚨 Alarm System</h2>

      <div className="flex gap-4">
        <button
          onClick={handleArm}
          disabled={state.security_armed}
          className="bg-orange-600 hover:bg-orange-700 disabled:bg-gray-600 px-6 py-3 rounded font-bold"
        >
          ARM SYSTEM
        </button>
        
        <div className="flex gap-2">
          <input
            type="password"
            placeholder="PIN (1234)"
            value={pin}
            onChange={(e) => setPin(e.target.value)}
            className="bg-gray-700 px-4 py-3 rounded text-white"
            maxLength={4}
          />
          <button
            onClick={handleDisarm}
            className="bg-green-600 hover:bg-green-700 px-6 py-3 rounded font-bold"
          >
            DISARM
          </button>
        </div>
      </div>

      {error && <p className="text-red-500 mt-2 font-bold">{error}</p>}
    </div>
  );
}