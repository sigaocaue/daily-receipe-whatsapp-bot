from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = Field(..., description="PostgreSQL async connection string")
    DATABASE_USE_SSL: bool = Field(default=True, description="Enable SSL for database connection")

    # Twilio
    TWILIO_ACCOUNT_SID: str = Field(..., description="Twilio Account SID")
    TWILIO_AUTH_TOKEN: str = Field(..., description="Twilio Auth Token")
    TWILIO_WHATSAPP_FROM: str = Field(..., description="Twilio WhatsApp sender number")
    TWILIO_CONTENT_SID: str = Field(default="", description="Twilio Content Template SID for WhatsApp")

    # OpenAI
    OPENAI_API_KEY: str = Field(..., description="OpenAI API key")

    # Gemini
    GEMINI_API_KEY: str = Field(..., description="Google Gemini API key")

    # Unsplash
    UNSPLASH_ACCESS_KEY: str = Field(..., description="Unsplash API access key")

    # AI Provider
    AI_PROVIDER: str = Field(default="gemini", description="AI provider to use: 'gemini' or 'openai'")

    # TudoGostoso Scraper
    TUDO_GOSTOSO_SCRAPER_URL: str = Field(
        default="https://daily-receipe-web-scraping.vercel.app/api/receita",
        description="URL of the TudoGostoso recipe scraper API",
    )

    # App
    APP_ENV: str = Field(default="development", description="Application environment")
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    CORS_ALLOW_ORIGINS: str = Field(
        default=(
            "https://sigaocaue-daily-receipe.netlify.app,"
            "http://localhost:3000,"
            "http://localhost:5173"
        ),
        description="Comma-separated list of allowed CORS origins",
    )

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore",
    }


settings = Settings()
