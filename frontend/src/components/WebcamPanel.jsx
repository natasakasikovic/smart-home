import React from 'react';

export default function WebcamPanel() {
  const WEBCAM_URL = 'http://192.168.107.144:8080/?action=stream';
  
  return (
    <div className="mt-8">
      <h2 className="text-2xl font-bold mb-4">📹 Door Camera</h2>
      <div className="bg-gray-800 rounded-lg overflow-hidden">
        <img 
          src={WEBCAM_URL} 
          alt="Webcam stream"
          className="w-full h-auto"
          onError={(e) => {
            e.target.src = 'https://via.placeholder.com/640x480?text=Camera+Offline';
          }}
        />
      </div>
    </div>
  );
}