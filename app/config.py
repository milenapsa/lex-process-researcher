from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    app_port: int = 8080
    http_timeout_seconds: float = 20.0

    datajud_base_url: str = "https://api-publica.datajud.cnj.jus.br"
    datajud_api_key: str | None = None
    datajud_auto_discover_key: bool = True
    datajud_key_page_url: str = "https://datajud-wiki.cnj.jus.br/api-publica/acesso/"
    datajud_key_cache_seconds: int = 21600
    datajud_default_health_tribunal: str = "tjsc"
    datajud_max_requests_per_minute: int = 100
    datajud_max_concurrency: int = 4

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
