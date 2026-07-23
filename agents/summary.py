from src.llm import groq_client
from src.models import FAST_MODEL
from src.prompts import SUMMARY_PROMPT


class SummaryAgent:
    """
    Handles summarization requests.
    """

    def run(self, message: str) -> str:

        response = groq_client.chat.completions.create(
            model=FAST_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": SUMMARY_PROMPT,
                },
                {
                    "role": "user",
                    "content": message,
                },
            ],
            temperature=0,
            max_tokens=200,
        )

        return response.choices[0].message.content.strip()