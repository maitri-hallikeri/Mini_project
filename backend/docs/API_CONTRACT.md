# API Contract

**For Member 4 (frontend) — precise specification of every route and WebSocket message.**

Base URL: `http://localhost:8000` (development)  
API prefix: `/api/v1`  
All datetimes: ISO-8601 UTC (e.g. `"2026-11-23T10:00:00Z"`)  
Error envelope: `{"detail": "<message>", "code": "<CODE>"}`

---

## REST endpoints

### GET /api/v1/health

Returns the application health status.  Always HTTP 200 when the process is running.

**Response 200**
```json
{
  "status": "ok",
  "app_version": "0.1.0",
  "env": "development",
  "pipeline_enabled": false,
  "server_time": "2026-11-23T10:00:00.123456Z"
}
```

---

### GET /api/v1/traffic/windows

Returns recent traffic feature windows.

**Query parameters**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `limit` | int | 100 | Max windows to return (1–1000) |
| `since` | datetime | — | Return only windows after this UTC timestamp |

**Response 200** — array of `WindowFeatures` (empty until pipeline runs)
```json
[]
```

**WindowFeatures shape**
```json
{
  "window_start": "2026-11-23T10:00:00Z",
  "window_end": "2026-11-23T10:00:10Z",
  "duration_s": 10.0,
  "total_requests": 350,
  "requests_per_sec": 35.0,
  "unique_ips": 12,
  "top_ip": "198.51.100.43",
  "top_ip_share": 0.71,
  "max_requests_per_ip": 250,
  "mean_requests_per_ip": 29.2,
  "top_endpoint": "/login",
  "top_endpoint_share": 0.80,
  "status_4xx_rate": 0.02,
  "status_5xx_rate": 0.00,
  "avg_latency_ms": 18.4,
  "p95_latency_ms": 45.0,
  "burstiness": 1.3
}
```

---

### GET /api/v1/risk/current

Returns the most recent risk assessment, or `null` if none exists.

**Response 200**
```json
null
```
or a `RiskAssessment` object (see shape below).

---

### GET /api/v1/risk/history

Returns all stored risk assessments, newest first.

**Response 200** — array of `RiskAssessment` (empty until pipeline runs)

**RiskAssessment shape**
```json
{
  "window_start": "2026-11-23T10:00:00Z",
  "window_end": "2026-11-23T10:00:10Z",
  "score": 78.5,
  "level": "HIGH",
  "scenario": "ENDPOINT_FLOOD",
  "signals": [
    {
      "name": "top_ip_share",
      "observed_value": 0.72,
      "baseline_value": 0.15,
      "threshold": 0.5,
      "deviation": 11.4,
      "weight": 0.3,
      "triggered": true,
      "description": "Top IP holds 72% of requests (baseline 15%, threshold 50%)."
    }
  ],
  "offending_ips": ["198.51.100.43"],
  "offending_endpoints": ["/login"],
  "detectors_used": ["RuleDetector", "StatisticalDetector"]
}
```

**level values:** `LOW` | `MEDIUM` | `HIGH` | `CRITICAL`  
**scenario values:** `NONE` | `REQUEST_FLOOD` | `ENDPOINT_FLOOD` | `BURST_ANOMALY` | `UNKNOWN`

---

### GET /api/v1/mitigations

Returns mitigation actions.

**Query parameters**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `status` | string | — | Filter by `ACTIVE`, `EXPIRED`, `ROLLED_BACK`, or `FAILED` |

**Response 200** — array of `MitigationAction` (empty until pipeline runs)

**MitigationAction shape**
```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "action_type": "TEMP_BLOCK_IP",
  "status": "ACTIVE",
  "target": "198.51.100.43",
  "parameters": {"duration_s": 300},
  "risk_level": "HIGH",
  "reason": "Top IP holds 72% of requests in window.",
  "incident_id": "7c8d9e0f-1234-5678-abcd-ef0123456789",
  "created_at": "2026-11-23T10:00:10Z",
  "expires_at": "2026-11-23T10:05:10Z"
}
```

**action_type values:** `LOG_ONLY` | `INCREASE_MONITORING` | `RATE_LIMIT` | `PROTECT_ENDPOINT` | `TEMP_BLOCK_IP` | `ROLLBACK`  
**status values:** `ACTIVE` | `EXPIRED` | `ROLLED_BACK` | `FAILED`

---

### POST /api/v1/mitigations/{action_id}/rollback

Manually rolls back an ACTIVE mitigation action.

