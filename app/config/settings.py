from functools import lru_cache
import os

from dotenv import load_dotenv


load_dotenv()


class Settings:
    app_name: str = os.getenv("APP_NAME", "VentureLens AI")
    app_env: str = os.getenv("APP_ENV", "dev")
    app_host: str = os.getenv("APP_HOST", "0.0.0.0")
    app_port: int = int(os.getenv("PORT", os.getenv("APP_PORT", "8000")))

    embedding_model: str = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")

    qdrant_url: str = os.getenv("QDRANT_URL", "")
    qdrant_api_key: str = os.getenv("QDRANT_API_KEY", "")
    qdrant_collection: str = os.getenv("QDRANT_COLLECTION", "venturelens_docs")
    qdrant_local_path: str = os.getenv("QDRANT_LOCAL_PATH", ":memory:")

    llama_cloud_api_key: str = os.getenv("LLAMA_CLOUD_API_KEY", "")

    request_timeout_seconds: float = float(os.getenv("REQUEST_TIMEOUT_SECONDS", "20"))
    request_verify_ssl: bool = os.getenv("REQUEST_VERIFY_SSL", "false").lower() in {"1", "true", "yes"}

    max_chunk_size: int = int(os.getenv("MAX_CHUNK_SIZE", "800"))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "120"))


@lru_cache
def get_settings() -> Settings:
    return Settings()
