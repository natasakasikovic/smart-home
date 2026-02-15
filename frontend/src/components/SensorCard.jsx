import React from 'react';

export default function SensorCard({ code, data }) {
  const getIcon = (code) => {
    if (code.includes('DHT')) return '🌡️';
    if (code.includes('PIR')) return '👁️';
    if (code.includes('DS')) return '🚪';
    if (code.includes('DUS')) return '📏';
    if (code === 'GSG') return '⚖️';
    if (code === 'DMS') return '🔢';
    if (code === 'IR') return '📡';
    return '📡';
  };

  return (
    <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
      <div className="flex justify-between items-start mb-4">
        <div>
          <p className="text-2xl">{getIcon(code)}</p>
          <h3 className="text-lg font-semibold">{code}</h3>
          <p className="text-sm text-gray-400">{data.name || 'Unknown'}</p>
        </div>
        {data.simulated && (
          <span className="text-xs bg-yellow-600 px-2 py-1 rounded">SIM</span>
        )}
      </div>
      
      <div className="space-y-2">
        {/* Door Sensor (DS) - state: OPEN/CLOSED */}
        {data.state !== undefined && code.includes('DS') && (
          <p className="text-sm">
            State: <span className={`font-bold ${data.state === 'OPEN' ? 'text-red-400' : 'text-green-400'}`}>
              {data.state}
            </span>
          </p>
        )}

        {/* DHT - Temperature & Humidity */}
        {data.temperature !== undefined && (
          <p className="text-sm">Temp: <span className="font-bold text-orange-400">{data.temperature}°C</span></p>
        )}
        {data.humidity !== undefined && (
          <p className="text-sm">Humidity: <span className="font-bold text-blue-400">{data.humidity}%</span></p>
        )}

        {/* DUS - Ultrasonic Distance */}
        {data.distance_cm !== undefined && (
          <p className="text-sm">Distance: <span className="font-bold text-cyan-400">{data.distance_cm.toFixed(1)}cm</span></p>
        )}

        {/* DPIR - Motion Sensor (detected: true/false) */}
        {data.detected !== undefined && (
          <p className="text-sm">
            Motion: <span className={`font-bold ${data.detected ? 'text-green-400' : 'text-gray-500'}`}>
              {data.detected ? '🟢 DETECTED' : '⚫ NONE'}
            </span>
          </p>
        )}

        {/* GSG - Gyroscope (nested accelerometer & gyroscope objects) */}
        {data.accelerometer && (
          <div className="text-sm">
            <p className="font-semibold text-cyan-400 mb-1">📐 Accelerometer:</p>
            <div className="grid grid-cols-3 gap-2 text-xs">
              <div>X: <span className="font-bold">{data.accelerometer.x?.toFixed(2)}</span></div>
              <div>Y: <span className="font-bold">{data.accelerometer.y?.toFixed(2)}</span></div>
              <div>Z: <span className="font-bold">{data.accelerometer.z?.toFixed(2)}</span></div>
            </div>
          </div>
        )}
        {data.gyroscope && (
          <div className="text-sm mt-2">
            <p className="font-semibold text-purple-400 mb-1">🔄 Gyroscope:</p>
            <div className="grid grid-cols-3 gap-2 text-xs">
              <div>X: <span className="font-bold">{data.gyroscope.x?.toFixed(2)}</span></div>
              <div>Y: <span className="font-bold">{data.gyroscope.y?.toFixed(2)}</span></div>
              <div>Z: <span className="font-bold">{data.gyroscope.z?.toFixed(2)}</span></div>
            </div>
          </div>
        )}

        {/* IR - Infrared (command) */}
        {data.command !== undefined && (
          <p className="text-sm">
            Command: <span className="font-bold text-yellow-400">📻 {data.command}</span>
          </p>
        )}

        {/* DMS - Membrane Switch (keypad - state holds the key) */}
        {data.state !== undefined && code.includes('DMS') && (
          <p className="text-sm">
            Key: <span className="font-bold text-green-400 text-xl">🔢 {data.state}</span>
          </p>
        )}

        {/* Timestamp */}
        {data.timestamp && (
          <p className="text-xs text-gray-500 mt-2">
            ⏱️ {new Date(data.timestamp).toLocaleTimeString()}
          </p>
        )}
      </div>
    </div>
  );
}