**Response 501** (not yet implemented)
```json
{
  "detail": "TODO(member2/member3): not implemented",
  "code": "NOT_IMPLEMENTED"
}
```

---

### GET /api/v1/incidents

Returns all recorded incidents, newest first.

**Response 200** — array of `Incident` (empty until pipeline runs)

**Incident shape**
```json
{
  "id": "7c8d9e0f-1234-5678-abcd-ef0123456789",
  "status": "RESOLVED",
  "scenario": "ENDPOINT_FLOOD",
  "peak_risk_level": "HIGH",
  "started_at": "2026-11-23T10:00:00Z",
  "t_detect": "2026-11-23T10:00:03Z",
  "t_mitigate": "2026-11-23T10:00:05Z",
  "t_recover": "2026-11-23T10:08:30Z",
  "legit_success_rate": 0.994,
  "actions": []
}
```

**status values:** `OPEN` | `MITIGATING` | `RECOVERING` | `RESOLVED`

---

### GET /api/v1/incidents/{id}

Returns one incident by ID.

**Response 200** — `Incident` object  
**Response 404**
```json
{"detail": "Incident 'abc123' not found.", "code": "NOT_FOUND"}
```

---

### GET /api/v1/replicas

Returns health snapshots for all configured replicas.

**Response 200** — array of `ReplicaHealth` (empty until health checker is implemented)

**ReplicaHealth shape**
```json
{
  "replica_id": "app1",
  "url": "http://app1:8080",
  "healthy": true,
  "latency_ms": 8.3,
  "consecutive_failures": 0,
  "last_checked": "2026-11-23T10:00:05Z"
}
```

---

### GET /api/v1/metrics/summary

Returns aggregated evaluation metrics.

**Response 200**
```json
{
  "incident_count": 0,
  "detection_latency_s": null,
  "mitigation_latency_s": null,
  "recovery_time_s": null,
  "availability_pct": null,
  "legit_success_rate_pct": null
}
```

All float fields are `null` until at least one incident is resolved.

---

## WebSocket: /ws/live

Upgrade URL: `ws://localhost:8000/ws/live`

### Message envelope (all messages)

```json
{
  "type": "<string>",
  "timestamp": "2026-11-23T10:00:00.123456Z",
  "payload": {}
}
```

All server→client messages use this envelope.

### Allowed types (server → client)

| type | When sent | Payload schema |
|---|---|---|
| `hello` | Immediately on connect; also as keepalive every 30 s | `{}` |
| `risk_update` | After each pipeline cycle produces a `RiskAssessment` | `RiskAssessment` (see above) |
| `mitigation_event` | When a `MitigationAction` is applied, expired, or rolled back | `MitigationAction` (see above) |
| `health_update` | After each replica health check | `list[ReplicaHealth]` (see above) |
| `incident_update` | When an `Incident` is created or its status changes | `Incident` (see above) |

### hello example

```json
{
  "type": "hello",
  "timestamp": "2026-11-23T10:00:00Z",
  "payload": {}
}
```

### risk_update example

```json
{
  "type": "risk_update",
  "timestamp": "2026-11-23T10:00:10Z",
  "payload": {
    "window_start": "2026-11-23T10:00:00Z",
    "window_end": "2026-11-23T10:00:10Z",
    "score": 78.5,
    "level": "HIGH",
    "scenario": "ENDPOINT_FLOOD",
    "signals": [],
    "offending_ips": ["198.51.100.43"],
    "offending_endpoints": ["/login"],
    "detectors_used": ["RuleDetector"]
  }
}
```

### mitigation_event example

```json
{
  "type": "mitigation_event",
  "timestamp": "2026-11-23T10:00:11Z",
  "payload": {
    "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "action_type": "TEMP_BLOCK_IP",
    "status": "ACTIVE",
    "target": "198.51.100.43",
    "parameters": {},
    "risk_level": "HIGH",
    "reason": "Critical source.",
    "incident_id": null,
    "created_at": "2026-11-23T10:00:11Z",
    "expires_at": "2026-11-23T10:05:11Z"
  }
}
```

### Client → server

Client-sent messages are accepted but ignored in this version.

---

## Common error codes

| code | HTTP status | Meaning |
|---|---|---|
| `NOT_FOUND` | 404 | Resource with the given ID does not exist |
| `BAD_REQUEST` | 400 | Invalid request parameters |
| `NOT_IMPLEMENTED` | 501 | Feature not yet implemented |
| `VALIDATION_ERROR` | 422 | Request body or query parameter failed validation |
| `INTERNAL_SERVER_ERROR` | 500 | Unexpected server error |
