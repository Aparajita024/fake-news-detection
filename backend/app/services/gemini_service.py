# In gemini_service.py (now functioning as an OpenAI service)

import json
import subprocess
import sys
from ..core.config.settings import settings
import os

# --- 1. Package Installation and OpenAI Client Setup ---
def ensure_package_installed():
    try:
        import openai
        return True
    except ImportError:
        print("Installing openai package...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "openai"])
            return True
        except Exception as e:
            print(f"Failed to install openai package: {e}")
            return False

OPENAI_AVAILABLE = ensure_package_installed()
client = None

if OPENAI_AVAILABLE:
    from openai import AsyncOpenAI
    try:
        # Modern client initialization (requires OPENAI_API_KEY to be set in your environment)
        if not settings.GEMINI_API_KEY:
             raise ValueError("OPENAI_API_KEY is not set in your configuration/environment.")
        
        client = AsyncOpenAI(api_key=settings.GEMINI_API_KEY)
        print("OpenAI client configured successfully!")
    except Exception as e:
        print(f"Error configuring OpenAI client: {e}")
        OPENAI_AVAILABLE = False
else:
    print("Warning: openai package is not available.")

# --- 2. The Core Analysis Function (Using modern OpenAI syntax) ---
async def analyze_credibility(text: str) -> dict:
    """
    Analyzes text credibility using OpenAI's GPT API.
    """
    if not OPENAI_AVAILABLE or client is None:
        print("OpenAI is not available. Check API key and package installation.")
        return {"verdict": "Unknown", "explanation": "OpenAI API not available."}

    # Choose a real, available OpenAI model.
    # 'gpt-4o' is powerful and intelligent.
    # 'gpt-3.5-turbo' is faster and cheaper.
    MODEL_NAME = "gpt-4o" 
    
    # This is the system prompt. It tells the AI how to behave.
    system_prompt = """
    You are an expert fact-checker and credibility analyst. Your task is to analyze a given text
    and determine if it is "Real" or "Fake" news. You must respond ONLY with a valid JSON object
    that follows this exact structure:
    {
        "verdict": "Real" or "Fake",
        "confidence": <an integer between 0 and 100 representing your confidence>,
        "explanation": "A concise, detailed explanation for your verdict.",
        "key_indicators": ["A list of 3-4 key phrases or reasons that led to your conclusion"]
    }
    Do not include any text, greetings, or markdown before or after the JSON object.
    """

    try:
        print(f"Sending request to OpenAI model: {MODEL_NAME}")
        
        # This is the modern, correct way to call the API asynchronously
        response = await client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Please analyze this text: \"{text}\""}
            ],
            # This crucial setting forces the model to output valid JSON
            response_format={"type": "json_object"} 
        )
        
        # Extract the JSON content from the response
        analysis_result_str = response.choices[0].message.content
        analysis_result = json.loads(analysis_result_str)
        
        print("Successfully received and parsed response from OpenAI.")
        
        return {
            "verdict": analysis_result.get("verdict", "Unknown"),
            "confidence": int(analysis_result.get("confidence", 0)),
            "explanation": analysis_result.get("explanation", "Analysis incomplete."),
            "key_indicators": analysis_result.get("key_indicators", [])
        }
        
    except Exception as e:
        print(f"OpenAI API Error: {str(e)}")
        # Return a structured error so the fallback logic works correctly
        return {
            "verdict": "Unknown",
            "confidence": 0,
            "explanation": f"Error during OpenAI analysis: {e}",
            "key_indicators": []
        }