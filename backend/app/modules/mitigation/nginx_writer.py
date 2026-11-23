"""
Nginx rule writer — stub implementation.

Owner: Member 2.
# TODO(member2): implement NginxRuleWriter
# TODO(member2): adapt from protection_engine/app/main.py sync_nginx_blocklist()
"""

from __future__ import annotations

from app.modules.mitigation.interfaces import RuleWriter


class NginxRuleWriter(RuleWriter):
    """
    Writes IP blocklist and rate-limit configuration to the Nginx includes
    directory and signals Nginx to reload.

    Args:
        blocklist_path: Absolute path to the Nginx blocklist include file
                        (from ``Settings.NGINX_BLOCKLIST_PATH``).

    TODO(member2): adapt from protection_engine/app/main.py —
    ``sync_nginx_blocklist()`` already shows the write pattern for the deny
    list.  Extend it to handle rate-limit rules too.
    """

    def __init__(self, blocklist_path: str) -> None:
        self._blocklist_path = blocklist_path

    def write_blocklist(self, ips: list[str]) -> None:
        """
        Raises:
            NotImplementedError: TODO(member2): write deny rules to NGINX_BLOCKLIST_PATH.
        """
        raise NotImplementedError(
            "TODO(member2): write 'deny <ip>;' lines to NGINX_BLOCKLIST_PATH "
            "(adapt from protection_engine/app/main.py sync_nginx_blocklist)"
        )

    def write_rate_limits(self, rules: list[dict]) -> None:
        """
        Raises:
            NotImplementedError: TODO(member2): write rate-limit rules to Nginx config.
        """
        raise NotImplementedError(
            "TODO(member2): write rate-limit include file for Nginx"
        )

    def reload(self) -> None:
        """
        Raises:
            NotImplementedError: TODO(member2): send SIGHUP or nginx -s reload.
        """
        raise NotImplementedError(
            "TODO(member2): call 'nginx -s reload' or send SIGHUP to reload config"
        )
