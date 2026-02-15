import React from 'react';

export default function GrafanaPanel() {
  // should be in .env file, but for demo purposes, it's hardcoded here
  const GRAFANA_URL = 'http://localhost:3000/d/adpnxxg/branislav?orgId=1&from=2026-02-15T08:35:22.628Z&to=2026-02-15T10:19:45.400Z&timezone=browser';
  
  return (
    <div className="mt-8">
      <h2 className="text-2xl font-bold mb-4">📊 Grafana Dashboard</h2>
      <div className="bg-gray-800 rounded-lg overflow-hidden" style={{ height: '600px' }}>
        <iframe
          src={GRAFANA_URL}
          width="100%"
          height="100%"
          frameBorder="0"
          title="Grafana Dashboard"
        />
      </div>
    </div>
  );
}