import React, { useState } from 'react';
import { armAlarm, disarmAlarm } from '../api';

export default function AlarmPanel({ state }) {
  const [pin, setPin] = useState('');
  const [armPin, setArmPin] = useState('');
  const [error, setError] = useState('');
  const [arming, setArming] = useState(false); // countdown in progress

  const handleArm = async () => {
    if (armPin.length !== 4) {
      setError('❌ PIN mora biti 4 cifre');
      return;
    }
    try {
      await armAlarm(armPin);
      setArmPin('');
      setError('');
      setArming(true);
      setTimeout(() => setArming(false), 10000);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to arm');
    }
  };

  const handleDisarm = async () => {
    try {
      await disarmAlarm(pin);
      setPin('');
      setError('');
      setArming(false);
    } catch (err) {
      setError('❌ WRONG PIN');
    }
  };

  return (
    <div className="bg-gray-800 p-6 rounded-lg border-2 border-red-600 mb-8">
      <h2 className="text-2xl font-bold mb-4">🚨 Alarm System</h2>

      {arming && (
        <div className="mb-4 text-yellow-400 font-bold animate-pulse">
          ⏳ System is arming in 10 seconds...
        </div>
      )}

      <div className="flex gap-4 flex-wrap">
        {/* ARM section */}
        <div className="flex gap-2">
          <input
            type="password"
            placeholder="Activation PIN"
            value={armPin}
            onChange={(e) => setArmPin(e.target.value)}
            className="bg-gray-700 px-4 py-3 rounded text-white w-40"
            maxLength={4}
          />
          <button
            onClick={handleArm}
            disabled={state.security_armed || arming}
            className="bg-orange-600 hover:bg-orange-700 disabled:bg-gray-600 px-6 py-3 rounded font-bold"
          >
            ARM SYSTEM
          </button>
        </div>

        {/* DISARM section */}
        <div className="flex gap-2">
          <input
            type="password"
            placeholder="Deactivation PIN"
            value={pin}
            onChange={(e) => setPin(e.target.value)}
            className="bg-gray-700 px-4 py-3 rounded text-white w-40"
            maxLength={4}
          />
          <button
            onClick={handleDisarm}
            disabled={!state.security_armed && !arming}
            className="bg-green-600 hover:bg-green-700 disabled:bg-gray-600 px-6 py-3 rounded font-bold"
          >
            DISARM
          </button>
        </div>
      </div>

      {error && <p className="text-red-500 mt-2 font-bold">{error}</p>}

      <div className="mt-3 text-sm text-gray-400">
        Status:{' '}
        <span className={state.security_armed ? 'text-red-400 font-bold' : 'text-green-400 font-bold'}>
          {state.security_armed ? 'ARMED' : arming ? 'ARMING...' : 'DISARMED'}
        </span>
      </div>
    </div>
  );
}
