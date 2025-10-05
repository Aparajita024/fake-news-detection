import asyncio
try:
    import pytesseract
except Exception:
    pytesseract = None
from PIL import Image
import io
from ..utils.helpers import fetch_article_text_from_url
from .external_apis import x_service, reddit_service
from .gemini_service import analyze_credibility
from ..core.ml_model import predict

# Import whisper with error handling
try:
    import whisper
    WHISPER_AVAILABLE = True
except Exception as e:
    print(f"Whisper import error: {e}")
    whisper = None
    WHISPER_AVAILABLE = False


async def _get_combined_analysis(text: str):
    """
    Internal function to run ML prediction with Gemini fallback and external API calls concurrently.
    """
    try:
        print("Starting analysis...")
        # First try the ML model
        try:
            ml_result = predict(text)
            print(f"ML Model result: {ml_result.get('verdict')} with confidence {ml_result.get('confidence')}%")
        except Exception as e:
            print(f"ML model error: {str(e)}")
            ml_result = {
                "verdict": "Uncertain",
                "confidence": 0,
                "explanation": f"ML model error: {str(e)}",
                "highlighted": []
            }
        
        # Determine if we need to use Gemini as fallback
        needs_gemini = (
            ml_result.get("confidence", 0) < 50 or  # Low confidence
            ml_result.get("verdict") == "Uncertain" or  # Uncertain verdict
            "error" in ml_result.get("explanation", "").lower()  # Error in analysis
        )

        print(f"Needs Gemini fallback: {needs_gemini}")

        # Tasks to run concurrently
        tasks = []
        
        # Add Gemini analysis if needed
        if needs_gemini:
            print("ML model uncertain, falling back to Gemini analysis...")
            tasks.append(analyze_credibility(text))
        
        # Add social media tasks
        try:
            tasks.extend([x_service.search_posts(text), reddit_service.search_posts(text)])
        except Exception as e:
            print(f"Error setting up social media tasks: {str(e)}")
        
        # Run external API calls concurrently
        external_results = []
        if tasks:
            try:
                results = await asyncio.gather(*tasks, return_exceptions=True)
                external_results = [r for r in results if not isinstance(r, Exception)]
            except Exception as e:
                print(f"Error in external API calls: {str(e)}")
        
        # Process results
        if needs_gemini and external_results:
            social_results = external_results[:-1] if len(external_results) > 1 else []
            gemini_result = external_results[-1] if external_results else {}
            
            # Combine ML and Gemini results
            final_verdict = {
                "verdict": gemini_result.get("verdict", ml_result.get("verdict", "Uncertain")),
                "confidence": gemini_result.get("confidence", ml_result.get("confidence", 0)),
                "explanation": gemini_result.get("explanation", ml_result.get("explanation", "")),
                "highlighted": ml_result.get("highlighted", []),
                "key_indicators": gemini_result.get("key_indicators", []),
                "source": "Gemini AI (Fallback)"
            }
        else:
            social_results = external_results
            final_verdict = {
                **ml_result,
                "source": "ML Model"
            }

        print(f"Analysis complete. Final verdict: {final_verdict['verdict']}")
        
        return {
            "analysis": final_verdict,
            "related_sources": social_results or [],
            "extracted_text": text
        }
        
    except Exception as e:
        print(f"Error in analysis: {str(e)}")
        return {
            "analysis": {
                "verdict": "Error",
                "confidence": 0,
                "explanation": f"Error during analysis: {str(e)}",
                "highlighted": [],
                "source": "Error"
            },
            "related_sources": [],
            "extracted_text": text
        }

async def analyze_text_service(text: str):
    """Analyzes raw text."""
    return await _get_combined_analysis(text)

async def analyze_url_service(url: str):
    """Fetches text from a URL and analyzes it."""
    article_text = fetch_article_text_from_url(url)
    if not article_text:
        return None
    return await _get_combined_analysis(article_text)

async def analyze_image_service(image_bytes: bytes):
    """Performs OCR on an image and analyzes the extracted text.

    This function is tolerant: if pytesseract or the Tesseract binary
    isn't available it returns None so the route can raise an HTTP error
    with a helpful message.
    """
    if pytesseract is None:
        # OCR not available in this environment
        return None

    try:
        image = Image.open(io.BytesIO(image_bytes))
        # Run OCR off the event loop
        text = await asyncio.to_thread(pytesseract.image_to_string, image)
        if not text or not text.strip():
            return None
        return await _get_combined_analysis(text.strip())
    except Exception as e:
        # Keep errors quiet at service layer; route will convert to HTTP errors
        print(f"Error during OCR processing: {e}")
        return None

# Initialize whisper model
whisper_model = None
if WHISPER_AVAILABLE:
    try:
        print("Loading Whisper model...")
        whisper_model = whisper.load_model("base") 
        print("Whisper model loaded successfully.")
    except Exception as e:
        print(f"Could not load Whisper model: {e}")
else:
    print("Whisper is not available. Voice analysis will be disabled.")

async def analyze_voice_service(voice_file_path: str):
    """Transcribes a voice file using Whisper and analyzes the text."""
    if whisper_model is None:
        return {"error": "Whisper model is not available."}
    
    try:
        # Perform transcription. This is CPU/GPU intensive.
        # Use asyncio.to_thread to avoid blocking the main event loop.
        result = await asyncio.to_thread(whisper_model.transcribe, voice_file_path)
        text = result["text"]
        
        if not text:
             return {"error": "Could not understand the audio."}
        
        # Now, pass the high-quality text to our analysis function
        return await _get_combined_analysis(text)
    except Exception as e:
        return {"error": f"An error occurred during voice transcription: {e}"}