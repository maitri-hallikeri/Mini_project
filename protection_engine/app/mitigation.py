import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from app.config import settings
from app.schemas import (
    DetectionAlert,
    MitigationRecord,
    ProtectionAction,
    RiskLevel,
    AttackType,
)


class MitigationManager:
    """
    Manages automated risk-based traffic mitigation, temporary restrictions,
    auto-expiry timers, and audit history.
    """

    def __init__(self):
        # Stores currently active restrictions mapped by source_ip
        # Example: {"198.51.100.43": MitigationRecord(...)}
        self.active_restrictions: Dict[str, MitigationRecord] = {}

        # Stores complete audit log of all decisions (for Person 4's dashboard)
        self.mitigation_history: List[MitigationRecord] = []

    def cleanup_expired_restrictions(self) -> List[str]:
        """
        Checks all active blocks/rate-limits and automatically removes
        any restriction whose expiry timestamp has passed.
        Returns a list of IPs that were unblocked.
        """
        now = datetime.utcnow()
        expired_ips = []

        for ip, record in list(self.active_restrictions.items()):
            if record.expires_at and now >= record.expires_at:
                record.is_active = False
                del self.active_restrictions[ip]
                expired_ips.append(ip)

        return expired_ips

    def evaluate_and_mitigate(self, alert: DetectionAlert) -> MitigationRecord:
        """
        Main decision engine called whenever Person 1 sends a DetectionAlert.
        """
        # Step 1: Always clean up expired rules first
        self.cleanup_expired_restrictions()
        now = datetime.utcnow()

        # Step 2: Safeguard — Never block whitelisted internal/admin IPs
        if alert.source_ip in settings.WHITELISTED_IPS:
            record = MitigationRecord(
                action_id=str(uuid.uuid4())[:8],
                source_ip=alert.source_ip,
                endpoint=alert.endpoint,
                risk_level=alert.risk_level,
                attack_type=alert.attack_type,
                action_taken=ProtectionAction.ALLOW,
                applied_at=now,
                expires_at=None,
                duration_seconds=0,
                reason="Safeguard triggered: IP is in WHITELISTED_IPS.",
                is_active=False,
            )
            self.mitigation_history.append(record)
            return record

        # Step 3: Safeguard — Prevent duplicate actions if IP is already restricted
        if alert.source_ip in self.active_restrictions:
            existing = self.active_restrictions[alert.source_ip]
            remaining = int((existing.expires_at - now).total_seconds()) if existing.expires_at else 0
            return MitigationRecord(
                action_id=existing.action_id,
                source_ip=alert.source_ip,
                endpoint=alert.endpoint,
                risk_level=alert.risk_level,
                attack_type=alert.attack_type,
                action_taken=ProtectionAction.ALREADY_MITIGATED,
                applied_at=existing.applied_at,
                expires_at=existing.expires_at,
                duration_seconds=max(0, remaining),
                reason=f"IP already under {existing.action_taken.value} ({max(0, remaining)}s remaining).",
                is_active=True,
            )

        # Step 4: Risk-Based Decision Matrix
        action = ProtectionAction.ALLOW
        duration = 0
        reason = "Traffic within normal baseline."

        if alert.risk_level == RiskLevel.CRITICAL:
            action = ProtectionAction.TEMPORARY_BLOCK
            duration = settings.CRITICAL_RISK_BLOCK_SECONDS
            reason = f"Critical risk ({alert.risk_score}/100) — {alert.attack_type.value} detected."

        elif alert.risk_level == RiskLevel.HIGH:
            action = ProtectionAction.TEMPORARY_BLOCK
            duration = settings.HIGH_RISK_BLOCK_SECONDS
            reason = f"High risk ({alert.risk_score}/100) — {alert.attack_type.value} detected."

        elif alert.risk_level == RiskLevel.MEDIUM:
            action = ProtectionAction.RATE_LIMIT
            duration = settings.MEDIUM_RISK_LIMIT_SECONDS
            reason = f"Medium risk ({alert.risk_score}/100) — applying rate-limiting to avoid false blocking."

        # Step 5: Apply & Record the Mitigation Action
        expires_at = now + timedelta(seconds=duration) if duration > 0 else None
        is_active = action in [ProtectionAction.TEMPORARY_BLOCK, ProtectionAction.RATE_LIMIT]

        record = MitigationRecord(
            action_id=str(uuid.uuid4())[:8],
            source_ip=alert.source_ip,
            endpoint=alert.endpoint,
            risk_level=alert.risk_level,
            attack_type=alert.attack_type,
            action_taken=action,
            applied_at=now,
            expires_at=expires_at,
            duration_seconds=duration,
            reason=reason,
            is_active=is_active,
        )

        if is_active:
            self.active_restrictions[alert.source_ip] = record

        self.mitigation_history.append(record)
        return record

    def get_active_restrictions(self) -> List[MitigationRecord]:
        """Returns all currently active blocks/rate-limits after purging expired ones."""
        self.cleanup_expired_restrictions()
        return list(self.active_restrictions.values())

    def manual_unblock(self, ip: str) -> bool:
        """Allows admin (or dashboard button) to manually lift a restriction early."""
        if ip in self.active_restrictions:
            self.active_restrictions[ip].is_active = False
            del self.active_restrictions[ip]
            return True
        return False


# Create a single shared instance to be imported across our app
mitigation_manager = MitigationManager()