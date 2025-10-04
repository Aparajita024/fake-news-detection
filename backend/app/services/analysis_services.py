import asyncio
import pytesseract
from PIL import Image
import io
import speech_recognition as sr
from ..core.ml_model import predict
from ..utils.helpers import fetch_article_text_from_url
from .external_apis import x_service, reddit_service

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
    """Performs OCR on an image and analyzes the extracted text."""
    try:
        image = Image.open(io.BytesIO(image_bytes))
        text = await asyncio.to_thread(pytesseract.image_to_string, image)
        if not text:
            return None
        return await _get_combined_analysis(text.strip())
    except Exception as e:
        print(f"Error during OCR processing: {e}")
        return None

async def analyze_voice_service(voice_file_path: str):
    """Converts a voice file to text and analyzes it."""
    recognizer = sr.Recognizer()
    with sr.AudioFile(voice_file_path) as source:
        audio_data = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio_data)
            return await _get_combined_analysis(text)
        except sr.UnknownValueError:
            return {"error": "Google Speech Recognition could not understand the audio."}
        except sr.RequestError as e:
            return {"error": f"Could not request results from Google Speech Recognition service; {e}"}