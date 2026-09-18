import sys, base64, io
from PIL import Image
sys.path.insert(0, 'd:/AgriSage/main')
from agrisage.disease_map import DISEASE_DISPLAY_MAP
import google.generativeai as genai

secrets_path = 'd:/AgriSage/main/.streamlit/secrets.toml'
gemini_key = None
with open(secrets_path, 'r') as f:
    for line in f:
        if 'GEMINI_API_KEY' in line:
            gemini_key = line.split('=')[1].strip().strip('"').strip("'")
            break

genai.configure(api_key=gemini_key)
model = genai.GenerativeModel('gemini-flash-latest')

img = Image.new('RGB', (100, 100), color = 'green')
buffer = io.BytesIO()
img.save(buffer, format='PNG')

print('Testing gemini-flash-latest...')
try:
    response = model.generate_content(['What is this?', Image.open(io.BytesIO(buffer.getvalue()))])
    print('Result:', response.text)
except Exception as e:
    print('Error:', e)
