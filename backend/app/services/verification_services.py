import httpx
import fitz  # PyMuPDF
import re
from typing import Dict, Any, List, Optional
from ..models.models import VerificationResponseOut

# --- MOCKED OFFICIAL PDF SOURCES ---
# In a real-world application, this would be the result of a sophisticated web crawler
# that searches official domains like pib.gov.in for PDFs related to the query.
MOCKED_PDF_DATABASE = [
    {
        "title": "PIB Fact Check on Fake News Schemes",
        "url": "https://pib.gov.in/FactCheck/guide_english.pdf",
        "keywords": ["scheme", "free", "laptop", "government", "fake"]
    },
    {
        "title": "WHO Q&A on COVID-19 and related topics",
        "url": "https://www.who.int/emergencies/diseases/novel-coronavirus-2019/question-and-answers-hub/q-a-detail/coronavirus-disease-(covid-19)",
        "keywords": ["covid", "vaccine", "mask", "virus"] # Note: This is an HTML page, we'll treat it as a fallback
    }
]

SUGGESTED_SOURCES_FALLBACK = [
    "https://pib.gov.in/factcheck.aspx",
    "https://www.india.gov.in/my-government/schemes",
    "https://www.who.int/emergencies/diseases/novel-coronavirus-2019/advice-for-public"
]

async def download_and_parse_pdf(url: str) -> Dict[int, str]:
    """Downloads a PDF from a URL and returns its text content, page by page."""
    pdf_pages = {}
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, follow_redirects=True, timeout=20.0)
            response.raise_for_status()
        
        # Open the PDF from the downloaded bytes
        pdf_document = fitz.open(stream=response.content, filetype="pdf")
        
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            pdf_pages[page_num + 1] = page.get_text("text") # Page numbers are 1-indexed
            
        pdf_document.close()
        return pdf_pages
    except Exception as e:
        print(f"Failed to download or parse PDF from {url}: {e}")
        return {}


def find_relevant_excerpt(page_text: str, keywords: List[str]) -> Optional[str]:
    """Finds a sentence containing the most keywords."""
    sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', page_text)
    best_sentence = None
    max_matches = 0

    for sentence in sentences:
        matches = sum(1 for keyword in keywords if keyword in sentence.lower())
        if matches > max_matches:
            max_matches = matches
            best_sentence = sentence.strip()
            
    # Require at least 2 keyword matches for a relevant excerpt
    return best_sentence if max_matches >= 2 else None


async def verify_query_against_pdfs(query: str) -> VerificationResponseOut:
    """
    Main service function to orchestrate the PDF verification process.
    """
    query_keywords = [word for word in query.lower().split() if len(word) > 3]

    # 1. Find potentially relevant PDFs (simulated)
    relevant_pdfs = [
        pdf for pdf in MOCKED_PDF_DATABASE 
        if any(kw in query.lower() for kw in pdf["keywords"])
    ]

    # 2. Iterate through relevant PDFs and search for the claim
    for pdf_info in relevant_pdfs:
        if not pdf_info["url"].endswith(".pdf"):
            continue # Skip non-PDF sources for direct parsing

        print(f"Analyzing PDF: {pdf_info['title']}")
        pdf_content = await download_and_parse_pdf(pdf_info["url"])

        for page_num, page_text in pdf_content.items():
            excerpt = find_relevant_excerpt(page_text, query_keywords)
            if excerpt:
                # --- VERIFICATION FOUND ---
                summary = f"Information related to the query was found in an official document. The claim appears to be addressed on page {page_num}."
                # A more advanced version would analyze the sentiment of the excerpt to determine true/false
                return VerificationResponseOut(
                    query=query,
                    verified="unknown", # Setting to "unknown" as sentiment analysis isn't implemented
                    source=pdf_info["title"],
                    page=page_num,
                    excerpt=excerpt,
                    summary=summary
                )

    # --- 3. FALLBACK STRATEGY ---
    # If no information is found in any of the PDFs
    print("Could not verify claim in available PDFs. Providing fallback sources.")
    return VerificationResponseOut(
        query=query,
        verified="unknown",
        summary="The query could not be verified using the available official PDF documents. It is recommended to check the following official sources directly.",
        suggested_sources=SUGGESTED_SOURCES_FALLBACK
    )