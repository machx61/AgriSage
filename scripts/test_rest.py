import sys, base64, io, requests, json
from PIL import Image

secrets_path = 'd:/AgriSage/main/.streamlit/secrets.toml'
gemini_key = None
with open(secrets_path, 'r') as f:
    for line in f:
        if 'GEMINI_API_KEY' in line:
            gemini_key = line.split('=')[1].strip().strip('"').strip("'")
            break

img = Image.new('RGB', (100, 100), color='green')
buffer = io.BytesIO()
img.save(buffer, format='PNG')
b64_img = base64.b64encode(buffer.getvalue()).decode('utf-8')

url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.5-flash:generateContent?key={gemini_key}"
headers = {'Content-Type': 'application/json'}
payload = {
    "contents": [{
        "parts": [
            {"text": "What is this?"},
            {"inline_data": {"mime_type": "image/png", "data": b64_img}}
        ]
    }]
}

print('Calling REST API...')
response = requests.post(url, headers=headers, json=payload)
print(response.status_code)
print(response.text)
