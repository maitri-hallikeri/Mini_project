import time
import statistics
import httpx

BASE_URL = "http://127.0.0.1:8001"


def generate_evaluation_report():
    mitigation_latencies_ms = []
    benign_total = 80
    benign_allowed = 0
    false_blocks = 0
    attack_total = 20
    attack_mitigated = 0

    with httpx.Client(base_url=BASE_URL, timeout=10.0) as client:
        # 1. Test 80 Benign Users
        for i in range(benign_total):
            ip = f"203.0.113.{i + 1}"
            t0 = time.perf_counter()
            res = client.post("/api/v1/mitigate", json={
                "source_ip": ip,
                "endpoint": "/api/items",
                "risk_score": 15.0,
                "risk_level": "LOW",
                "attack_type": "NONE"
            }).json()
            mitigation_latencies_ms.append((time.perf_counter() - t0) * 1000)

            if res["action_taken"] == "ALLOW":
                benign_allowed += 1
            elif res["action_taken"] == "TEMPORARY_BLOCK":
                false_blocks += 1

        # 2. Test 20 Attacking Sources
        for i in range(attack_total):
            ip = f"198.51.100.{i + 50}"
            t0 = time.perf_counter()
            res = client.post("/api/v1/mitigate", json={
                "source_ip": ip,
                "endpoint": "/login",
                "risk_score": 90.0,
                "risk_level": "HIGH",
                "attack_type": "HTTP_FLOOD"
            }).json()
            mitigation_latencies_ms.append((time.perf_counter() - t0) * 1000)

            if res["action_taken"] in ["TEMPORARY_BLOCK", "RATE_LIMIT"]:
                attack_mitigated += 1

        # 3. Fetch Recovery History from Server
        rec_history = client.get("/api/v1/recovery/history").json()
        total_recoveries = len(rec_history)
        successful_recoveries = sum(1 for r in rec_history if r["success"])
        avg_recovery_time = (
            round(statistics.mean(r["recovery_time_seconds"] for r in rec_history), 3)
            if total_recoveries > 0 else 0.0
        )
        recovery_success_pct = (
            round((successful_recoveries / total_recoveries) * 100, 2)
            if total_recoveries > 0 else 100.0
        )

    avg_mitigation_ms = round(statistics.mean(mitigation_latencies_ms), 2)
    legit_success_rate = round((benign_allowed / benign_total) * 100, 2)
    availability_pct = round(((benign_allowed + attack_mitigated) / (benign_total + attack_total)) * 100, 2)

    print("\n" + "=" * 62)
    print("CLOUDSHIELD — MODULE F PERFORMANCE EVALUATION REPORT")
    print("=" * 62)
    print(f"1. Average Mitigation Response Time : {avg_mitigation_ms} ms")
    print(f"2. Average Container Recovery Time   : {avg_recovery_time} s")
    print(f"3. Legitimate Request Success Rate   : {legit_success_rate}% ({benign_allowed}/{benign_total})")
    print(f"4. Total Mitigation Actions Executed : {attack_mitigated}")
    print(f"5. False Blocking Incidents          : {false_blocks}")
    print(f"6. System Availability Under Load    : {availability_pct}%")
    print(f"7. Successful Recovery Percentage    : {recovery_success_pct}%")
    print("=" * 62)


if __name__ == "__main__":
    generate_evaluation_report()