# Module Contracts

## Governance rule

> **Any change to a schema in `app/schemas/` requires a pull request approved
> by the module owners on both sides of the interface.**

Schemas are the shared language between modules.  Unilateral changes break
teammates' code.

---

## traffic_analysis interfaces

**Owner:** Member 1  
**File:** `app/modules/traffic_analysis/interfaces.py`

### LogSource

```python
class LogSource(ABC):
    def read_new_records(self) -> list[RequestLogRecord]: ...
```

| | Type | Description |
|---|---|---|
| **Returns** | `list[RequestLogRecord]` | All new log records since the last call, ordered by timestamp ascending |

### LogParser

```python
class LogParser(ABC):
    def parse_line(self, line: str) -> RequestLogRecord | None: ...
```

| | Type | Description |
|---|---|---|
| `line` | `str` | One raw Nginx access log line |
| **Returns** | `RequestLogRecord \| None` | Parsed record, or `None` for invalid/empty lines |

### WindowAggregator

```python
class WindowAggregator(ABC):
    def add(self, records: list[RequestLogRecord]) -> None: ...
    def pop_ready_windows(self, now: datetime) -> list[tuple[datetime, datetime, list[RequestLogRecord]]]: ...
```

| | Type | Description |
|---|---|---|
| `records` | `list[RequestLogRecord]` | Records to buffer |
| `now` | `datetime` (UTC) | Current time for window boundary check |
| **Returns** | `list[tuple[start, end, records]]` | Completed windows, oldest first |

### FeatureExtractor

```python
class FeatureExtractor(ABC):
    def extract(self, records: list[RequestLogRecord], window_start: datetime, window_end: datetime) -> WindowFeatures: ...
```

| | Type | Description |
|---|---|---|
| `records` | `list[RequestLogRecord]` | All records in the window |
| `window_start` / `window_end` | `datetime` (UTC) | Window boundaries |
| **Returns** | `WindowFeatures` | Fully-populated feature snapshot |

### BaselineStore

```python
class BaselineStore(ABC):
    def get(self, at: datetime) -> BaselineProfile | None: ...
    def update(self, features: WindowFeatures) -> None: ...
```

| | Type | Description |
|---|---|---|
| `at` | `datetime` (UTC) | Selects the matching hour-of-day bucket |
| **get returns** | `BaselineProfile \| None` | Profile, or `None` if fewer than 30 samples |
| `features` | `WindowFeatures` | From a window judged to be normal (LOW risk) |

---

## detection interfaces

**Owner:** Member 2  
**File:** `app/modules/detection/interfaces.py`

### Detector

```python
class Detector(ABC):
    name: str               # property
    def evaluate(self, features: WindowFeatures, baseline: BaselineProfile | None) -> list[SignalEvidence]: ...
```

| | Type | Description |
|---|---|---|
| `features` | `WindowFeatures` | Current window features |
| `baseline` | `BaselineProfile \| None` | Learned baseline, or `None` |
| **Returns** | `list[SignalEvidence]` | One entry per checked signal (triggered or not) |

### RiskScorer

```python
class RiskScorer(ABC):
    def score(self, features: WindowFeatures, signals: list[SignalEvidence]) -> RiskAssessment: ...
```

| | Type | Description |
|---|---|---|
| `features` | `WindowFeatures` | Used for window timestamps and offending IP/endpoint extraction |
| `signals` | `list[SignalEvidence]` | All signals from all detectors |
| **Returns** | `RiskAssessment` | Score (0-100), level, scenario, offending IPs/endpoints |
| **Constraint** | — | HIGH requires ≥ 2 triggered signals; CRITICAL requires ≥ 3 |

### DetectionEngineBase

```python
class DetectionEngineBase(ABC):
    def assess(self, features: WindowFeatures, baseline: BaselineProfile | None) -> RiskAssessment: ...
```

This is wired in `engine.py` — it calls all enabled detectors and the scorer.

---

## mitigation interfaces

**Owner:** Member 2  
**File:** `app/modules/mitigation/interfaces.py`

### MitigationController

```python
class MitigationController(ABC):
    def decide(self, assessment: RiskAssessment) -> list[MitigationAction]: ...
    def apply(self, actions: list[MitigationAction]) -> list[MitigationAction]: ...
    def expire_due(self, now: datetime) -> list[MitigationAction]: ...
    def rollback(self, action_id: str, actor: str) -> MitigationAction: ...
```

Default policy (see `app/modules/mitigation/README.md` for the full table).

### RuleWriter

```python
class RuleWriter(ABC):
    def write_blocklist(self, ips: list[str]) -> None: ...
    def write_rate_limits(self, rules: list[dict]) -> None: ...
    def reload(self) -> None: ...
```

### AuditLogger

```python
class AuditLogger(ABC):
    def record(self, event_type: str, details: dict, action_id: str | None = None) -> None: ...
```

---

## recovery interfaces

**Owner:** Member 2  
**File:** `app/modules/recovery/interfaces.py`

### HealthChecker

```python
class HealthChecker(ABC):
    def check_all(self) -> list[ReplicaHealth]: ...
```

| | Type | Description |
|---|---|---|
| **Returns** | `list[ReplicaHealth]` | One entry per URL in `Settings.REPLICA_URLS` |

### RecoveryManager

```python
class RecoveryManager(ABC):
    def recover(self, unhealthy: list[ReplicaHealth]) -> list[RecoveryEvent]: ...
    def restore_routing(self, replica_id: str) -> RecoveryEvent: ...
```

---

## Schema change process

1. Open a pull request with the proposed change to `app/schemas/<file>.py`.
2. Request review from **all owners of modules that import the changed schema**.
3. Merge only when all reviewers approve.
4. Each reviewer updates their module's stub or implementation in the same PR or a follow-up PR.
