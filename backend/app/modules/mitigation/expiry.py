"""
Expiry helper for mitigation actions.

Owner: Member 2.
# TODO(member2): implement expiry scanning logic used by the controller
"""

from __future__ import annotations

from datetime import UTC, datetime

from app.schemas.mitigation import ActionStatus, MitigationAction


def find_expired(
    actions: list[MitigationAction],
    now: datetime | None = None,
) -> list[MitigationAction]:
    """
    Return all ACTIVE actions whose ``expires_at`` is in the past.

    Args:
        actions: Current list of active mitigation actions.
        now:     UTC datetime to compare against.  Defaults to utcnow().

    Returns:
        Subset of ``actions`` that have expired.

    TODO(member2): call this inside ``DefaultMitigationController.expire_due()``.
    """
    if now is None:
        now = datetime.now(UTC)
    return [
        a for a in actions
        if a.status == ActionStatus.ACTIVE
        and a.expires_at is not None
        and a.expires_at <= now
    ]
