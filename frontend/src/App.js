import React, { useState, useEffect } from 'react';
import AlertPanel from './components/AlertPanel'; // Import the new component
import L from 'leaflet';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import { LineChart, Line, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import './App.css';
import droneIconSvg from './airplanemode_active.svg';

// --- NEW: Custom Drone Icon ---
// We use a DivIcon which allows us to use HTML and CSS for the marker, including rotation.
const createDroneIcon = (rotation, is_anomaly) => {
  const anomalyClass = is_anomaly ? 'drone-icon-anomaly' : '';
  return L.divIcon({
    className: 'drone-icon-container',
    html: `<img src="${droneIconSvg}" style="transform: rotate(${rotation}deg);" class="drone-icon ${anomalyClass}"/>`,
    iconSize: [30, 30],
    iconAnchor: [15, 15],
  });
};

// Fix for default marker icon issue with webpack
// delete L.Icon.Default.prototype._getIconUrl;
// L.Icon.Default.mergeOptions({
//   iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
//   iconUrl: require('leaflet/dist/images/marker-icon.png'),
//   shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
// });

// const anomalyIcon = new L.Icon({
//     iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png',
//     shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
//     iconSize: [25, 41],
//     iconAnchor: [12, 41],
//     popupAnchor: [1, -34],
//     shadowSize: [41, 41]
// });

// --- Helper function to calculate angle ---
function calculateAngle(lat1, lon1, lat2, lon2) {
  const dy = lat2 - lat1;
  const dx = Math.cos(lat1 * (Math.PI / 180)) * (lon2 - lon1);
  const angle = Math.atan2(dy, dx) * (180 / Math.PI);
  return angle;
}

function App() {
  const [drones, setDrones] = useState({});
  const [alerts, setAlerts] = useState([]);
  const [selectedDrone, setSelectedDrone] = useState(null);

  useEffect(() => {
    // const ws = new WebSocket("ws://localhost:8000/ws/dashboard");
    // const ws = new WebSocket(`ws://${window.location.host}/ws/dashboard`);
    const ws = new WebSocket('ws://localhost:8000/ws/dashboard');

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);

      // NEW: Differentiate between message types
      if (data.type === 'telemetry') {



      setDrones(prevDrones => {

        const existingDrone = prevDrones[data.drone_id];
        let rotation = existingDrone ? existingDrone.rotation : 0;
        if (existingDrone && (existingDrone.location.lat !== data.location.lat || existingDrone.location.lon !== data.location.lon)) {
            rotation = calculateAngle(
              existingDrone.location.lat,
              existingDrone.location.lon,
              data.location.lat,
              data.location.lon
            );
          }


        const newHistory = prevDrones[data.drone_id] 
          ? [...prevDrones[data.drone_id].history, { error: data.reconstruction_error, time: new Date().toLocaleTimeString() }]
          : [{ error: data.reconstruction_error, time: new Date().toLocaleTimeString() }];

        // Keep history to a manageable size
        if (newHistory.length > 50) newHistory.shift();

        return {
          ...prevDrones,
          [data.drone_id]: {
            ...data,
            history: newHistory,
            rotation: rotation,
          }
        };
      });
    } else if (data.type === 'alert') {
        setAlerts(prevAlerts => [...prevAlerts, data]);
      }
    };

    ws.onclose = () => console.log("WebSocket disconnected");
    ws.onerror = (error) => console.log("WebSocket error:", error);

    return () => ws.close();
  }, []);


  // --- NEW: Function to send commands to the backend API ---
  const handleSendCommand = async (droneId, command) => {
    try {
      const response = await fetch(`http://localhost:8000/api/drones/${droneId}/command`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ command }),
      });
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      const result = await response.json();
      console.log('Command success:', result);
    } catch (error) {
      console.error('Failed to send command:', error);
    }
  };

  const center = [8.5241, 76.9366]; // Thiruvananthapuram
  const selectedDroneData = drones[selectedDrone];

  return (
  <div className="app-container">
    <div className="dashboard">
      <div className="main-controls">
        <h1>Aegis Swarm Control</h1>
        <ul className="drone-list">
          {Object.values(drones).map(drone => (
            <li
              key={drone.drone_id}
              className={`drone-item ${drone.is_anomaly ? 'anomaly' : ''}`}
              onClick={() => setSelectedDrone(drone.drone_id)}
            >
              <strong>Drone ID:</strong> {drone.drone_id.substring(0, 8)}<br />
              <strong>Status:</strong>
              <span style={{ color: drone.is_anomaly ? '#F44336' : '#4CAF50', fontWeight: 'bold' }}>
                {drone.is_anomaly ? ` ${drone.anomaly_type}` : ' Normal'}
              </span>
            </li>
          ))}
        </ul>
        {selectedDroneData && (
          <div className="drone-details">
            <h2>Details for Drone {selectedDrone.substring(0, 8)}</h2>
            <p><strong>Battery:</strong> {selectedDroneData.battery_level.toFixed(2)}%</p>
            <p><strong>Altitude:</strong> {selectedDroneData.location.altitude.toFixed(2)}m</p>
            <p>
              <strong>Status:</strong>{' '}
              {selectedDroneData.is_anomaly ? (
                <span style={{ color: '#F44336', fontWeight: 'bold' }}>
                  {selectedDroneData.anomaly_type}
                </span>
              ) : (
                <span style={{ color: '#4CAF50' }}>Normal</span>
              )}
            </p>
            <p><strong>Reconstruction Error:</strong> {selectedDroneData.reconstruction_error.toFixed(6)}</p>

            {selectedDroneData.is_anomaly && (
              <button
                className="command-button"
                onClick={() => handleSendCommand(selectedDroneData.drone_id, 'RTB')}
              >
                Send RTB Command
              </button>
            )}
            
            <ResponsiveContainer width="100%" height={200}>
              <LineChart data={selectedDroneData.history}>
                <XAxis dataKey="time" />
                <YAxis domain={[0, 'auto']}/>
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="error" stroke="#8884d8" dot={false} />
                 <Line type="monotone" name="Threshold" dataKey={() => selectedDroneData.threshold} stroke="#F44336" dot={false}/>
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>
      <AlertPanel alerts={alerts} />
    </div>

      <div className="map-container">
        <MapContainer center={center} zoom={13} style={{ height: '100%', width: '100%' }}>
          <TileLayer
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          />
          {Object.values(drones).map(drone => (
            <Marker 
              key={drone.drone_id} 
              position={[drone.location.lat, drone.location.lon]}
              // icon={drone.is_anomaly ? anomalyIcon : new L.Icon.Default()}
              // icon={drone.is_anomaly ? anomalyIcon : createDroneIcon(drone.rotation)}
              icon={createDroneIcon(drone.rotation, drone.is_anomaly)}
            >
              <Popup>
                Drone ID: {drone.drone_id.substring(0, 8)} <br />
                Battery: {drone.battery_level.toFixed(2)}%
              </Popup>
            </Marker>
          ))}
        </MapContainer>
      </div>
    </div>
  );
}

export default App;