"""List the Gemini models available to the key in .streamlit/secrets.toml."""

import tomllib
from pathlib import Path

from google import genai

secrets_path = Path(__file__).resolve().parent.parent / ".streamlit" / "secrets.toml"
api_key = tomllib.loads(secrets_path.read_text(encoding="utf-8"))["GEMINI_API_KEY"]

client = genai.Client(api_key=api_key)
print("Listing models...")
for model in client.models.list():
    if "generateContent" in (model.supported_actions or []):
        print(model.name)
