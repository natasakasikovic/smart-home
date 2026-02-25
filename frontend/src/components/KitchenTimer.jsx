import React, { useState } from 'react';
import { controlActuator } from '../api';

export default function KitchenTimer() {
  const [minutes, setMinutes] = useState(0);
  const [seconds, setSeconds] = useState(0);
  const [addSeconds, setAddSeconds] = useState(10);

  const handleSetTimer = async () => {
    const totalSeconds = minutes * 60 + seconds;
    try {
      await controlActuator('4SD', 'set_timer', { seconds: totalSeconds });
      console.log(`✅ Timer set to ${totalSeconds}s`);
    } catch (error) {
      console.error('❌ Failed to set timer:', error);
    }
  };

  const handleStart = async () => {
    try {
      await controlActuator('4SD', 'start');
      console.log('✅ Timer started');
    } catch (error) {
      console.error('❌ Failed to start timer:', error);
    }
  };

  const handleStop = async () => {
    try {
      await controlActuator('4SD', 'stop');
      console.log('✅ Timer stopped');
    } catch (error) {
      console.error('❌ Failed to stop timer:', error);
    }
  };

  const handleConfigureButton = async () => {
    try {
      await controlActuator('BTN', 'configure', { add_seconds: addSeconds });
      console.log(`✅ Button configured to add ${addSeconds}s`);
    } catch (error) {
      console.error('❌ Failed to configure button:', error);
    }
  };

  return (
    <div className="mt-8">
      <h2 className="text-2xl font-bold mb-4">⏱️ Kitchen Timer (4SD + BTN)</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        
        {/* Timer Setup */}
        <div className="bg-gray-800 p-6 rounded-lg">
          <h3 className="text-lg font-semibold mb-4">Set Timer</h3>
          
          <div className="flex gap-4 mb-4">
            <div className="flex-1">
              <label className="block text-sm text-gray-400 mb-2">Minutes</label>
              <input
                type="number"
                min="0"
                max="99"
                value={minutes}
                onChange={(e) => setMinutes(parseInt(e.target.value) || 0)}
                className="w-full bg-gray-700 px-3 py-2 rounded text-white"
              />
            </div>
            <div className="flex-1">
              <label className="block text-sm text-gray-400 mb-2">Seconds</label>
              <input
                type="number"
                min="0"
                max="59"
                value={seconds}
                onChange={(e) => setSeconds(parseInt(e.target.value) || 0)}
                className="w-full bg-gray-700 px-3 py-2 rounded text-white"
              />
            </div>
          </div>

          <button
            onClick={handleSetTimer}
            className="w-full bg-blue-600 hover:bg-blue-700 px-4 py-3 rounded font-bold mb-2"
          >
            ⏱️ Set Timer ({minutes}m {seconds}s)
          </button>

          <div className="flex gap-2">
            <button
              onClick={handleStart}
              className="flex-1 bg-green-600 hover:bg-green-700 px-4 py-2 rounded"
            >
             Start
            </button>
            <button
              onClick={handleStop}
              className="flex-1 bg-red-600 hover:bg-red-700 px-4 py-2 rounded"
            >
             Stop
            </button>
          </div>
        </div>

        {/* Button Configuration */}
        <div className="bg-gray-800 p-6 rounded-lg">
          <h3 className="text-lg font-semibold mb-4">Kitchen Button (BTN)</h3>
          
          <div className="mb-4">
            <label className="block text-sm text-gray-400 mb-2">
              Seconds to add when BTN is pressed
            </label>
            <input
              type="number"
              min="1"
              max="300"
              value={addSeconds}
              onChange={(e) => setAddSeconds(parseInt(e.target.value) || 10)}
              className="w-full bg-gray-700 px-3 py-2 rounded text-white"
            />
          </div>

          <button
            onClick={handleConfigureButton}
            className="w-full bg-orange-600 hover:bg-orange-700 px-4 py-3 rounded font-bold"
          >
            🔧 Configure Button (+{addSeconds}s)
          </button>

          <p className="text-sm text-gray-400 mt-4">
            ℹ️ When the physical button is pressed, it will add {addSeconds} seconds to the timer.
          </p>
        </div>

      </div>
    </div>
  );
}