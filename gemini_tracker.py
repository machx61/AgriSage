import json
import base64
import io
import google.generativeai as genai
from PIL import Image

def get_initial_diagnosis(api_key, photo_b64, allowed_classes):
    """
    Sends a leaf photo to Gemini to classify it via the modern google.genai API.
    """
    from google import genai
    from google.genai import types
    import io, base64
    from PIL import Image
    
    try:
        client = genai.Client(api_key=api_key)
        
        image_data = base64.b64decode(photo_b64)
        image = Image.open(io.BytesIO(image_data))
        
        prompt = f"""
You are an expert plant pathologist. Analyze this leaf image and identify the crop and disease.

Here is a list of known database keys for reference:
{', '.join(allowed_classes)}

If the plant and disease exactly match one of these known keys, please use that exact key.
If it is a completely different disease or crop not on this list, output a descriptive lowercase string in the format 'crop_disease_name' (e.g., 'lemon_sooty_mold').

Respond ONLY with a valid JSON object. Do not include markdown formatting or code blocks.
The JSON object must have exactly the following keys:
- "class": the disease identifier string.
- "confidence": an integer between 0 and 100 representing your confidence.
"""
        
        response = client.models.generate_content(
            model='gemini-3.5-flash-lite',
            contents=[prompt, image],
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        
        text = response.text.strip()
        
        if text.startswith('```json'):
            text = text[7:]
        elif text.startswith('```'):
            text = text[3:]
        if text.endswith('```'):
            text = text[:-3]
        
        return json.loads(text.strip())
    except Exception as e:
        error_msg = str(e)
        print(f"GEMINI DIAGNOSIS ERROR: {repr(e)}")
        return {
            'class': f"error_{error_msg[:30]}",
            'confidence': 0
        }

def get_initial_assessment(api_key, photo_b64, disease_name, confidence):
    """
    Sends the initial plant photo to Gemini for a baseline health assessment via modern google.genai API.
    """
    from google import genai
    from google.genai import types
    import io, base64
    from PIL import Image
    
    try:
        client = genai.Client(api_key=api_key)
        
        image_data = base64.b64decode(photo_b64)
        image = Image.open(io.BytesIO(image_data))
        
        prompt = f"""
You are an expert plant pathologist. Please analyze the provided image of a plant diagnosed with '{disease_name}' (Confidence: {confidence:.2f}).
Provide a baseline health assessment. Respond ONLY with a valid JSON object. Do not include markdown formatting or code blocks.
The JSON object must have exactly the following keys and data types:
- "health_score": an integer between 0 and 100 representing overall plant health (100 is perfectly healthy).
- "status_label": a string summarizing the status (e.g., "Critical", "Moderate", "Mild").
- "ai_notes": a string containing brief observations.
- "next_checkin_days": an integer representing the recommended number of days until the next check-in.
"""
        response = client.models.generate_content(
            model='gemini-3.5-flash-lite',
            contents=[prompt, image],
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        
        text = response.text.strip()
        if text.startswith('```json'):
            text = text[7:]
        elif text.startswith('```'):
            text = text[3:]
        if text.endswith('```'):
            text = text[:-3]
        
        return json.loads(text.strip())
    except Exception as e:
        print(f"GEMINI TRACKER ERROR: {repr(e)}")
        return {
            'health_score': 50,
            'status_label': 'Unknown',
            'ai_notes': f'Error assessing image: {str(e)}',
            'next_checkin_days': 3
        }

def analyze_progress(api_key, prev_photo_b64, curr_photo_b64, disease_name, prev_score, treatment_history):
    """
    Sends previous and current plant photos to Gemini to assess progress via modern google.genai API.
    """
    from google import genai
    from google.genai import types
    import io, base64
    from PIL import Image
    
    try:
        client = genai.Client(api_key=api_key)
        
        prev_image_data = base64.b64decode(prev_photo_b64)
        prev_image = Image.open(io.BytesIO(prev_image_data))
        
        curr_image_data = base64.b64decode(curr_photo_b64)
        curr_image = Image.open(io.BytesIO(curr_image_data))
        
        prompt = f"""
You are an expert plant pathologist. Please analyze the two provided images of a plant undergoing treatment for '{disease_name}'.
Image 1 is the baseline (previous state with health score {prev_score}/100).
Image 2 is the current state.
The patient has been following this treatment plan: {treatment_history}

Provide a progress assessment. Respond ONLY with a valid JSON object. Do not include markdown formatting or code blocks.
The JSON object must have exactly the following keys and data types:
- "health_score": an integer (0-100) representing the CURRENT overall plant health.
- "status_label": exactly one of these strings: "improving", "stable", "worsening", "recovered".
- "ai_notes": a string comparing the two images and noting any changes.
- "treatment_adjustments": a string with brief, specific recommendations (e.g., "Continue plan", "Increase watering", "Try copper fungicide").
- "next_checkin_days": an integer (2-14) representing days until the next check-in.
"""
        response = client.models.generate_content(
            model='gemini-3.5-flash-lite',
            contents=[prompt, prev_image, curr_image],
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        
        text = response.text.strip()
        if text.startswith('```json'):
            text = text[7:]
        elif text.startswith('```'):
            text = text[3:]
        if text.endswith('```'):
            text = text[:-3]
        
        return json.loads(text.strip())
    except Exception as e:
        print(f"GEMINI PROGRESS ERROR: {repr(e)}")
        return {
            'health_score': prev_score,
            'status_label': 'stable',
            'ai_notes': f'Error comparing images: {str(e)}',
            'treatment_adjustments': 'Please consult manual treatments.',
            'next_checkin_days': 3
        }
