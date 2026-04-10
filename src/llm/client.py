import logging
import os
from typing import Optional

from dotenv import load_dotenv
from openai import OpenAI

logger = logging.getLogger(__name__)

DEFAULT_MODEL_NAME = "gpt-4.1-mini"


def load_environment() -> Optional[str]:
    """Load environment variables and return the OpenAI API key if present."""
    load_dotenv(dotenv_path=".env")
    return os.getenv("OPENAI_API_KEY")


def configure_client(api_key: Optional[str] = None) -> Optional[OpenAI]:
    """Return a configured OpenAI client instance."""
    key = api_key or load_environment()
    if not key:
        logger.error("OPENAI_API_KEY was not found")
        return None

    return OpenAI(api_key=key)


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
    """Send a prompt to OpenAI and return the cleaned text response."""
    logger.info("LLM Call triggered")
    if not prompt or not prompt.strip():
        return None

    client = configure_client()
    if client is None:
        return None

    try:
        response = client.responses.create(
            model=model_name,
            input=prompt,
        )
    
        text = response.output_text
        return clean_response(text)
    except Exception:
        logger.exception("OpenAI call failed for model %s", model_name)
        return None
