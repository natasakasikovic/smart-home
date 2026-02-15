import React from 'react';
import { useSmartHome } from '../hooks/useSmartHome';
import SensorCard from './SensorCard';
import Actuators from './Actuators';
import AlarmPanel from './AlarmPanel';
import GrafanaPanel from './GrafanaPanel';
import WebcamPanel from './WebcamPanel';

export default function Dashboard() {
  const { state, connected } = useSmartHome();

  return (
    <div className="min-h-screen bg-gray-900 text-white p-8">
      
      {/* Header */}
      <div className="mb-8 flex justify-between items-center">
        <h1 className="text-4xl font-bold">🏠 Smart Home Control Panel</h1>
        <div className="flex gap-4 items-center">
          <div className={`w-3 h-3 rounded-full ${connected ? 'bg-green-500' : 'bg-red-500'}`} />
          <span className="text-sm">{connected ? 'Connected' : 'Disconnected'}</span>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-3 gap-4 mb-8">
        <div className="bg-gray-800 p-6 rounded-lg">
          <p className="text-gray-400 text-sm">People Inside</p>
          <p className="text-3xl font-bold">{state.person_count}</p>
        </div>
        <div className="bg-gray-800 p-6 rounded-lg">
          <p className="text-gray-400 text-sm">Active Sensors</p>
          <p className="text-3xl font-bold">{Object.keys(state.sensors).length}</p>
        </div>
        <div className="bg-gray-800 p-6 rounded-lg">
          <p className="text-gray-400 text-sm">Security Status</p>
          <p className={`text-3xl font-bold ${state.security_armed ? 'text-red-500' : 'text-green-500'}`}>
            {state.security_armed ? 'ARMED' : 'DISARMED'}
          </p>
        </div>
      </div>

      {/* Alarm Panel */}
      <AlarmPanel state={state} />

      {/* Actuators */}
      <Actuators actuators={state.actuators} />

      {/* Grafana Dashboard */}
      <GrafanaPanel />

      {/* Webcam */}
      <WebcamPanel />

      {/* Live Sensor Data */}
      <div className="mt-8">
        <h2 className="text-2xl font-bold mb-4">📡 Live Sensor Data</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {Object.entries(state.sensors).map(([code, data]) => (
            <SensorCard key={code} code={code} data={data} />
          ))}
        </div>
      </div>

    </div>
  );
}