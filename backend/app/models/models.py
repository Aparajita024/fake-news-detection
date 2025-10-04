from pydantic import BaseModel, Field, HttpUrl
from typing import List, Dict, Any, Optional, Union

# --- Models for External Sources ---

class SocialMediaPost(BaseModel):
    """Defines the structure for a post/tweet from social media."""
    source: str = Field(description="The social media platform (e.g., 'X (Twitter)', 'Reddit').")
    text: str = Field(description="The content of the post.")
    engagement_score: int = Field(description="A numerical score representing the post's popularity or interaction.")
    user: str = Field(description="The username or ID of the post's author.")
    url: Optional[HttpUrl] = Field(None, description="URL to the original post.")

class FactCheckData(BaseModel):
    """Specific model for government/official fact-check data."""
    claim_reviewed: str
    publisher: str
    truth_rating: str
    explanation: str
    url: Optional[HttpUrl] = Field(None, description="URL to the official fact-check.")

class SourceResult(BaseModel):
    """Defines the structured output for a single external source."""
    source_name: str = Field(description="The name of the external API source (e.g., 'X (Twitter)', 'Gov Fact Check').")
    status: str = Field(description="The status of the operation for this source (e.g., 'SUCCESS', 'ERROR').")
    data: List[Union[SocialMediaPost, FactCheckData, Dict[str, Any]]] = Field(
        description="A list of data items retrieved from the source."
    )
    error_message: Optional[str] = Field(None, description="Detailed error message if status is 'ERROR'.")

# --- Models for Core Analysis ---

class AnalysisVerdict(BaseModel):
    """Model for the final verdict from our internal ML model."""
    verdict: str = Field(description="The final verdict: 'Fake', 'Real', or 'Uncertain'.")
    confidence: int = Field(ge=0, le=100, description="Confidence score from 0 to 100.")
    explanation: str = Field(description="Short explanation of the reasoning.")
    highlighted: List[str] = Field(description="List of suspicious keywords/phrases.")

class FinalAnalysisResponse(BaseModel):
    """Defines the final, aggregated response structure for the API."""
    analysis: AnalysisVerdict = Field(description="The core verdict from our ML model.")
    related_sources: List[SourceResult] = Field(description="Results from external sources supporting or contradicting the claim.")
    extracted_text: str = Field(description="The primary text used for backend analysis (from body, URL, or OCR).")

# --- Models for Request Inputs ---

class TextIn(BaseModel):
    text: str

class UrlIn(BaseModel):
    url: HttpUrl

class FeedbackIn(BaseModel):
    rating: int = Field(..., ge=1, le=5)

class FeedbackOut(BaseModel):
    id: str = Field(..., alias="_id")
    rating: int

    class Config:
        populate_by_name = True
        json_encoders = {
            # Convert MongoDB's ObjectId to a string
            'id': lambda v: str(v)
        }

try:
    import pytesseract
except ModuleNotFoundError:
    pytesseract = None
    # later, when you attempt OCR, check and raise a helpful error if None

class VerificationQueryIn(BaseModel):
    """Input model for a query to be verified against official PDFs."""
    query: str = Field(..., min_length=10, description="The claim or question to verify.")

class VerificationResponseOut(BaseModel):
    """Output model for the PDF verification result."""
    query: str
    verified: Union[bool, str] # Can be true, false, or "unknown"
    source: Optional[str] = None
    page: Optional[int] = None
    excerpt: Optional[str] = None
    summary: str
    suggested_sources: List[str] = []