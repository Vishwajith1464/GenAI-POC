from pydantic import SecretStr, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", frozen=True, str_strip_whitespace=True)
    gemini_api_key: SecretStr = Field(min_length = 1)
    gemini_model_name: str = "gemini-3.8-flash"



def load_settings() -> Settings:  
    return Settings()