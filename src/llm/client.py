import os
from typing import Optional

import google.generativeai as genai
from dotenv import load_dotenv


DEFAULT_MODEL_NAME = "gemini-2.5-flash"


def load_environment() -> Optional[str]:
    """Load environment variables and return the Gemini API key if present."""
    load_dotenv()
    return os.getenv("GEMINI_API_KEY")


def configure_client(api_key: Optional[str] = None) -> Optional[str]:
    """Configure the Gemini client and return the API key used."""
    key = api_key or load_environment()
    if not key:
        return None

    genai.configure(api_key=key)
    return key


def get_model(model_name: str = DEFAULT_MODEL_NAME) -> genai.GenerativeModel:
    """Return a configured Gemini model instance."""
    return genai.GenerativeModel(model_name)


def clean_response(text: Optional[str]) -> Optional[str]:
    """Remove common markdown code fences from model output."""
    if text is None:
        return None

    cleaned = text.strip()

    if cleaned.startswith("```json"):
        cleaned = cleaned[len("```json"):].strip()
    elif cleaned.startswith("```"):
        cleaned = cleaned[len("```"):].strip()

    if cleaned.endswith("```"):
        cleaned = cleaned[:-3].strip()

    return cleaned


def call_llm(prompt: str, model_name: str = DEFAULT_MODEL_NAME) -> Optional[str]:
    """Send a prompt to Gemini and return the cleaned text response."""
    if not prompt or not prompt.strip():
        return None

    if not configure_client():
        return None

    try:
        model = get_model(model_name)
        response = model.generate_content(prompt)

        text = getattr(response, "text", None)
        return clean_response(text)
    except Exception:
        return None
