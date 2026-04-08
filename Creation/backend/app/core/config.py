"""
项目配置（Settings / 配置中心）。

使用 Pydantic Settings（环境配置模型）从环境变量/`.env` 读取配置，并进行类型校验（validation/校验）。
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """应用配置模型（Application settings model / 应用配置模型）。"""
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_url: str
    secret_key: str
    openai_api_key: str = ""
    access_token_expire_minutes: int = 60 * 24
    algorithm: str = "HS256"


settings = Settings()
