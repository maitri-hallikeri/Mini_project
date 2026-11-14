from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Project metadata
    PROJECT_NAME: str = "CLOUDSHIELD Protection & Recovery Engine"
    VERSION: str = "1.0.0"

    # Risk-based Mitigation Durations (in seconds)
    MEDIUM_RISK_LIMIT_SECONDS: int = 120     # 2 minutes rate-limiting
    HIGH_RISK_BLOCK_SECONDS: int = 300       # 5 minutes temporary block
    CRITICAL_RISK_BLOCK_SECONDS: int = 900   # 15 minutes temporary block

    # Anti-False-Positive Safeguards
    WHITELISTED_IPS: list[str] = ["127.0.0.1", "::1"]  # Never block localhost/admin

    # Automated Recovery Settings
    HEALTH_CHECK_INTERVAL_SECONDS: int = 5   # Check container health every 5s
    FAILURE_THRESHOLD: int = 3               # Restart container after 3 consecutive fails
    TARGET_CONTAINERS: list[str] = [
        "cloudshield_web_1",
        "cloudshield_web_2"
    ]

settings = Settings()