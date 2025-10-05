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

# Whisper import
try:
    import whisper
    WHISPER_AVAILABLE = True
except Exception as e:
    print(f"Whisper import error: {e}")
    whisper = None
    WHISPER_AVAILABLE = False

# Initialize whisper model globally
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


async def _get_combined_analysis(text: str):
    """
    Full analysis pipeline:
    - Run ML model for initial verdict
    - Fallback to Gemini AI if ML is low confidence / uncertain
    - Aggregate social media results
    """
    try:
        print(f"Starting analysis for text: {text[:100]}...")

        ml_result = None
        final_verdict = None
        gemini_needed = True

        # Step 1: Run ML model
        try:
            ml_result = predict(text)
            print(f"ML Model verdict: {ml_result.get('verdict')} | confidence: {ml_result.get('confidence')}%")
            # Use ML only if confident
            is_short_text = len(text.split()) < 20 
            if is_short_text:
                print("Text is too short. Forcing Gemini AI analysis for higher accuracy.")
                gemini_needed = True
            # Only rely on the ML model if it's highly confident AND the text is long enough
            elif ml_result.get("confidence", 0) >= 80 and ml_result.get("verdict") != "Uncertain":
                gemini_needed = False
            if ml_result.get("confidence", 0) >= 80 and ml_result.get("verdict") != "Uncertain":
                gemini_needed = False
        except Exception as e:
            print(f"ML prediction failed: {e}")

        # Step 2: Prepare external tasks (social media + Gemini)
        tasks = []
        try:
            tasks.append(analyze_credibility(text))  # Gemini fallback
            tasks.extend([
                x_service.search_posts(text),
                reddit_service.search_posts(text)
            ])
        except Exception as e:
            print(f"Error preparing external API tasks: {e}")

        # Step 3: Run all tasks concurrently
        external_results = []
        if tasks:
            try:
                results = await asyncio.gather(*tasks, return_exceptions=True)
                external_results = [r for r in results if not isinstance(r, Exception)]
            except Exception as e:
                print(f"Error running external API tasks: {e}")

        # Step 4: Process results safely
        social_results = []
        gemini_result = {}

         # Gemini result is always the first task
        if external_results and "verdict" in external_results[0]:
            gemini_result = external_results[0]
            # Set gemini_needed to True if we have a valid result from Gemini
            gemini_needed = True 
        else:
            # Gemini failed or returned an error, so we cannot use it.
            gemini_needed = False
            print("Gemini analysis failed or returned no verdict. Falling back to ML model if available.")

        social_results = external_results[1:] if len(external_results) > 1 else []

        # --- Step 5: Decide final verdict (REVISED LOGIC) ---
        # Prioritize a valid Gemini result.
        if gemini_needed and gemini_result.get("verdict") != "Unknown":
            final_verdict = {
                "verdict": gemini_result.get("verdict"),
                "confidence": gemini_result.get("confidence", 0),
                "explanation": gemini_result.get("explanation", "No explanation available"),
                "highlighted": gemini_result.get("highlighted", []),
                "key_indicators": gemini_result.get("key_indicators", []),
                "source": "Gemini AI"
            }
        # Fallback to the ML Model result if Gemini was not needed or failed.
        elif ml_result:
            final_verdict = {
                **ml_result,
                "highlighted": ml_result.get("highlighted", []),
                "key_indicators": ml_result.get("key_indicators", []),
                "source": "ML Model"
            }
        # Final fallback if everything fails.
        else:
            final_verdict = {
                "verdict": "Error", "confidence": 0,
                "explanation": "Both ML and AI analysis failed.",
                "source": "Error"
            }

        print(f"Final verdict: {final_verdict['verdict']} | source: {final_verdict['source']}")

        # Step 6: Return structured response
        return {
            "analysis": final_verdict,
            "related_sources": social_results or [],
            "extracted_text": text
        }

    except Exception as e:
        print(f"Analysis pipeline error: {e}")
        return {
            "analysis": {
                "verdict": "Error",
                "confidence": 0,
                "explanation": f"Analysis failed: {e}",
                "highlighted": [],
                "key_indicators": [],
                "source": "Error"
            },
            "related_sources": [],
            "extracted_text": text
        }


# --- Service Wrappers ---
async def analyze_text_service(text: str):
    return await _get_combined_analysis(text)


async def analyze_url_service(url: str):
    article_text = fetch_article_text_from_url(url)
    if not article_text:
        return None
    return await _get_combined_analysis(article_text)


async def analyze_image_service(image_bytes: bytes):
    if pytesseract is None:
        return None
    try:
        image = Image.open(io.BytesIO(image_bytes))
        text = await asyncio.to_thread(pytesseract.image_to_string, image)
        if not text.strip():
            return None
        return await _get_combined_analysis(text.strip())
    except Exception as e:
        print(f"OCR processing error: {e}")
        return None


async def analyze_voice_service(voice_file_path: str):
    if whisper_model is None:
        return {"error": "Whisper model is not available."}
    try:
        result = await asyncio.to_thread(whisper_model.transcribe, voice_file_path)
        text = result.get("text", "")
        if not text.strip():
            return {"error": "Could not understand the audio."}
        return await _get_combined_analysis(text)
    except Exception as e:
        return {"error": f"Voice transcription failed: {e}"}
