import sys, base64, io, json
from PIL import Image
from google import genai
from google.genai import types

secrets_path = 'd:/AgriSage/main/.streamlit/secrets.toml'
gemini_key = None
with open(secrets_path, 'r') as f:
    for line in f:
        if 'GEMINI_API_KEY' in line:
            gemini_key = line.split('=')[1].strip().strip('"').strip("'")
            break

client = genai.Client(api_key=gemini_key)
img = Image.new('RGB', (100, 100), color='green')

print('Testing genai.Client...')
try:
    response = client.models.generate_content(
        model='gemini-3.6-flash',
        contents=['What is this?', img],
        config=types.GenerateContentConfig(
            response_mime_type='application/json',
        )
    )
    print('Result:', response.text)
except Exception as e:
    print('Error:', e)
