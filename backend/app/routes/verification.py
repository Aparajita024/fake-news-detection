from fastapi import APIRouter, HTTPException
from ..models.models import VerificationQueryIn, VerificationResponseOut
from ..services.verification_services import verify_query_against_pdfs

router = APIRouter()

@router.post(
    "/api/v1/verify-claim-pdf",
    response_model=VerificationResponseOut,
    summary="Verify a claim against official PDF documents",
    tags=["Verification"] # Group this endpoint separately in the docs
)
async def verify_claim_endpoint(request: VerificationQueryIn):
    """
    Accepts a user query (a claim or question) and attempts to verify it 
    by searching through a curated list of official government and organization PDFs.

    - The service simulates finding relevant PDFs based on keywords.
    - It then downloads, parses, and performs a full-text search on the documents.
    - If a relevant passage is found, it's returned with a source and page number.
    - If nothing is found, it provides a list of suggested official websites.
    """
    try:
        result = await verify_query_against_pdfs(request.query)
        return result
    except Exception as e:
        # This catches any unexpected errors during the process
        print(f"An unexpected error occurred in the verification endpoint: {e}")
        raise HTTPException(status_code=500, detail="An internal error occurred during the verification process.")