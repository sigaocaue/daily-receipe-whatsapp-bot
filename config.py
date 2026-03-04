from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = Field(..., description="PostgreSQL async connection string")

    # Twilio
    TWILIO_ACCOUNT_SID: str = Field(..., description="Twilio Account SID")
    TWILIO_AUTH_TOKEN: str = Field(..., description="Twilio Auth Token")
    TWILIO_WHATSAPP_FROM: str = Field(..., description="Twilio WhatsApp sender number")

    # OpenAI
    OPENAI_API_KEY: str = Field(..., description="OpenAI API key")

    # Unsplash
    UNSPLASH_ACCESS_KEY: str = Field(..., description="Unsplash API access key")

    # App
    APP_ENV: str = Field(default="development", description="Application environment")
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


settings = Settings()
