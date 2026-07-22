from src.llm import openrouter_client

response = openrouter_client.chat.completions.create(
    model="openai/gpt-4.1-mini",
    messages=[
        {
            "role": "user",
            "content": "Say Connection successful."
        }
    ],
    max_tokens=50
)

print(response.choices[0].message.content)