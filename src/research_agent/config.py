import os
from dotenv import load_dotenv

class Settings:
    gemini_api_key: str
    gemini_model_name: str

    def __init__(self, key: str, model: str):
        self.gemini_api_key = key
        self.gemini_model_name = model
            
def load_settings() -> Settings:  
    load_dotenv()
    gemini_api_key = (os.getenv("GEMINI_API_KEY") or "").strip()
    gemini_model_name = (os.getenv("GEMINI_MODEL_NAME") or "gemini-3.5-flash-lite").strip()
    if not gemini_api_key:
        raise ValueError("GEMINI_API_KEY is not set in the environment variables.")
    if not gemini_model_name:
        gemini_model_name = "gemini-3.5-flash-lite"  # Default model name
    return Settings(gemini_api_key, gemini_model_name)