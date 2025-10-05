import asyncio
import httpx
from typing import Dict, Any, Optional, List
from ..models.models import SourceResult, SocialMediaPost, FactCheckData, HttpUrl
from ..core.config.settings import settings # <-- Import the central settings object

# --- Base Service ---
class ExternalAPIService:
    """Base class for API services to handle common logic like async requests."""
    def __init__(self, api_name: str, base_url: str):
        self.api_name = api_name
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=10.0)

    async def _make_request(self, endpoint: str, params: Optional[Dict] = None, headers: Optional[Dict] = None) -> SourceResult:
        """Makes an async HTTP request and handles errors, returning a SourceResult."""
        try:
            # MOCKING LOGIC FOR DEVELOPMENT (can be removed later)
            # await asyncio.sleep(0.5)
            # if self.api_name == "X (Twitter)":
            #     mock_data = [
            #         SocialMediaPost(source="X (Twitter)", text="This is a mock tweet about the topic.", engagement_score=150, user="User_A", url=HttpUrl("https://x.com/example/1")),
            #     ]
            #     return SourceResult(source_name=self.api_name, status="SUCCESS", data=[p.model_dump() for p in mock_data])
            # elif self.api_name == "Reddit":
            #      mock_data = [
            #         SocialMediaPost(source="Reddit", text="Mock Reddit discussion thread.", engagement_score=42, user="Redditor_1", url=HttpUrl("https://reddit.com/r/news/1")),
            #     ]
            #      return SourceResult(source_name=self.api_name, status="SUCCESS", data=[p.model_dump() for p in mock_data])
            url = f"{self.base_url}{endpoint}"
            print(f"Making request to {self.api_name}: {url} with params {params}")
            
            response = await self.client.get(url, params=params, headers=headers)
            response.raise_for_status()
            
            api_data = response.json()

            import json
            print("="*50)
            print(f"RAW API RESPONSE FROM: {self.api_name}")
            # Use json.dumps for pretty-printing the JSON in your terminal
            print(json.dumps(api_data, indent=2))
            print("="*50)

            return SourceResult(
                source_name=self.api_name,
                status="SUCCESS",
                data=api_data,
                error_message=None,
            )

        except Exception as e:
            error_msg = f"An unexpected error occurred with {self.api_name}: {e}"
            print(f"{error_msg}")
            return SourceResult(source_name=self.api_name, status="ERROR", data=[], error_message=error_msg)

# --- Specific Service Implementations ---
class XService(ExternalAPIService):
    def __init__(self):
        super().__init__("X (Twitter)", "https://api.x.com/2/")
        # Securely get the bearer token from our central settings object
        self.headers = {"Authorization": f"Bearer {settings.X_BEARER_TOKEN}"}

    async def search_posts(self, query: str) -> SourceResult:
        endpoint = "tweets/search/recent"
        params = {"query": query, "max_results": 5}
        return await self._make_request(endpoint, params=params, headers=self.headers)

class RedditService(ExternalAPIService):
    def __init__(self):
        super().__init__("Reddit", "https://oauth.reddit.com/")
        self.headers = {
            "Authorization": f"bearer {getattr(settings, 'REDDIT_TOKEN', '')}",
            "User-Agent": "FakeNewsDetector/0.1"
        }
    
    async def search_posts(self, query: str) -> SourceResult:
        endpoint = "r/all/search"
        params = {"q": query, "sort": "relevance", "limit": 3}
        return await self._make_request(endpoint, params=params)

# Instantiate singleton services for use across the app
x_service = XService()
reddit_service = RedditService()