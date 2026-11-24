"""
Mitigation controller implementation.

Owner: Member 2.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

from app.core.config import get_settings
from app.modules.mitigation.audit import DbAuditLogger
from app.modules.mitigation.expiry import find_expired
from app.modules.mitigation.interfaces import AuditLogger, MitigationController, RuleWriter
from app.modules.mitigation.nginx_writer import NginxRuleWriter
from app.schemas.detection import RiskAssessment, RiskLevel
from app.schemas.mitigation import ActionStatus, ActionType, MitigationAction

# Safeguard: never block localhost / internal loopback addresses
WHITELISTED_IPS = {"127.0.0.1", "::1", "localhost"}


class DefaultMitigationController(MitigationController):
    """
    Decides, applies, expires, and rolls back automated mitigation actions
    based on incoming ``RiskAssessment`` objects.
    """

    def __init__(
        self,
        rule_writer: RuleWriter | None = None,
        audit_logger: AuditLogger | None = None,
        mitigation_repo: Any = None,
        default_ttl_s: int | None = None,
    ) -> None:
        settings = get_settings()
        self._writer = rule_writer or NginxRuleWriter(settings.NGINX_BLOCKLIST_PATH)
        self._audit = audit_logger or DbAuditLogger()
        self._repo = mitigation_repo
        self._default_ttl_s = default_ttl_s or settings.MITIGATION_DEFAULT_TTL_S

        # In-memory store keyed by action.id so lifecycle operations work
        # standalone and in unit tests even before DB repositories are wired.
        self._actions: dict[str, MitigationAction] = {}

    def _is_target_already_active(self, target: str | None, action_type: ActionType) -> bool:
        """Prevent duplicate active rules for the same IP or endpoint."""
        if target is None:
            return False
        return any(
            a.status == ActionStatus.ACTIVE
            and a.target == target
            and a.action_type == action_type
            for a in self._actions.values()
        )

    def _sync_nginx(self) -> None:
        """Rebuild Nginx blocklist and rate-limit files from currently ACTIVE actions."""
        active_actions = [
            a for a in self._actions.values() if a.status == ActionStatus.ACTIVE
        ]

        blocked_ips = [
            a.target
            for a in active_actions
            if a.action_type == ActionType.TEMP_BLOCK_IP and a.target
        ]
        rate_rules = [
            {
                "target": a.target,
                "rate": a.parameters.get("rate", 10),
                "burst": a.parameters.get("burst", 20),
            }
            for a in active_actions
            if a.action_type in (ActionType.RATE_LIMIT, ActionType.PROTECT_ENDPOINT)
            and a.target
        ]

        self._writer.write_blocklist(blocked_ips)
        self._writer.write_rate_limits(rate_rules)
        self._writer.reload()

    def decide(self, assessment: RiskAssessment) -> list[MitigationAction]:
        """Choose proportional mitigation actions for a given RiskAssessment."""
        now = datetime.now(UTC)
        level = assessment.level
        safe_ips = [ip for ip in assessment.offending_ips if ip not in WHITELISTED_IPS]
        actions: list[MitigationAction] = []

        if level == RiskLevel.LOW:
            actions.append(
                MitigationAction(
                    id=str(uuid.uuid4()),
                    action_type=ActionType.LOG_ONLY,
                    status=ActionStatus.ACTIVE,
                    target=None,
                    parameters={"score": assessment.score},
                    risk_level=level.value,
                    reason="Normal traffic baseline; logging observation only.",
                    created_at=now,
                    expires_at=None,
                )
            )
            return actions

        if level == RiskLevel.MEDIUM:
            ttl = min(120, self._default_ttl_s)
            expires = now + timedelta(seconds=ttl)
            actions.append(
                MitigationAction(
                    id=str(uuid.uuid4()),
                    action_type=ActionType.INCREASE_MONITORING,
                    status=ActionStatus.ACTIVE,
                    target=None,
                    parameters={"duration_s": ttl, "score": assessment.score},
                    risk_level=level.value,
                    reason=f"Medium risk ({assessment.score}/100): tightening monitoring.",
                    created_at=now,
                    expires_at=expires,
                )
            )
            for ip in safe_ips:
                if not self._is_target_already_active(ip, ActionType.RATE_LIMIT):
                    actions.append(
                        MitigationAction(
                            id=str(uuid.uuid4()),
                            action_type=ActionType.RATE_LIMIT,
                            status=ActionStatus.ACTIVE,
                            target=ip,
                            parameters={"rate": 20, "burst": 40, "duration_s": ttl},
                            risk_level=level.value,
                            reason=f"Medium risk ({assessment.score}/100): conservative rate-limit on {ip}.",
                            created_at=now,
                            expires_at=expires,
                        )
                    )
            return actions

        if level == RiskLevel.HIGH:
            ttl = self._default_ttl_s
            expires = now + timedelta(seconds=ttl)
            for ip in safe_ips:
                if not self._is_target_already_active(ip, ActionType.RATE_LIMIT):
                    actions.append(
                        MitigationAction(
                            id=str(uuid.uuid4()),
                            action_type=ActionType.RATE_LIMIT,
                            status=ActionStatus.ACTIVE,
                            target=ip,
                            parameters={"rate": 5, "burst": 10, "duration_s": ttl},
                            risk_level=level.value,
                            reason=f"High risk ({assessment.score}/100): strict rate-limit on {ip}.",
                            created_at=now,
                            expires_at=expires,
                        )
                    )
            for ep in assessment.offending_endpoints:
                if not self._is_target_already_active(ep, ActionType.PROTECT_ENDPOINT):
                    actions.append(
                        MitigationAction(
                            id=str(uuid.uuid4()),
                            action_type=ActionType.PROTECT_ENDPOINT,
                            status=ActionStatus.ACTIVE,
                            target=ep,
                            parameters={"rate": 10, "burst": 15, "duration_s": ttl},
                            risk_level=level.value,
                            reason=f"High risk ({assessment.score}/100): protecting targeted endpoint {ep}.",
                            created_at=now,
                            expires_at=expires,
                        )
                    )
            return actions

        # CRITICAL risk -> temporary IP block for high-confidence offenders
        ttl = self._default_ttl_s
        expires = now + timedelta(seconds=ttl)
        for ip in safe_ips:
            if not self._is_target_already_active(ip, ActionType.TEMP_BLOCK_IP):
                actions.append(
                    MitigationAction(
                        id=str(uuid.uuid4()),
                        action_type=ActionType.TEMP_BLOCK_IP,
                        status=ActionStatus.ACTIVE,
                        target=ip,
                        parameters={"duration_s": ttl, "scenario": assessment.scenario.value},
                        risk_level=level.value,
                        reason=f"Critical risk ({assessment.score}/100): temporary IP block on {ip}.",
                        created_at=now,
                        expires_at=expires,
                    )
                )
        return actions

    def apply(self, actions: list[MitigationAction]) -> list[MitigationAction]:
        """Apply decided mitigation actions, update Nginx rules, and write audit records."""
        for action in actions:
            try:
                action.status = ActionStatus.ACTIVE
                self._actions[action.id] = action

                if self._repo is not None:
                    try:
                        self._repo.add(action)
                    except NotImplementedError:
                        pass

                self._audit.record(
                    event_type="ACTION_APPLIED",
                    details={
                        "action_type": action.action_type.value,
                        "target": action.target,
                        "risk_level": action.risk_level,
                        "reason": action.reason,
                    },
                    action_id=action.id,
                )
            except Exception as exc:
                action.status = ActionStatus.FAILED
                self._audit.record(
                    event_type="ACTION_FAILED",
                    details={"error": str(exc), "target": action.target},
                    action_id=action.id,
                )

        if actions:
            self._sync_nginx()

        return actions

    def expire_due(self, now: datetime) -> list[MitigationAction]:
        """Expire all ACTIVE actions whose expires_at <= now."""
        active_list = [
            a for a in self._actions.values() if a.status == ActionStatus.ACTIVE
        ]
        expired = find_expired(active_list, now=now)

        for action in expired:
            action.status = ActionStatus.EXPIRED
            if self._repo is not None:
                try:
                    self._repo.update_status(action.id, ActionStatus.EXPIRED)
                except NotImplementedError:
                    pass

            self._audit.record(
                event_type="ACTION_EXPIRED",
                details={
                    "action_type": action.action_type.value,
                    "target": action.target,
                },
                action_id=action.id,
            )

        if expired:
            self._sync_nginx()

        return expired

    def rollback(self, action_id: str, actor: str = "operator") -> MitigationAction:
        """Manually roll back an ACTIVE action before its TTL expires."""
        if action_id not in self._actions:
            raise KeyError(f"MitigationAction '{action_id}' not found.")

        action = self._actions[action_id]
        action.status = ActionStatus.ROLLED_BACK

        if self._repo is not None:
            try:
                self._repo.update_status(action.id, ActionStatus.ROLLED_BACK)
            except NotImplementedError:
                pass

        self._audit.record(
            event_type="ACTION_ROLLED_BACK",
            details={
                "action_type": action.action_type.value,
                "target": action.target,
                "rolled_back_by": actor,
            },
            action_id=action.id,
        )
        self._sync_nginx()
        return action