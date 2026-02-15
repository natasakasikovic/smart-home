import React, { useState } from 'react';
import { controlActuator } from '../api';

export default function Actuators({ actuators }) {
  const [loading, setLoading] = useState({});

  const handleControl = async (code, action, params = {}) => {
    setLoading({ ...loading, [code]: true });
    try {
      await controlActuator(code, action, params);
      console.log(`✅ ${code}: ${action}`);
    } catch (error) {
      console.error('❌ Control error:', error);
    } finally {
      setTimeout(() => {
        setLoading({ ...loading, [code]: false });
      }, 500);
    }
  };

  return (
    <div className="mt-8">
      <h2 className="text-2xl font-bold mb-4">🎛️ Actuators</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        
        {/* Buzzer */}
        {actuators.DB && (
          <div className="bg-gray-800 p-6 rounded-lg">
            <h3 className="text-lg font-semibold mb-4">🔊 Door Buzzer</h3>
            <div className="flex gap-2">
              <button
                onClick={() => handleControl('DB', 'on')}
                className="flex-1 bg-green-600 hover:bg-green-700 px-4 py-2 rounded disabled:opacity-50"
                disabled={loading.DB}
              >
                ON
              </button>
              <button
                onClick={() => handleControl('DB', 'off')}
                className="flex-1 bg-red-600 hover:bg-red-700 px-4 py-2 rounded disabled:opacity-50"
                disabled={loading.DB}
              >
                OFF
              </button>
            </div>
          </div>
        )}

        {/* Door Light */}
        {actuators.DL && (
          <div className="bg-gray-800 p-6 rounded-lg">
            <h3 className="text-lg font-semibold mb-4">💡 Door Light</h3>
            <div className="flex gap-2">
              <button
                onClick={() => handleControl('DL', 'on')}
                className="flex-1 bg-green-600 hover:bg-green-700 px-4 py-2 rounded"
              >
                ON
              </button>
              <button
                onClick={() => handleControl('DL', 'off')}
                className="flex-1 bg-red-600 hover:bg-red-700 px-4 py-2 rounded"
              >
                OFF
              </button>
            </div>
          </div>
        )}

        {/* RGB */}
        {actuators.RGB && (
          <div className="bg-gray-800 p-6 rounded-lg">
            <h3 className="text-lg font-semibold mb-4">🌈 RGB Light</h3>
            <div className="grid grid-cols-4 gap-2">
              <button onClick={() => handleControl('RGB', 'red')} className="bg-red-600 hover:bg-red-700 p-3 rounded">R</button>
              <button onClick={() => handleControl('RGB', 'green')} className="bg-green-600 hover:bg-green-700 p-3 rounded">G</button>
              <button onClick={() => handleControl('RGB', 'blue')} className="bg-blue-600 hover:bg-blue-700 p-3 rounded">B</button>
              <button onClick={() => handleControl('RGB', 'yellow')} className="bg-yellow-500 hover:bg-yellow-600 p-3 rounded">Y</button>
              <button onClick={() => handleControl('RGB', 'purple')} className="bg-purple-600 hover:bg-purple-700 p-3 rounded">P</button>
              <button onClick={() => handleControl('RGB', 'light_blue')} className="bg-cyan-500 hover:bg-cyan-600 p-3 rounded">C</button>
              <button onClick={() => handleControl('RGB', 'white')} className="bg-white hover:bg-gray-200 text-black p-3 rounded">W</button>
              <button onClick={() => handleControl('RGB', 'off')} className="bg-gray-600 hover:bg-gray-700 p-3 rounded">OFF</button>
            </div>
          </div>
        )}

        {/* LCD */}
        {actuators.LCD && (
          <div className="bg-gray-800 p-6 rounded-lg">
            <h3 className="text-lg font-semibold mb-4">📟 LCD Display</h3>
            <input
              type="text"
              placeholder="Enter text..."
              className="w-full bg-gray-700 px-3 py-2 rounded mb-2 text-white"
              onKeyDown={(e) => {
                if (e.key === 'Enter' && e.target.value) {
                  handleControl('LCD', 'display_text', { text: e.target.value, line: 0 });
                  e.target.value = '';
                }
              }}
            />
            <button
              onClick={() => handleControl('LCD', 'clear')}
              className="w-full bg-red-600 hover:bg-red-700 px-4 py-2 rounded"
            >
              Clear
            </button>
          </div>
        )}
      </div>
    </div>
  );
}