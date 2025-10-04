import requests
from bs4 import BeautifulSoup
import re
from typing import List
from pydantic import HttpUrl

def fetch_article_text_from_url(url: str) -> str:
    """Fetches and extracts the main text content from a news article URL."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        
        # A common heuristic: find all paragraphs and join their text
        paragraphs = soup.find_all("p")
        article_text = " ".join([p.get_text() for p in paragraphs])
        return article_text.strip()
    except requests.RequestException as e:
        print(f"Error fetching URL {url}: {e}")
        return ""

def extract_urls_from_text(text: str) -> List[HttpUrl]:
    """Extracts and validates URLs from a block of text."""
    url_pattern = re.compile(
        r'https?://(?:www\.)?(?:[\da-z\.-]+)\.(?:[a-z\.]{2,6})(?:/[^\s]*)?'
    )
    found_urls = url_pattern.findall(text)
    valid_urls = []
    for url in found_urls:
        try:
            valid_urls.append(HttpUrl(url))
        except Exception:
            pass # Ignore invalid URLs
    return valid_urls