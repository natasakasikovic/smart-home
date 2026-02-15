import React from 'react';
import { updatePersonCount } from '../api';

export default function PersonCounter({ currentCount }) {
  const handleReset = async () => {
    try {
      await updatePersonCount('set', 0);
      console.log('✅ Person count reset to 0');
    } catch (error) {
      console.error('❌ Failed to reset:', error);
    }
  };

  return (
    <div className="bg-gray-800 p-4 rounded-lg flex items-center justify-between">
      <div>
        <p className="text-gray-400 text-sm">People Inside</p>
        <p className="text-3xl font-bold text-cyan-400">{currentCount}</p>
      </div>
      <button
        onClick={handleReset}
        className="bg-red-600 hover:bg-red-700 px-6 py-2 rounded font-bold"
      >
        Reset to 0
      </button>
    </div>
  );
}