import asyncio
try:
    import pytesseract
except Exception:
    pytesseract = None
from PIL import Image
import io
# import speech_recognition as sr
from ..core.ml_model import predict
from ..utils.helpers import fetch_article_text_from_url
from .external_apis import x_service, reddit_service
import whisper


async def _get_combined_analysis(text: str):
    """
    Internal function to run ML prediction and external API calls concurrently.
    """
    # Task 1: Get the core verdict from our internal ML model.
    ml_verdict_task = asyncio.to_thread(predict, text)

    # Tasks 2 & 3: Concurrently fetch data from external social media sources.
    tasks = [
        ml_verdict_task,
        x_service.search_posts(text),
        reddit_service.search_posts(text),
    ]

    # Await all tasks to complete.
    results = await asyncio.gather(*tasks)

    # Unpack results
    ml_verdict = results[0]
    external_sources = results[1:]

    return {
        "analysis": ml_verdict,
        "related_sources": external_sources,
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

try:
    print("Loading Whisper model...")
    whisper_model = whisper.load_model("base") 
    print("Whisper model loaded successfully.")
except Exception as e:
    print(f"Could not load Whisper model: {e}")
    whisper_model = None

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