"""SmartSpray backend configuration from environment variables."""

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings loaded from environment / .env file."""

    # App
    app_env: str = Field(default="development")
    app_host: str = Field(default="0.0.0.0")
    app_port: int = Field(default=8000)

    # Database
    database_url: str = Field(default="sqlite+aiosqlite:///./data/smartspray.db")

    # ESP32
    esp32_connection: str = Field(default="mock")  # "serial" or "mock"
    esp32_serial_port: str = Field(default="COM5")
    esp32_baud_rate: int = Field(default=115200)

    # AI
    ai_model_path: str = Field(default="./data/models/best.pt")
    ai_confidence_threshold: float = Field(default=0.50)

    # Severity thresholds
    severity_mild_max: int = Field(default=25)
    severity_moderate_max: int = Field(default=60)

    # Hardware limits
    max_servo_angle: int = Field(default=160)
    min_servo_angle: int = Field(default=20)
    max_pump_duration_ms: int = Field(default=3000)
    min_pump_duration_ms: int = Field(default=100)

    # Command validation
    command_stale_seconds: int = Field(default=30)

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
