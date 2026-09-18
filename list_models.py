import google.generativeai as genai
secrets_path = 'd:/AgriSage/main/.streamlit/secrets.toml'
gemini_key = None
with open(secrets_path, 'r') as f:
    for line in f:
        if 'GEMINI_API_KEY' in line:
            gemini_key = line.split('=')[1].strip().strip('"').strip("'")
            break

genai.configure(api_key=gemini_key)
print("Listing models...")
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(m.name)

