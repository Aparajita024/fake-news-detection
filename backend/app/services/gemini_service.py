import json
from ..core.config import settings
import sys
import subprocess
import os

def ensure_package_installed():
    try:
        import google.generativeai
        return True
    except ImportError:
        print("Installing google-generativeai package...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "google-generativeai"])
            return True
        except Exception as e:
            print(f"Failed to install package: {e}")
            return False

# Try to ensure the package is installed
GEMINI_AVAILABLE = ensure_package_installed()

if GEMINI_AVAILABLE:
    import google.generativeai as genai
    # Configure the Gemini API
    try:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        # Test the configuration
        model = genai.GenerativeModel('gemini-pro')
        print("Gemini API configured successfully!")
    except Exception as e:
        print(f"Error configuring Gemini API: {e}")
        GEMINI_AVAILABLE = False
else:
    print("Warning: google.generativeai package not available. Falling back to default analysis.")

async def analyze_credibility(text: str) -> dict:
    """
    Analyze text credibility using Google's Gemini API
    """
    if not GEMINI_AVAILABLE:
        print(f"Debug: GEMINI_AVAILABLE is False, API key: {settings.GEMINI_API_KEY[:5]}...")
        return {
            "verdict": "Unknown",
            "confidence": 0,
            "explanation": "Gemini API not available. Please check server logs.",
            "key_indicators": []
        }

    try:
        print("Initializing Gemini model...")
        # Initialize the model
        model = genai.GenerativeModel('gemini-pro')
        
        # Craft the prompt for credibility analysis
        prompt = f"""
        Analyze the following text for credibility and provide a structured response:
        
        TEXT TO ANALYZE:
        {text}
        
        Provide your analysis in the following JSON format:
        {{
            "verdict": "Real" or "Fake",
            "confidence": (number between 0-100),
            "explanation": "detailed explanation of the verdict",
            "key_indicators": ["list of key credibility indicators found"]
        }}
        
        Base your analysis on:
        - Factual accuracy
        - Source credibility
        - Language patterns
        - Sensationalism
        - Logical consistency
        """
        
        # Generate response
        response = await model.generate_content(prompt)
        
        # Parse the response to extract the JSON
        # The response might be in a code block, so we'll clean it up
        response_text = response.text.strip()
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0]
        elif "```" in response_text:
            response_text = response_text.split("```")[1]
            
        analysis_result = json.loads(response_text.strip())
        
        # Ensure we have all required fields
        return {
            "verdict": analysis_result.get("verdict", "Unknown"),
            "confidence": int(analysis_result.get("confidence", 0)),
            "explanation": analysis_result.get("explanation", "Analysis incomplete"),
            "key_indicators": analysis_result.get("key_indicators", [])
        }
        
    except Exception as e:
        print(f"Gemini API Error: {str(e)}")
        return {
            "verdict": "Unknown",
            "confidence": 0,
            "explanation": "Error during analysis",
            "key_indicators": []
        }