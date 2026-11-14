import time
import httpx

BASE_URL = "http://127.0.0.1:8001"


def run_all_tests():
    print("=" * 60)
    print("CLOUDSHIELD — AUTOMATED PROTECTION & RECOVERY TEST SUITE")
    print("=" * 60)

    with httpx.Client(base_url=BASE_URL, timeout=10.0) as client:
        # 1. Check Server Health
        res = client.get("/")
        assert res.status_code == 200, "Server is not running on port 8001!"
        print("[PASS] 1. Protection Engine API is ONLINE.")

        # 2. Normal Website Traffic (LOW Risk)
        res = client.post("/api/v1/mitigate", json={
            "source_ip": "198.51.100.10",
            "endpoint": "/products",
            "risk_score": 12.5,
            "risk_level": "LOW",
            "attack_type": "NONE",
            "requests_per_second": 1.2
        })
        assert res.json()["action_taken"] == "ALLOW"
        print("[PASS] 2. Normal traffic (LOW risk) -> ALLOW.")

        # 3. Legitimate Spike / Subtle Traffic (MEDIUM Risk -> Rate Limit, not Block)
        res = client.post("/api/v1/mitigate", json={
            "source_ip": "198.51.100.20",
            "endpoint": "/search",
            "risk_score": 55.0,
            "risk_level": "MEDIUM",
            "attack_type": "LOW_RATE_PERSISTENT",
            "requests_per_second": 14.0
        })
        assert res.json()["action_taken"] == "RATE_LIMIT"
        print("[PASS] 3. Medium risk traffic -> RATE_LIMIT (prevents false blocking).")

        # 4. Single-Source Burst Attack (HIGH Risk -> Temporary Block)
        start_mitigation = time.perf_counter()
        res = client.post("/api/v1/mitigate", json={
            "source_ip": "198.51.100.43",
            "endpoint": "/login",
            "risk_score": 88.0,
            "risk_level": "HIGH",
            "attack_type": "SINGLE_SOURCE_BURST",
            "requests_per_second": 95.0
        })
        mitigation_ms = round((time.perf_counter() - start_mitigation) * 1000, 2)
        assert res.json()["action_taken"] == "TEMPORARY_BLOCK"
        print(f"[PASS] 4. High risk attack -> TEMPORARY_BLOCK in {mitigation_ms} ms.")

        # 5. Duplicate Alert Safeguard (Idempotency)
        res = client.post("/api/v1/mitigate", json={
            "source_ip": "198.51.100.43",
            "endpoint": "/login",
            "risk_score": 91.0,
            "risk_level": "HIGH",
            "attack_type": "SINGLE_SOURCE_BURST"
        })
        assert res.json()["action_taken"] == "ALREADY_MITIGATED"
        print("[PASS] 5. Duplicate alert ignored cleanly -> ALREADY_MITIGATED.")

        # 6. Distributed HTTP Flood (Multiple Attacking IPs)
        bot_ips = ["198.51.100.101", "198.51.100.102", "198.51.100.103"]
        for ip in bot_ips:
            r = client.post("/api/v1/mitigate", json={
                "source_ip": ip,
                "endpoint": "/checkout",
                "risk_score": 96.0,
                "risk_level": "CRITICAL",
                "attack_type": "DISTRIBUTED_HTTP_FLOOD",
                "requests_per_second": 150.0
            })
            assert r.json()["action_taken"] == "TEMPORARY_BLOCK"
        print(f"[PASS] 6. Distributed flood across {len(bot_ips)} IPs blocked.")

        # 7. Anti-False-Positive Whitelist Safeguard
        res = client.post("/api/v1/mitigate", json={
            "source_ip": "127.0.0.1",
            "endpoint": "/",
            "risk_score": 99.0,
            "risk_level": "CRITICAL",
            "attack_type": "HTTP_FLOOD"
        })
        assert res.json()["action_taken"] == "ALLOW"
        print("[PASS] 7. Whitelisted IP (127.0.0.1) protected from self-lockout.")

        # 8. Rollback / Unblock Verification
        res = client.delete("/api/v1/mitigations/198.51.100.43")
        assert res.status_code == 200
        print("[PASS] 8. Manual/Expiry rollback restored access for 198.51.100.43.")

        # 9. Automated Container Crash & Recovery Test
        print("\n[INFO] Injecting simulated crash into 'cloudshield_web_1'...")
        res = client.post("/api/v1/recovery/simulate-crash/cloudshield_web_1")
        assert res.status_code == 200

        print("[INFO] Waiting ~16 seconds for 3 background health checks (every 5s)...")
        time.sleep(16)

        status_res = client.get("/api/v1/recovery/status").json()
        web1 = next(c for c in status_res if c["container_name"] == "cloudshield_web_1")
        assert web1["status"] == "HEALTHY"
        print(f"[PASS] 9. Container 'cloudshield_web_1' auto-recovered! Status: {web1['status']} | {web1['message']}")

    print("\n" + "=" * 60)
    print("ALL 9 VERIFICATION TESTS PASSED SUCCESSFULLY!")
    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()