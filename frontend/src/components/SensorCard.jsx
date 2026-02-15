import React from 'react';

export default function SensorCard({ code, data }) {
  const getIcon = (code) => {
    if (code.includes('DHT')) return '🌡️';
    if (code.includes('PIR')) return '👁️';
    if (code.includes('DS')) return '🚪';
    if (code.includes('DUS')) return '📏';
    if (code === 'GSG') return '⚖️';
    if (code === 'DMS') return '🔢';
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
        {data.state !== undefined && (
          <p className="text-sm">State: <span className="font-bold">{data.state}</span></p>
        )}
        {data.temperature !== undefined && (
          <p className="text-sm">Temp: <span className="font-bold">{data.temperature}°C</span></p>
        )}
        {data.humidity !== undefined && (
          <p className="text-sm">Humidity: <span className="font-bold">{data.humidity}%</span></p>
        )}
        {data.distance !== undefined && (
          <p className="text-sm">Distance: <span className="font-bold">{data.distance}cm</span></p>
        )}
        {data.active !== undefined && (
          <p className="text-sm">Active: <span className="font-bold">{data.active ? 'YES' : 'NO'}</span></p>
        )}
        {data.timestamp && (
          <p className="text-xs text-gray-500 mt-2">
            {new Date(data.timestamp).toLocaleTimeString()}
          </p>
        )}
      </div>
    </div>
  );
}