import json
import base64
import io
import google.generativeai as genai
from PIL import Image

def get_initial_assessment(api_key, photo_b64, disease_name, confidence):
    """
    Sends the initial plant photo to Gemini for a baseline health assessment.
    """
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-3.6-flash')
        
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
        response = model.generate_content([prompt, image])
        text = response.text.strip()
        if text.startswith('```json'):
            text = text[7:]
        elif text.startswith('```'):
            text = text[3:]
        if text.endswith('```'):
            text = text[:-3]
        
        return json.loads(text.strip())
    except Exception as e:
        return {
            'health_score': 50,
            'status_label': 'Unknown',
            'ai_notes': f'Error assessing image: {str(e)}',
            'next_checkin_days': 3
        }

def analyze_progress(api_key, prev_photo_b64, curr_photo_b64, disease_name, prev_score, treatment_history):
    """
    Sends previous and current plant photos to Gemini to assess progress.
    """
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-3.6-flash')
        
        prev_image_data = base64.b64decode(prev_photo_b64)
        prev_image = Image.open(io.BytesIO(prev_image_data))
        
        curr_image_data = base64.b64decode(curr_photo_b64)
        curr_image = Image.open(io.BytesIO(curr_image_data))
        
        prompt = f"""
You are an expert plant pathologist. Please analyze the two provided images of a plant undergoing treatment for '{disease_name}'.
The first image is the previous state (score: {prev_score}). The second image is the current state.
Treatment history: {treatment_history}
Compare the two images and assess the progress. Respond ONLY with a valid JSON object. Do not include markdown formatting or code blocks.
The JSON object must have exactly the following keys and data types:
- "health_score": an integer between 0 and 100 representing the current overall plant health.
- "status_label": a string, must be one of: "improving", "stable", "worsening", or "recovered".
- "ai_notes": a string containing brief observations on the changes.
- "treatment_adjustments": a string containing suggestions for adjusting treatment based on progress.
- "next_checkin_days": an integer between 2 and 14 representing recommended days until next check-in.
"""
        response = model.generate_content([prompt, "Image 1 (Previous):", prev_image, "Image 2 (Current):", curr_image])
        text = response.text.strip()
        if text.startswith('```json'):
            text = text[7:]
        elif text.startswith('```'):
            text = text[3:]
        if text.endswith('```'):
            text = text[:-3]
        
        return json.loads(text.strip())
    except Exception as e:
        return {
            'health_score': prev_score,
            'status_label': 'stable',
            'ai_notes': f'Error analyzing progress: {str(e)}',
            'treatment_adjustments': 'Continue current treatment',
            'next_checkin_days': 7
        }
