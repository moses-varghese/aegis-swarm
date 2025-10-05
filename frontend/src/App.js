import React, { useState, useEffect } from 'react';
import L from 'leaflet';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import { LineChart, Line, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import './App.css';

// Fix for default marker icon issue with webpack
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
  iconUrl: require('leaflet/dist/images/marker-icon.png'),
  shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
});

const anomalyIcon = new L.Icon({
    iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [1, -34],
    shadowSize: [41, 41]
});

function App() {
  const [drones, setDrones] = useState({});
  const [selectedDrone, setSelectedDrone] = useState(null);

  useEffect(() => {
    // const ws = new WebSocket("ws://localhost:8000/ws/dashboard");
    const ws = new WebSocket(`ws://${window.location.host}/ws/dashboard`);

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setDrones(prevDrones => {
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
          }
        };
      });
    };

    ws.onclose = () => console.log("WebSocket disconnected");
    ws.onerror = (error) => console.log("WebSocket error:", error);

    return () => ws.close();
  }, []);

  const center = [8.5241, 76.9366]; // Thiruvananthapuram
  const selectedDroneData = drones[selectedDrone];

  return (
    <div className="app-container">
      <div className="dashboard">
        <h1>Aegis Swarm Control</h1>
        <ul className="drone-list">
          {Object.values(drones).map(drone => (
            <li
              key={drone.drone_id}
              className={`drone-item ${drone.is_anomaly ? 'anomaly' : ''}`}
              onClick={() => setSelectedDrone(drone.drone_id)}
            >
              <strong>Drone ID:</strong> {drone.drone_id.substring(0, 8)}<br />
              <strong>Status:</strong> {drone.status}
            </li>
          ))}
        </ul>
        {selectedDroneData && (
          <div className="drone-details">
            <h2>Details for Drone {selectedDrone.substring(0, 8)}</h2>
            <p><strong>Battery:</strong> {selectedDroneData.battery_level.toFixed(2)}%</p>
            <p><strong>Altitude:</strong> {selectedDroneData.location.altitude.toFixed(2)}m</p>
            <p><strong>Anomaly:</strong> {selectedDroneData.is_anomaly ? 'YES' : 'NO'}</p>
            <p><strong>Reconstruction Error:</strong> {selectedDroneData.reconstruction_error.toFixed(6)}</p>
            
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
              icon={drone.is_anomaly ? anomalyIcon : new L.Icon.Default()}
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