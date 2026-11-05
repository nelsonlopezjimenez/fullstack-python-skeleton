"""Settings read from environment variables and .env (Chapter 3: server/config/config.js)."""
from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

DEV_SECRET = "dev-only-secret-do-not-use-in-production"


# [BEGINNER] Each field is one environment variable: `port` reads PORT, `mongodb_uri` reads
# MONGODB_URI (case does not matter). The type annotation converts the text, so PORT=8000
# becomes the int 8000. The value after `=` is the default, like `?? 3000` in config.js.
class Settings(BaseSettings):
    # [BEGINNER] env_file: read .env if it exists (config.js needed Node's --env-file flag).
    # extra="ignore": unrelated variables in .env are not an error.
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    env: str = "development"
    port: int = 8000
    mongodb_uri: str = "mongodb://localhost:27017/pythonskeleton?directConnection=true"
    jwt_secret: str = DEV_SECRET
    # [ADVANCED] jsonwebtoken accepted '1d' / '12h'; PyJWT works with seconds, and the cookie's
    # max_age is in seconds too, so ONE number keeps the token and the cookie in step
    # (Chapter 3 needed JWT_EXPIRES_IN and JWT_COOKIE_MAX_AGE_MS and asked you to keep them equal).
    jwt_expires_in_seconds: int = 24 * 60 * 60
    # Comma-separated origins allowed to call /api from another site. Empty = CORS off.
    cors_origin: str = ""

    @property
    def cors_origins(self) -> list[str]:
        # [BEGINNER] A list comprehension: split, strip each part, keep the non-empty ones.
        # Same as .split(',').map(o => o.trim()).filter(Boolean) in config.js.
        return [origin.strip() for origin in self.cors_origin.split(",") if origin.strip()]

    @property
    def is_production(self) -> bool:
        return self.env == "production"

    # [ADVANCED] Fail fast, as in config.js: a production server must not start with the
    # development secret, which is public on GitHub, because anyone could forge tokens with it.
    @model_validator(mode="after")
    def require_real_secret_in_production(self):
        if self.is_production and self.jwt_secret == DEV_SECRET:
            raise ValueError("JWT_SECRET must be set in production")
        return self


# [BEGINNER] One shared instance, created when the module is first imported
# (like `export default config`). Other modules do `from app.config import settings`.
settings = Settings()
