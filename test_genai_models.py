import sys, io
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

models = [
    'gemini-3.5-flash',
    'gemini-3-flash-preview',
    'gemini-omni-1.1-flash',
    'gemini-flash-latest',
]

for m in models:
    print(f'Testing {m}...')
    try:
        response = client.models.generate_content(
            model=m,
            contents=['What is this?', img]
        )
        print('  Success! Result:', response.text[:50])
    except Exception as e:
        print('  Failed:', e)

