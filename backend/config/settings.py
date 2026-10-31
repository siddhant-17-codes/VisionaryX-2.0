from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    google_api_key: str
    huggingfacehub_api_token: str
    # Cloudflare Workers AI, the first image provider. Unset = Hugging Face only.
    cloudflare_account_id: str = ""
    cloudflare_api_token: str = ""
    allowed_origins: str = "http://localhost:5173"
    supabase_url: str = ""
    supabase_service_key: str = ""
    # Tried in order; the next model is used when one is out of quota, overloaded or
    # gone. Each model has its own free-tier quota.
    gemini_models: str = "gemini-2.5-flash,gemini-3.5-flash-lite,gemini-3.1-flash-lite"
    # Suggested questions after an upload: lite models only, so they never use the
    # main model's quota.
    gemini_suggest_models: str = "gemini-3.5-flash-lite,gemini-3.1-flash-lite"
    # Proxies that append to X-Forwarded-For when CF-Connecting-IP is absent.
    trusted_proxy_hops: int = 1

    @property
    def origins_list(self) -> list[str]:
        # Browsers send the origin without a trailing slash, so "https://x.app/" would never match.
        return [o.strip().rstrip("/") for o in self.allowed_origins.split(",") if o.strip()]

    @property
    def gemini_model_list(self) -> list[str]:
        return [m.strip() for m in self.gemini_models.split(",") if m.strip()]

    @property
    def gemini_suggest_model_list(self) -> list[str]:
        return [m.strip() for m in self.gemini_suggest_models.split(",") if m.strip()]

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    return Settings()
