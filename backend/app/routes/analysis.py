from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from ..models.models import TextIn, UrlIn, FinalAnalysisResponse
from ..services.analysis_service import (
    analyze_text_service,
    analyze_url_service,
    analyze_image_service,
    analyze_voice_service,
)

router = APIRouter()

@router.post("/analysis", response_model=FinalAnalysisResponse)
async def analyze_text(request: TextIn):
    """Analyze a raw block of text."""
    try:
        if not request.text or not request.text.strip():
            raise HTTPException(status_code=400, detail="Text cannot be empty")
            
        print(f"Analyzing text: {request.text[:100]}...")
        result = await analyze_text_service(request.text)
        
        if not result:
            raise HTTPException(status_code=500, detail="Analysis failed - no result returned")
            
        print(f"Analysis complete. Verdict: {result.get('analysis', {}).get('verdict')}")
        return {
            "analysis": result.get("analysis", {
                "verdict": "Unknown",
                "confidence": 0,
                "explanation": "Analysis failed to return a valid result"
            }),
            "related_sources": result.get("related_sources", []),
            "extracted_text": result.get("extracted_text", request.text)
        }
        
    except Exception as e:
        print(f"Error in analyze_text: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

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