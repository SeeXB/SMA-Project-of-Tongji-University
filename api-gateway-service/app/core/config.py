from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    gateway_title: str = "Canvas AI Unified Gateway"
    gateway_version: str = "1.0.0"
    course_service_url: str = "http://127.0.0.1:8081"
    assignment_service_url: str = "http://127.0.0.1:8082"
    qa_service_url: str = "http://127.0.0.1:8083"
    moderation_service_url: str = "http://127.0.0.1:8084"
    ai_gateway_service_url: str = "http://127.0.0.1:8000"
    rag_service_url: str = "http://127.0.0.1:8001"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()
