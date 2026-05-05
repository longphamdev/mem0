import json
import logging
import os
import re
from typing import List

from app.utils.prompts import MEMORY_CATEGORIZATION_PROMPT
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential

load_dotenv()

# Lazy-load OpenAI client to avoid credentials error at import time
_openai_client = None

def _get_openai_client():
    """Get OpenAI client using CHAT_LLM_* env vars for the MiniMax-compatible endpoint."""
    global _openai_client
    if _openai_client is None:
        from openai import OpenAI
        api_key = os.environ.get('CHAT_LLM_API_KEY', '')
        base_url = os.environ.get('CHAT_LLM_BASE_URL')

        _openai_client = OpenAI(api_key=api_key, base_url=base_url)
    return _openai_client


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=15))
def get_categories_for_memory(memory: str) -> List[str]:
    """Get categories for a memory using the CHAT_LLM provider.

    Uses regular chat completions instead of beta.parse to support
    OpenAI-compatible providers like MiniMax that may not support
    structured output with Pydantic response_format.
    """
    try:
        openai_client = _get_openai_client()
        model = os.environ.get('CHAT_LLM_MODEL', 'gpt-4o-mini')
        messages = [
            {"role": "system", "content": MEMORY_CATEGORIZATION_PROMPT},
            {"role": "user", "content": memory}
        ]

        completion = openai_client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0
        )

        response_text = completion.choices[0].message.content

        # Try to parse as JSON array first
        try:
            categories = json.loads(response_text)
            if isinstance(categories, list):
                return [cat.strip().lower() for cat in categories]
        except json.JSONDecodeError:
            pass

        # Try to extract JSON from markdown code blocks
        json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', response_text)
        if json_match:
            try:
                categories = json.loads(json_match.group(1))
                if isinstance(categories, list):
                    return [cat.strip().lower() for cat in categories]
            except json.JSONDecodeError:
                pass

        # Fallback: try to find any JSON array in the response
        array_match = re.search(r'\[\s*"[^"]*"(?:\s*,\s*"[^"]*")*\s*\]', response_text)
        if array_match:
            try:
                categories = json.loads(array_match.group(0))
                return [cat.strip().lower() for cat in categories]
            except json.JSONDecodeError:
                pass

        logging.warning(f"[WARN] Could not parse categories from response: {response_text}")
        return []

    except Exception as e:
        logging.error(f"[ERROR] Failed to get categories: {e}")
        raise
