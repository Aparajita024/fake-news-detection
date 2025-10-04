import os
import asyncio
import httpx
from typing import Dict, Any, Optional, List
from ..models.models import SourceResult, SocialMediaPost, FactCheckData, HttpUrl

# --- API Key Configuration ---
class ApiKeys:
    X_BEARER_TOKEN: str = os.getenv("X_BEARER_TOKEN", "X_BEARER_TOKEN_PLACEHOLDER")
    # Add other keys as needed

KEYS = ApiKeys()

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
            # --- MOCKING LOGIC ---
            # In a real app, you'd remove the sleep and uncomment the httpx call.
            await asyncio.sleep(0.5) # Simulate network latency
            if self.api_name == "X (Twitter)":
                mock_data = [
                    SocialMediaPost(source="X (Twitter)", text="This is a mock tweet about the topic.", engagement_score=150, user="User_A", url=HttpUrl("https://x.com/example/1")),
                ]
                return SourceResult(source_name=self.api_name, status="SUCCESS", data=[p.model_dump() for p in mock_data])
            elif self.api_name == "Reddit":
                 mock_data = [
                    SocialMediaPost(source="Reddit", text="Mock Reddit discussion thread.", engagement_score=42, user="Redditor_1", url=HttpUrl("https://reddit.com/r/news/1")),
                ]
                 return SourceResult(source_name=self.api_name, status="SUCCESS", data=[p.model_dump() for p in mock_data])
            
            # --- REAL API CALL LOGIC (uncomment for production) ---
            # url = f"{self.base_url}{endpoint}"
            # response = await self.client.get(url, params=params, headers=headers)
            # response.raise_for_status()
            # parsed_data = self._parse_response(response.json())
            # return SourceResult(source_name=self.api_name, status="SUCCESS", data=parsed_data)

        except httpx.RequestError as e:
            error_msg = f"Network error connecting to {self.api_name}: {e}"
            print(f"❌ {error_msg}")
            return SourceResult(source_name=self.api_name, status="ERROR", data=[], error_message=error_msg)
        except httpx.HTTPStatusError as e:
            error_msg = f"API error from {self.api_name}: {e.response.status_code}"
            print(f"❌ {error_msg}")
            return SourceResult(source_name=self.api_name, status="ERROR", data=[], error_message=error_msg)
        except Exception as e:
            error_msg = f"An unexpected error occurred with {self.api_name}: {e}"
            print(f"❌ {error_msg}")
            return SourceResult(source_name=self.api_name, status="ERROR", data=[], error_message=error_msg)

    def _parse_response(self, response_json: Dict) -> List[Dict]:
        """Placeholder for transforming raw API responses into our Pydantic models."""
        # This is where you would map the API's fields to your model's fields.
        raise NotImplementedError("Each service must implement its own response parser.")

# --- Specific Service Implementations ---
class XService(ExternalAPIService):
    def __init__(self):
        super().__init__("X (Twitter)", "https://api.x.com/2/")
        self.headers = {"Authorization": f"Bearer {KEYS.X_BEARER_TOKEN}"}

    async def search_posts(self, query: str) -> SourceResult:
        endpoint = "tweets/search/recent"
        params = {"query": query, "max_results": 5}
        return await self._make_request(endpoint, params=params, headers=self.headers)

class RedditService(ExternalAPIService):
    def __init__(self):
        super().__init__("Reddit", "https://oauth.reddit.com/")
        # Reddit API typically uses OAuth2, which is more complex.
        # For this example, we assume a simple API key or public endpoint.
    
    async def search_posts(self, query: str) -> SourceResult:
        endpoint = "r/all/search"
        params = {"q": query, "sort": "relevance", "limit": 3}
        return await self._make_request(endpoint, params=params)

# Instantiate singleton services for use across the app
x_service = XService()
reddit_service = RedditService()