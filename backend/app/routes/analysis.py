from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from ..models.models import TextIn, UrlIn, FinalAnalysisResponse
from ..services.analysis_service import (
    analyze_text_service,
    analyze_url_service,
    analyze_image_service,
    analyze_voice_service,
)

router = APIRouter()

@router.post("/analyze-text", response_model=FinalAnalysisResponse)
async def analyze_text(request: TextIn):
    """Analyze a raw block of text."""
    result = await analyze_text_service(request.text)
    if not result:
        raise HTTPException(status_code=500, detail="Analysis failed.")
    return result

@router.post("/analyze-url", response_model=FinalAnalysisResponse)
async def analyze_url(request: UrlIn):
    """Scrape and analyze an article from a URL."""
    result = await analyze_url_service(str(request.url))
    if not result:
        raise HTTPException(status_code=400, detail="Could not fetch or process the article from the URL.")
    return result

@router.post("/analyze-image", response_model=FinalAnalysisResponse)
async def analyze_image(file: UploadFile = File(...)):
    """Extract text from an image via OCR and analyze it."""
    contents = await file.read()
    result = await analyze_image_service(contents)
    if not result:
        raise HTTPException(status_code=400, detail="Could not extract readable text from the image.")
    return result

@router.post("/analyze-voice", response_model=FinalAnalysisResponse)
async def analyze_voice(file: UploadFile = File(...)):
    """Transcribe a voice file and analyze the text."""
    # Saving file temporarily to disk for SpeechRecognition library
    file_path = f"/tmp/{file.filename}"
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())
    
    result = await analyze_voice_service(file_path)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result