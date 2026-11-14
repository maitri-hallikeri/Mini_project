from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

# 1. Exact Risk Levels defined in our CLOUDSHIELD problem statement
class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

# 2. The 6 Attack Scenarios from Person 1's Detection Module
class AttackType(str, Enum):
    NONE = "NONE"
    HTTP_FLOOD = "HTTP_FLOOD"
    DISTRIBUTED_HTTP_FLOOD = "DISTRIBUTED_HTTP_FLOOD"
    TARGETED_ENDPOINT_FLOOD = "TARGETED_ENDPOINT_FLOOD"
    SINGLE_SOURCE_BURST = "SINGLE_SOURCE_BURST"
    LOW_RATE_PERSISTENT = "LOW_RATE_PERSISTENT"
    MIXED_BOT_BURST = "MIXED_BOT_BURST"

# 3. Protective Actions your module can decide to take
class ProtectionAction(str, Enum):
    ALLOW = "ALLOW"                         # Normal traffic - do nothing
    RATE_LIMIT = "RATE_LIMIT"               # Slow down IP / endpoint
    TEMPORARY_BLOCK = "TEMPORARY_BLOCK"     # Block IP temporarily with auto-expiry
    ALREADY_MITIGATED = "ALREADY_MITIGATED" # Safeguard against duplicate alerts

# 4. INPUT: What Person 1 sends to your API every 10s window
class DetectionAlert(BaseModel):
    source_ip: str = Field(..., examples=["198.51.100.43"])
    endpoint: Optional[str] = Field(default="/", examples=["/login"])
    risk_score: float = Field(..., ge=0.0, le=100.0, examples=[85.0])
    risk_level: RiskLevel = Field(..., examples=[RiskLevel.HIGH])
    attack_type: AttackType = Field(default=AttackType.NONE, examples=[AttackType.SINGLE_SOURCE_BURST])
    requests_per_second: Optional[float] = Field(default=0.0, examples=[45.2])
    timestamp: datetime = Field(default_factory=datetime.utcnow)

# 5. OUTPUT: What your module returns to Person 1 & logs for Person 4's Dashboard
class MitigationRecord(BaseModel):
    action_id: str
    source_ip: str
    endpoint: Optional[str]
    risk_level: RiskLevel
    attack_type: AttackType
    action_taken: ProtectionAction
    applied_at: datetime
    expires_at: Optional[datetime]
    duration_seconds: int
    reason: str
    is_active: bool = True

# 6. OUTPUT: Container Health Status (for Module C - Automated Recovery)
class ContainerHealthRecord(BaseModel):
    container_name: str
    status: str                  # "HEALTHY", "UNHEALTHY", "RECOVERING", "FAILED"
    consecutive_failures: int
    last_checked_at: datetime
    last_recovery_at: Optional[datetime] = None
    recovery_time_seconds: Optional[float] = None
    message: str