from dataclasses import dataclass
import os


@dataclass(frozen=True)
class Settings:
    postgres_db: str = os.getenv("POSTGRES_DB", "kniha_jazd")
    postgres_user: str = os.getenv("POSTGRES_USER", "kniha_user")
    postgres_password: str = os.getenv("POSTGRES_PASSWORD", "kniha_pass")
    postgres_host: str = os.getenv("POSTGRES_HOST", "localhost")
    postgres_port: str = os.getenv("POSTGRES_PORT", "5432")

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg2://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )


settings = Settings()
