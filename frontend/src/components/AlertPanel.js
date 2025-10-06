import React, { useState, useEffect, useRef } from 'react';
import './AlertPanel.css';


// NEW: Accept 'alerts' as a prop
function AlertPanel({ alerts }) {
  const alertsEndRef = useRef(null);

  useEffect(() => {
    // Auto-scroll to the latest alert
    alertsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [alerts]); // Effect runs when alerts change










// function AlertPanel() {
//   const [alerts, setAlerts] = useState([]);
//   const alertsEndRef = useRef(null);

//   useEffect(() => {
//     const ws = new WebSocket('ws://localhost:8001/ws/alerts');

//     ws.onmessage = (event) => {
//       const alertData = JSON.parse(event.data);
//       setAlerts(prevAlerts => [...prevAlerts, alertData]);
//     };

//     ws.onclose = () => console.log("Alert WebSocket disconnected");
//     ws.onerror = (error) => console.log("Alert WebSocket error:", error);

//     return () => ws.close();
//   }, []);

//   useEffect(() => {
//     // Auto-scroll to the latest alert
//     alertsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
//   }, [alerts]);

  return (
    <div className="alert-panel">
      <h2>🚨 Critical Alerts</h2>
      <ul className="alert-list">
        {alerts.map((alert, index) => (
          <li key={index} className="alert-item">
            <div className="alert-timestamp">{new Date(alert.timestamp).toLocaleTimeString()}</div>
            <div className="alert-message">
              <strong>{alert.anomaly_type}</strong> detected for Drone <strong>{alert.drone_id.substring(0, 8)}</strong>
            </div>
          </li>
        ))}
        <div ref={alertsEndRef} />
      </ul>
    </div>
  );
}

export default AlertPanel;