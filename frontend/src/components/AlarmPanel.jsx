import React, { useState, useEffect } from 'react';
import { armAlarm, disarmAlarm } from '../api';

export default function AlarmPanel({ state, socket }) {
  const [pin, setPin] = useState('');
  const [armPin, setArmPin] = useState('');
  const [error, setError] = useState('');
  const [countdown, setCountdown] = useState(0);

  useEffect(() => {
    if (!socket) return;

    socket.on('arming', ({ countdown: c }) => {
      setCountdown(c);
    });

    return () => socket.off('arming');
  }, [socket]);

  useEffect(() => {
    if (countdown <= 0) return;
    const interval = setInterval(() => {
      setCountdown(prev => {
        if (prev <= 1) {
          clearInterval(interval);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
    return () => clearInterval(interval);
  }, [countdown]);

  const isArming = countdown > 0;

  const handleArm = async () => {
    if (armPin.length !== 4) {
      setError('❌ PIN has to be 4 digits');
      return;
    }
    try {
      await armAlarm(armPin);
      setArmPin('');
      setError('');
    } catch (err) {
      setError(err.response?.data?.error || '❌ Failed to arm');
    }
  };

  const handleDisarm = async () => {
    if (pin.length !== 4) {
      setError('❌ PIN has to be 4 digits');
      return;
    }
    try {
      await disarmAlarm(pin);
      setPin('');
      setError('');
      setCountdown(0);
    } catch (err) {
      setError('❌ Wrong PIN');
    }
  };

  const getStatusLabel = () => {
    if (state.alarm_active) return { label: '🚨 ALARM ACTIVE', cls: 'text-red-500 animate-pulse' };
    if (state.security_armed) return { label: '🔴 ARMED', cls: 'text-red-400 font-bold' };
    if (isArming) return { label: `⏳ ARMING... ${countdown}s`, cls: 'text-yellow-400 animate-pulse' };
    return { label: '🟢 DISARMED', cls: 'text-green-400 font-bold' };
  };

  const { label, cls } = getStatusLabel();

  return (
    <div className={`bg-gray-800 p-6 rounded-lg border-2 mb-8 ${state.alarm_active ? 'border-red-500' : state.security_armed ? 'border-orange-500' : 'border-gray-600'}`}>
      <h2 className="text-2xl font-bold mb-4">🚨 Alarm System</h2>

      <div className={`mb-4 text-lg font-bold ${cls}`}>{label}</div>

      {state.alarm_active && (
        <div className="mb-4 p-3 bg-red-900 rounded text-red-200 text-sm">
          Alarm is active! Enter PIN to disarm the system.
        </div>
      )}

      {isArming && (
        <div className="mb-4 p-3 bg-yellow-900 rounded text-yellow-200 text-sm">
          <div className="flex justify-between mb-2">
            <span>⏳ System arming...</span>
            <span className="font-bold">{countdown}s</span>
          </div>
          <div className="w-full bg-yellow-800 rounded-full h-2">
            <div
              className="bg-yellow-400 h-2 rounded-full transition-all duration-1000"
              style={{ width: `${(countdown / 10) * 100}%` }}
            />
          </div>
          <div className="mt-2 text-xs text-yellow-300">Enter PIN to cancel arming</div>
        </div>
      )}

      <div className="flex gap-4 flex-wrap">
        {/* ARM */}
        <div className="flex gap-2">
          <input
            type="password"
            placeholder="PIN (4 digits)"
            value={armPin}
            onChange={(e) => setArmPin(e.target.value.replace(/\D/, '').slice(0, 4))}
            className="bg-gray-700 px-4 py-3 rounded text-white w-36"
            maxLength={4}
          />
          <button
            onClick={handleArm}
            disabled={state.security_armed || state.alarm_active || isArming}
            className="bg-orange-600 hover:bg-orange-700 disabled:bg-gray-600 disabled:cursor-not-allowed px-6 py-3 rounded font-bold"
          >
            ARM
          </button>
        </div>

        {/* DISARM */}
        <div className="flex gap-2">
          <input
            type="password"
            placeholder="PIN (4 digits)"
            value={pin}
            onChange={(e) => setPin(e.target.value.replace(/\D/, '').slice(0, 4))}
            className="bg-gray-700 px-4 py-3 rounded text-white w-36"
            maxLength={4}
          />
          <button
            onClick={handleDisarm}
            disabled={!state.security_armed && !state.alarm_active && !isArming}
            className="bg-green-600 hover:bg-green-700 disabled:bg-gray-600 disabled:cursor-not-allowed px-6 py-3 rounded font-bold"
          >
            DISARM
          </button>
        </div>
      </div>

      {error && <p className="text-red-400 mt-3 font-bold">{error}</p>}
    </div>
  );
}