import React, { useEffect, useState } from 'react';

export default function AlarmNotification({ alarmActive }) {
  const [show, setShow] = useState(false);

  useEffect(() => {
    if (alarmActive) {
      setShow(true);
    } else {
      const timer = setTimeout(() => setShow(false), 3000);
      return () => clearTimeout(timer);
    }
  }, [alarmActive]);

  if (!show) return null;

  return (
    <div className={`fixed top-4 right-4 p-6 rounded-lg shadow-lg z-50 ${
      alarmActive ? 'bg-red-600 animate-pulse' : 'bg-green-600'
    }`}>
      <div className="flex items-center gap-4">
        <span className="text-4xl">{alarmActive ? '🚨' : '✅'}</span>
        <div>
          <h3 className="text-xl font-bold">
            {alarmActive ? 'ALARM ACTIVE!' : 'Alarm Deactivated'}
          </h3>
          <p className="text-sm">
            {alarmActive ? 'Security breach detected!' : 'System is safe'}
          </p>
        </div>
      </div>
    </div>
  );
}