import sys, base64, io
from PIL import Image
sys.path.insert(0, 'd:/AgriSage/main')
from agrisage.gemini_tracker import get_initial_diagnosis
from agrisage.disease_map import DISEASE_DISPLAY_MAP

secrets_path = 'd:/AgriSage/main/.streamlit/secrets.toml'
gemini_key = None
with open(secrets_path, 'r') as f:
    for line in f:
        if 'GEMINI_API_KEY' in line:
            gemini_key = line.split('=')[1].strip().strip('"').strip("'")
            break

img = Image.new('RGB', (100, 100), color='green')
buffer = io.BytesIO()
img.save(buffer, format='JPEG')
photo_b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')

print('Testing REST implementation...')
allowed_classes = list(DISEASE_DISPLAY_MAP.keys())
res = get_initial_diagnosis(gemini_key, photo_b64, allowed_classes)
print('Result:', res)
