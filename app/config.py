from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "mysql+pymysql://root:password@localhost:3306/biblioteca"
    secret_key: str = "dev-secret-key-change-in-production"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
