# 🏠 Smart Home Frontend

React-based dashboard for real-time monitoring and control of smart home devices.

## 🚀 Quick Start

```bash
cd frontend
npm install
npm run dev
```

Open: **http://localhost:5173**

## 📦 Dependencies

- **React** - UI framework
- **Vite** - Build tool
- **Socket.io** - Real-time WebSocket communication
- **Axios** - HTTP requests

## 📁 Structure

```
src/
├── App.jsx                   # Main app entry
├── api.js                    # API helper functions
├── hooks/
│   └── useSmartHome.js       # WebSocket + state management
└── components/
    ├── Dashboard.jsx         # Main dashboard
    ├── SensorCard.jsx        # Individual sensor display
    ├── Actuators.jsx         # Actuator controls (buzzer, lights, RGB, LCD)
    ├── AlarmPanel.jsx        # Alarm system control
    ├── GrafanaPanel.jsx      # Grafana dashboard embed
    └── WebcamPanel.jsx       # Camera stream
```

## 🔌 Backend Requirements

- Flask server running on `http://localhost:5000`
- WebSocket endpoint for real-time updates
- REST API endpoints: `/api/state`, `/api/actuator/<code>`, `/api/alarm/*`

## ✨ Features

- ✅ Real-time sensor data via WebSocket
- ✅ Actuator control (buzzer, lights, RGB LED, LCD)
- ✅ Alarm system management
- ✅ Grafana dashboard integration
- ✅ Webcam stream display

## 🛠️ Configuration

### Grafana Dashboard

Edit `src/components/GrafanaPanel.jsx`:

```jsx
const GRAFANA_URL =
  "http://localhost:3000/d/your-dashboard-id?orgId=1&theme=dark&kiosk";
```

Get your dashboard URL:

1. Open Grafana dashboard
2. Click **Share** → **Link**
3. Enable **Kiosk mode** and **Dark theme**
4. Copy URL

### Webcam Stream

Edit `src/components/WebcamPanel.jsx`:

```jsx
const WEBCAM_URL = "http://192.168.1.100:8080/?action=stream";
```

Replace with your Pi webcam IP address.

## 📡 API Endpoints Used

| Method | Endpoint               | Description              |
| ------ | ---------------------- | ------------------------ |
| GET    | `/api/state`           | Get current system state |
| POST   | `/api/actuator/<code>` | Control actuator         |
| POST   | `/api/alarm/arm`       | Arm security system      |
| POST   | `/api/alarm/disarm`    | Disarm with PIN          |
