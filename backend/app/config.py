"""Application configuration."""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "煤矿技改概算管控系统"
    APP_VERSION: str = "1.0.0"
    DATABASE_URL: str = "sqlite+aiosqlite:///./coal_mine_budget.db"
    SECRET_KEY: str = "pingmei-shenma-taneng-isfara-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480  # 8 hours

    # Server settings (Render.com injects PORT env var)
    PORT: int = 8001
    CORS_ORIGINS: str = "*"  # Comma-separated origins, or "*" for all

    # Budget settings
    TOTAL_BUDGET: float = 56397.84  # 万元
    DEFAULT_RESERVE_RATE: float = 0.07  # 7% default reserve (5%-10% range)

    # Alert thresholds
    ALERT_YELLOW_THRESHOLD: float = 0.80  # 80% budget used = yellow
    ALERT_RED_THRESHOLD: float = 0.90  # 90% budget used = red
    PROGRESS_DELAY_THRESHOLD: float = 0.10  # 10% behind schedule = warning

    @property
    def cors_origin_list(self) -> list[str]:
        """Parse CORS_ORIGINS into a list."""
        if self.CORS_ORIGINS == "*":
            return ["*"]
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    class Config:
        env_file = ".env"


settings = Settings()
