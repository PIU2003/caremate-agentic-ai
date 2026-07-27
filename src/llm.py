"""LLM clients and model selection for CareMate AI.

ROUTING_MODEL (Groq): cheap, low-latency classification / reminder parse.
REASONING_MODEL (OpenRouter): stronger answers for health, alerts, planning,
reflection, and summarization.
"""

import os

from dotenv import load_dotenv
from groq import Groq
from openai import OpenAI

load_dotenv()

ROUTING_MODEL = "llama-3.1-8b-instant"
REASONING_MODEL = "meta-llama/llama-3.3-70b-instruct"

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

groq_client = Groq(api_key=GROQ_API_KEY)
openrouter_client = OpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1",
)


def chat(
    messages,
    *,
    model: str | None = None,
    provider: str = "groq",
    temperature: float = 0.2,
    max_tokens: int = 300,
) -> str:
    """
    provider:
      - "groq"       → ROUTING_MODEL by default
      - "openrouter" → REASONING_MODEL by default
    OpenRouter failures fall back to Groq.
    """
    use_openrouter = provider == "openrouter" and bool(OPENROUTER_API_KEY)

    try:
        if use_openrouter:
            selected = model or REASONING_MODEL
            response = openrouter_client.chat.completions.create(
                model=selected,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        else:
            selected = model or ROUTING_MODEL
            response = groq_client.chat.completions.create(
                model=selected,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        return response.choices[0].message.content.strip()
    except Exception:
        if use_openrouter:
            response = groq_client.chat.completions.create(
                model=ROUTING_MODEL,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content.strip()
        raise
