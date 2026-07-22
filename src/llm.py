import os
from dotenv import load_dotenv
from groq import Groq
from openai import OpenAI

# Load .env
load_dotenv()

# Read API Keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Create clients
groq_client = Groq(api_key=GROQ_API_KEY)

openrouter_client = OpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1"
)