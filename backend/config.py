from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    tavily_api_key: str = Field("", env="TAVILY_API_KEY")
    app_env: str = Field("development", env="APP_ENV")
    log_level: str = Field("INFO", env="LOG_LEVEL")
    chroma_persist_dir: str = Field("./database/chroma_store", env="CHROMA_PERSIST_DIR")
    sqlite_db_path: str = Field("./database/chat_history.db", env="SQLITE_DB_PATH")
    upload_dir: str = Field("./uploads", env="UPLOAD_DIR")
    max_upload_size_mb: int = Field(20, env="MAX_UPLOAD_SIZE_MB")
    backend_url: str = Field("http://localhost:8000", env="BACKEND_URL")
    model_name: str = Field("gpt-4o", env="MODEL_NAME")

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
