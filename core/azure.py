import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from .schema import MeetingAnalysis
from .prompt import SYSTEM_PROMPT

BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables
load_dotenv(BASE_DIR / ".env", override=True)

AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21")

def validate_config():
    missing = []
    if not AZURE_OPENAI_ENDPOINT:
        missing.append("AZURE_OPENAI_ENDPOINT")
    if not AZURE_OPENAI_API_KEY:
        missing.append("AZURE_OPENAI_API_KEY")
    if not AZURE_OPENAI_DEPLOYMENT:
        missing.append("AZURE_OPENAI_DEPLOYMENT")

    if missing:
        raise ValueError(f"Missing required environment variables in .env: {', '.join(missing)}")

def get_client() -> OpenAI:
    validate_config()
    return OpenAI(
        base_url=AZURE_OPENAI_ENDPOINT,
        api_key=AZURE_OPENAI_API_KEY
    )

def analyze_meeting(meeting_text: str) -> MeetingAnalysis:
    client = get_client()
    response = client.beta.chat.completions.parse(
        model=AZURE_OPENAI_DEPLOYMENT,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": meeting_text}
        ],
        response_format=MeetingAnalysis
    )

    result = response.choices[0].message.parsed
    if result is None:
        raise ValueError("Azure OpenAI did not return a structured response.")
    return result
