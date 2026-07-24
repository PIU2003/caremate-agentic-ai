from src.llm import groq_client
from src.models import FAST_MODEL
from src.prompts import HEALTH_PROMPT
from src.prompts import (
    HEALTH_PROMPT,
    HEALTH_INTENT_PROMPT,
)

class HealthAgent:

    def run(self, message: str) -> str:

        response = groq_client.chat.completions.create(
            model=FAST_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": HEALTH_PROMPT,
                },
                {
                    "role": "user",
                    "content": message,
                },
            ],
            temperature=0.2,
            max_tokens=150,
        )

        return response.choices[0].message.content.strip()

    def detect_intent(self, message: str) -> str:

        response = groq_client.chat.completions.create(
        model=FAST_MODEL,
        messages=[
            {
                "role": "system",
                "content": HEALTH_INTENT_PROMPT,
            },
            {
                "role": "user",
                "content": message,
            },
        ],
        temperature=0,
        max_tokens=10,
    )

        return response.choices[0].message.content.strip()