import os
from langchain_core.rate_limiters import InMemoryRateLimiter
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the API key from the environment variable
groq_api_key = os.getenv("GROQ_API_KEY")

# If the API key is not set, raise an exception
if not groq_api_key:
    raise ValueError("GROQ_API_KEY environment variable not set")

rate_limiter = InMemoryRateLimiter(
    requests_per_second=1,
    check_every_n_seconds=0.5,
    max_bucket_size=10,
)

def get_json_client():
    return ChatOpenAI(
        base_url="https://api.groq.com/openai/v1",
        model="qwen/qwen3-32b",
        api_key=groq_api_key,
        temperature=0,
        rate_limiter=rate_limiter,
        response_format={"type": "json_object"}
    )

def get_client():
    return ChatOpenAI(
        base_url="https://api.groq.com/openai/v1",
        model="qwen/qwen3-32b",
        api_key=groq_api_key,
        temperature=0,
        rate_limiter=rate_limiter,
    )

json_client = get_json_client()
client = get_client()
