import json
import os

import requests
from dotenv import load_dotenv

load_dotenv()

FIRECRAWL_SEARCH_URL = "https://api.firecrawl.dev/v2/search"


def search_catalog_markdown(query: str) -> str:
    api_key = os.getenv("FIRECRAWL_API_KEY")
    if not api_key:
        return "FIRECRAWL_API_KEY is missing from .env"

    payload = {
        "query": f"{query} from Amazon India, Flipkart, and Snitch",
        "sources": ["web"],
        "limit": 20,
        "scrapeOptions": {
            "onlyMainContent": True,
            "maxAge": 172800000,
            "formats": [],
        },
    }

    try:
        response = requests.post(
            FIRECRAWL_SEARCH_URL,
            json=payload,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            timeout=45,
        )
        response.raise_for_status()
        return json.dumps(response.json(), indent=2, ensure_ascii=False)

    except requests.RequestException as error:
        return f"Firecrawl Search failed: {error}"