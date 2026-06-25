"""
Configuration management for Enterprise Digital COO
"""
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, DotEnvSettingsSource, EnvSettingsSource
from typing import Optional, Tuple, Type


class Settings(BaseSettings):
    """Application settings"""

    # Application
    APP_NAME: str = "Enterprise Digital COO"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"

    # API
    API_V1_PREFIX: str = "/api/v1"
    HOST: str = "0.0.0.0"
    PORT: int = 8001

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
    ]

    # Database - PostgreSQL
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = ""          # Set via POSTGRES_PASSWORD env var or .env
    POSTGRES_HOST: str = "127.0.0.1"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "enterprise_coo"
    
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    @property
    def SYNC_DATABASE_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    # ChromaDB - Vector Database
    CHROMADB_HOST: str = "localhost"
    CHROMADB_PORT: int = 8000
    CHROMADB_PERSIST_DIR: str = "./chroma_data"
    
    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    
    @property
    def REDIS_URL(self) -> str:
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    # ChromaDB
    CHROMA_HOST: str = "localhost"
    CHROMA_PORT: int = 8001
    CHROMA_PERSIST_DIRECTORY: str = "./chroma_data"
    
    # OpenAI
    OPENAI_API_KEY: str = "your-openai-api-key"
    OPENAI_MODEL: str = "gpt-4"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-ada-002"
    OPENAI_TEMPERATURE: float = 0.7
    OPENAI_MAX_TOKENS: int = 2000
    
    # LangSmith (Optional - for tracing)
    LANGCHAIN_TRACING_V2: bool = False
    LANGCHAIN_API_KEY: Optional[str] = None
    LANGCHAIN_PROJECT: str = "enterprise-digital-coo"
    
    # Agent Configuration
    AGENT_TIMEOUT_SECONDS: int = 300
    AGENT_MAX_RETRIES: int = 3
    AGENT_PARALLEL_EXECUTION: bool = True
    
    # Anomaly Detection
    ANOMALY_DETECTION_THRESHOLD: float = 0.85
    ANOMALY_CONFIDENCE_THRESHOLD: float = 0.75
    STATISTICAL_SIGNIFICANCE_LEVEL: float = 0.05
    
    # Simulation
    MONTE_CARLO_ITERATIONS: int = 10000
    SIMULATION_TIME_HORIZON_DAYS: int = 90
    
    # Memory
    MEMORY_MAX_RESULTS: int = 10
    MEMORY_SIMILARITY_THRESHOLD: float = 0.7
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000
    
    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    # Monitoring
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 9090
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        # Ignore env vars whose values cannot be coerced to the field type
        # (e.g. Windows system var DEBUG=release).  The .env file value wins.
        "env_ignore_empty": False,
        "extra": "ignore",
    }

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        **kwargs,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        """Prioritise .env file over OS environment variables.

        Order: init > dotenv (.env file) > OS env vars
        This ensures DEBUG=true in .env wins over DEBUG=release in the Windows
        system environment.
        """
        return init_settings, dotenv_settings, env_settings


def get_settings() -> Settings:
    """Get settings instance (cache removed for hot reload)"""
    return Settings()


# Global settings instance
settings = get_settings()

# Made with Bob
