import { useState, useEffect } from 'react'
import './App.css'

function App() {
const [health, setHealth] = useState(null)
const [healthError, setHealthError] = useState(false)

const [traffic, setTraffic] = useState([])
const [trafficError, setTrafficError] = useState(false)

const [risk, setRisk] = useState(null)
const [riskError, setRiskError] = useState(false)

const [mitigations, setMitigations] = useState([])
const [mitigationsError, setMitigationsError] = useState(false)

const [incidents, setIncidents] = useState([])
const [incidentsError, setIncidentsError] = useState(false)

const [replicas, setReplicas] = useState([])
const [replicasError, setReplicasError] = useState(false)

const [metrics, setMetrics] = useState(null)
const [metricsError, setMetricsError] = useState(false)

useEffect(() => {
  fetch('http://127.0.0.1:8000/api/v1/health')
    .then(response => {
      if (!response.ok) {
        throw new Error('Health API failed')
      }
      return response.json()
    })
    .then(data => {
      setHealth(data)
      setHealthError(false)
    })
    .catch(error => {
      console.error('Health API error:', error)
      setHealthError(true)
    })
    fetch('http://127.0.0.1:8000/api/v1/traffic/windows?limit=100')
  .then(response => {
    if (!response.ok) {
      throw new Error('Traffic API failed')
    }
    return response.json()
  })
  .then(data => {
    setTraffic(data)
    setTrafficError(false)
  })
  .catch(error => {
    console.error('Traffic API error:', error)
    setTrafficError(true)
  })
  fetch('http://127.0.0.1:8000/api/v1/risk/current')
  .then(response => {
    if (!response.ok) {
      throw new Error('Risk API failed')
    }
    return response.json()
  })
  .then(data => {
    setRisk(data)
    setRiskError(false)
  })
  .catch(error => {
    console.error('Risk API error:', error)
    setRiskError(true)
  })
  fetch('http://127.0.0.1:8000/api/v1/mitigations')
  .then(response => {
    if (!response.ok) {
      throw new Error('Mitigations API failed')
    }
    return response.json()
  })
  .then(data => {
    setMitigations(data)
    setMitigationsError(false)
  })
  .catch(error => {
    console.error('Mitigations API error:', error)
    setMitigationsError(true)
  })
  fetch('http://127.0.0.1:8000/api/v1/incidents')
  .then(response => {
    if (!response.ok) {
      throw new Error('Incidents API failed')
    }
    return response.json()
  })
  .then(data => {
    setIncidents(data)
    setIncidentsError(false)
  })
  .catch(error => {
    console.error('Incidents API error:', error)
    setIncidentsError(true)
  })
  fetch('http://127.0.0.1:8000/api/v1/replicas')
  .then(response => {
    if (!response.ok) {
      throw new Error('Replicas API failed')
    }
    return response.json()
  })
  .then(data => {
    setReplicas(data)
    setReplicasError(false)
  })
  .catch(error => {
    console.error('Replicas API error:', error)
    setReplicasError(true)
  })
  fetch('http://127.0.0.1:8000/api/v1/metrics/summary')
  .then(response => {
    if (!response.ok) {
      throw new Error('Metrics API failed')
    }
    return response.json()
  })
  .then(data => {
    setMetrics(data)
    setMetricsError(false)
  })
  .catch(error => {
    console.error('Metrics API error:', error)
    setMetricsError(true)
  })
}, [])
  return (
    <div className="app">

      <header className="navbar">
        <div className="logo">CLOUDSHIELD</div>

        <nav>
          <span className="active">Dashboard</span>
        </nav>

        <div className="system-status">
          <span className="status-dot"></span>
          System Online
        </div>
      </header>

      <main className="dashboard">

        <h1>Security Dashboard</h1>
        <p>Monitor, detect and protect your network.</p>

        {/* Overview Cards */}
        <section className="overview-cards">

          <div className="card">
            <h3>System Status</h3>
            <h2 className={health?.status === 'ok' ? 'green' : ''}>
              {healthError ? 'Offline' : health ? 'Online' : 'Checking...'}
            </h2>
          </div>

          <div className="card">
  <h3>Current Risk Level</h3>
  <h2>
    {riskError
      ? 'Unavailable'
      : risk
        ? risk.level
        : 'No Assessment'}
  </h2>
</div>

          <div className="card">
            <h3>Blocked IPs</h3>
            <h2>0</h2>
          </div>

          <div className="card">
            <h3>Container Health</h3>
            <h2 className="green">Healthy</h2>
          </div>

        </section>

                {/* Traffic Monitoring */}
        <section className="traffic-section">

          <div className="section-heading">
            <div>
              <h2>Traffic Monitoring</h2>
              <p>Monitor incoming network traffic.</p>
            </div>

            <span className="monitor-status">
              Monitoring
            </span>
          </div>

          <div className="traffic-placeholder">
  {trafficError ? (
    <p>Unable to load traffic data.</p>
  ) : traffic.length === 0 ? (
    <p>No traffic data available.</p>
  ) : (
    <div className="traffic-stats">
      <p>Total Requests: {traffic[traffic.length - 1].total_requests}</p>
      <p>Requests/sec: {traffic[traffic.length - 1].requests_per_sec}</p>
      <p>Unique IPs: {traffic[traffic.length - 1].unique_ips}</p>
      <p>Average Latency: {traffic[traffic.length - 1].avg_latency_ms} ms</p>
    </div>
  )}
</div>

        </section>

        {/* Active Mitigations */}
<section className="mitigation-section">

  <div className="section-heading">
    <div>
      <h2>Active Mitigations</h2>
      <p>Currently applied protection actions.</p>
    </div>
  </div>

  <div className="table-container">
    <table>
      <thead>
        <tr>
          <th>Source IP</th>
          <th>Attack Type</th>
          <th>Risk Level</th>
          <th>Action Taken</th>
          <th>Status</th>
        </tr>
      </thead>

      <tbody>
  {mitigationsError ? (
    <tr>
      <td colSpan="5" className="empty-table">
        Unable to load mitigation data.
      </td>
    </tr>
  ) : mitigations.length === 0 ? (
    <tr>
      <td colSpan="5" className="empty-table">
        No active mitigations.
      </td>
    </tr>
  ) : (
    mitigations.map(item => (
      <tr key={item.id}>
        <td>{item.target}</td>
        <td>{item.action_type}</td>
        <td>{item.risk_level}</td>
        <td>{item.action_type}</td>
        <td>{item.status}</td>
      </tr>
    ))
  )}
</tbody>
    </table>
  </div>

</section>

{/* Recovery Monitoring */}
<section className="recovery-section">

  <div className="section-heading">
    <div>
      <h2>Recovery Monitoring</h2>
      <p>Monitor container failures and recovery activity.</p>
    </div>
  </div>

  <div className="recovery-content">
    <div className="recovery-card">
      <h3>Recovery Status</h3>
      <p>Waiting for backend data</p>
    </div>

    <div className="recovery-card">
      <h3>Recent Recovery Activity</h3>
      <p>No recovery activity available.</p>
    </div>
  </div>

</section>

{/* Performance Metrics */}
<section className="recovery-section">

  <div className="section-heading">
    <div>
      <h2>Performance Metrics</h2>
      <p>Overview of system performance and recovery.</p>
    </div>
  </div>

  <div className="recovery-content">

    <div className="recovery-card">
      <h3>Total Incidents</h3>
      <p>{metricsError ? 'Unavailable' : metrics ? metrics.incident_count : 'Loading...'}</p>
    </div>

    <div className="recovery-card">
      <h3>Detection Latency</h3>
      <p>{metricsError ? 'Unavailable' : metrics?.detection_latency_s ?? 'N/A'}{metrics?.detection_latency_s != null ? ' s' : ''}</p>
    </div>

    <div className="recovery-card">
      <h3>Mitigation Latency</h3>
      <p>{metricsError ? 'Unavailable' : metrics?.mitigation_latency_s ?? 'N/A'}{metrics?.mitigation_latency_s != null ? ' s' : ''}</p>
    </div>

    <div className="recovery-card">
      <h3>Recovery Time</h3>
      <p>{metricsError ? 'Unavailable' : metrics?.recovery_time_s ?? 'N/A'}{metrics?.recovery_time_s != null ? ' s' : ''}</p>
    </div>

    <div className="recovery-card">
      <h3>Availability</h3>
      <p>{metricsError ? 'Unavailable' : metrics?.availability_pct ?? 'N/A'}{metrics?.availability_pct != null ? '%' : ''}</p>
    </div>

    <div className="recovery-card">
      <h3>Legitimate Success Rate</h3>
      <p>{metricsError ? 'Unavailable' : metrics?.legit_success_rate_pct ?? 'N/A'}{metrics?.legit_success_rate_pct != null ? '%' : ''}</p>
    </div>

  </div>

</section>

        {/* Dashboard Sections */}
        <section className="dashboard-sections">

          <div className="panel">
  <h2>Container Status</h2>

  {replicasError ? (
    <div className="empty-state">
      Unable to load replica data.
    </div>
  ) : replicas.length === 0 ? (
    <div className="empty-state">
      No replica data available.
    </div>
  ) : (
    replicas.map(replica => (
      <div className="container-item" key={replica.replica_id}>
        <span>{replica.replica_id}</span>
        <span className={replica.healthy ? 'healthy' : ''}>
          {replica.healthy ? 'Healthy' : 'Unhealthy'}
        </span>
      </div>
    ))
  )}
</div>

          <div className="panel">
  <h2>Recent Security Incidents</h2>

  <div className="empty-state">
    {incidentsError ? (
      'Unable to load security incidents.'
    ) : incidents.length === 0 ? (
      'No security incidents to display.'
    ) : (
      incidents.map(incident => (
        <div className="container-item" key={incident.id}>
          <span>{incident.scenario}</span>
          <span>{incident.status}</span>
        </div>
      ))
    )}
  </div>
</div>

        </section>

      </main>
    </div>
  )
}

export default App
