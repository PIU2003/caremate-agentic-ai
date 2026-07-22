
from src.llm import groq_client
from src.models import FAST_MODEL
from src.prompts import COORDINATOR_PROMPT


class CoordinatorAgent:
    """
    Routes user requests to the correct specialized agent.
    """

    def route(self, message: str) -> str:
        response = groq_client.chat.completions.create(
            model=FAST_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": COORDINATOR_PROMPT,
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