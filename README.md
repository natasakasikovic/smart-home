# Smart Home Automation & Security System 🏠

## Overview

This project implements a complete smart home automation and security system integrating multiple sensors, actuators, and a web application.
The smart home system comprises three Raspberry Pi units, each interfaced with different sensors and actuators.

## System Architecture & Technology Stack

The smart home system consists of three Raspberry Pi devices, each responsible for different sensors and actuators.

Communication & Data Flow:

- Raspberry Pi devices send sensor and actuator data via MQTT protocol to a Flask-based server for storage in InfluxDB and visualization in Grafana.
- Web application interfaces allow users to monitor sensor readings, control actuators, and view historical data.
- Each sensor and actuator can operate in **simulated** or **real** mode, which can be configured in the `settings.json` file.

Technology Stack:

- Programming & Server: Python, Flask
- Communication: MQTT
- Database: InfluxDB
- Visualization: Grafana
- Web Application: React

Hardware: Raspberry Pi, GPIO sensors and actuators

## Features

### Security & Motion Detection

- [x] When DPIR1 detects motion, DL1 is turned on for 10 seconds.
- [x] When DPIR1 detects motion, determine whether a person is entering or exiting the building based on the distance measured by DUS1 in the previous few seconds.
- [x] Same logic for DPIR2 and DUS2 as written above
- [x] Maintain and update the real-time count of occupants inside the building.
- [x] If a signal from DS1 or DS2 is detected for more than 5 seconds, activate the ALARM until the DS state changes. This simulates an unlocked door.
- [x] Enable activation of the security alarm via the DMS component.
- [x] When a 4-digit PIN code is entered, the system activates after 10 seconds.
- [x] If the system is active, trigger the ALARM when a signal is detected on DS1 or DS2, unless the correct PIN is entered via the DMS component.
- [x] Entering the PIN deactivates the ALARM and disarms the system.
- [x] If the number of people inside the building (as per point 2) is zero, trigger the ALARM when motion is detected by any of the RPIR1-3 sensors.
- [x] If the GSG (attached to the Slava icon) detects significant movement, trigger the ALARM.

### Environmental Monitoring

- [x] Display the temperature and humidity from DHT1-3 on the LCD, cycling through the readings from each DHT sensor every few seconds.

### Kitchen Timer

- [x] Enable kitchen timer settings.
- [x] Allow the timer duration to be set via the web application. Display the time on the 4-digit 7-segment (4SD) display.
- [x] Allow pressing the button (BTN) to add N seconds to the timer. N is the number of seconds configured via the web application.
- [x] When the timer expires, the 4SD display should blink showing 00:00. Pressing the button (BTN) stops the blinking.

### Lighting Control

- [x] Enable turning the BRGB light on/off and controlling its colors via the remote control and IR sensor, as well as through the web application.

### Camera

- [x] Display the webcam video on the web application.

## How to run?

1. Clone the repository
   - git clone `https://github.com/natasakasikovic/smart-home.git`
   - cd smart-home
2. Start Docker services (terminal docker)
   - cd docker
   - docker compose up -d
3. Run Raspberry Pi simulators (in separate terminals)
   - python main.py PI1
   - python main.py PI2
   - python main.py PI3
4. Start the server (terminal server)
   - python -m server.server
5. Start the frontend (terminal frontend)
   - cd frontend
   - npm install
   - npm run dev
