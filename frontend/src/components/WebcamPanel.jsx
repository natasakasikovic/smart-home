import { useState } from 'react';

export default function WebcamPanel() {
  const WEBCAM_URL = 'http://192.168.107.144:8080/?action=stream';
  const [isOn, setIsOn] = useState(false);
  
  return (
    <div className="mt-8">
      <div className="flex items-center gap-4 mb-4">
        <h2 className="text-2xl font-bold">📹 Door Camera</h2>
        <button
          onClick={() => setIsOn(prev => !prev)}
          className={`px-4 py-1 rounded-full text-sm font-semibold transition-colors ${
            isOn 
              ? 'bg-red-600 hover:bg-red-700 text-white' 
              : 'bg-green-600 hover:bg-green-700 text-white'
          }`}
        >
          {isOn ? '⏹ Stop' : '▶ Start'}
        </button>
        {isOn && (
          <span className="flex items-center gap-1 text-sm text-green-400">
            <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse inline-block" />
            Live
          </span>
        )}
      </div>

      <div className="w-80 bg-gray-800 rounded-lg overflow-hidden">
        {isOn ? (
          <img 
            src={WEBCAM_URL} 
            alt="Webcam stream"
            className="w-full h-auto"
            onError={(e) => {
              e.target.src = 'https://placehold.co/640x480?text=Camera+Offline';
            }}
          />
        ) : (
          <div className="flex items-center justify-center h-48 text-gray-500">
            <div className="text-center">
              <div className="text-4xl mb-2">📷</div>
              <div className="text-sm">Camera is off</div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}