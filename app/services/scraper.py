import os
from urllib.parse import urlparse

import requests
from dotenv import load_dotenv
from firecrawl import Firecrawl
from firecrawl.v2.utils.error_handler import WebsiteNotSupportedError

from app.services.preprocessor import extract_product_evidence

load_dotenv()

FIRECRAWL_SEARCH_URL = "https://api.firecrawl.dev/v2/search"

STORES = {
    "Amazon": "amazon.in",
    "Flipkart": "flipkart.com",
    "Myntra": "myntra.com",
    "AJIO": "ajio.com",
    "Snitch": "snitch.com",
    "Red Tape": "redtape.com",
    "Allen Solly": "allensolly.com",
    "Arrow": "arrow1851.com",
    "Banana Club": "bananaclub.co.in",
    "H&M": "hm.com",
    "The Souled Store": "thesouledstore.com",
    "Fuaark": "fuaark.com",
    "5feet11": "5feet11.com",
}


def search_and_scrape_store_products(
    query: str,
    per_store_limit: int = 3,
    max_markdown_chars: int = 6000,
) -> list[dict]:
    """
    Search each configured retailer with Firecrawl Search, then scrape
    the resulting product/collection pages.
    """

    api_key = os.getenv("FIRECRAWL_API_KEY")
    if not api_key:
        raise RuntimeError("FIRECRAWL_API_KEY is missing from .env")

    firecrawl = Firecrawl(api_key=api_key)
    scraped_pages = []
    seen_urls = set()

    for store_name, domain in STORES.items():
        try:
            # Firecrawl Search finds results only from this retailer's domain.
            search_response = requests.post(
                FIRECRAWL_SEARCH_URL,
                json={
                    "query": f"{query} site:{domain}",
                    "sources": ["web"],
                    "limit": per_store_limit,
                    "scrapeOptions": {
                        "onlyMainContent": True,
                        "maxAge": 172800000,
                        "formats": [],
                    },
                },
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                timeout=45,
            )

            search_response.raise_for_status()

            results = search_response.json().get("data", {}).get("web", [])

        except requests.RequestException as error:
            print(f"Search failed for {store_name}: {error}")
            continue

        for item in results:
            url = item.get("url", "")
            hostname = urlparse(url).netloc.lower()

            # Reject irrelevant URLs returned by web search.
            if not url or domain not in hostname or url in seen_urls:
                continue

            seen_urls.add(url)

            try:
                response = firecrawl.scrape(
                    url,
                    formats=["markdown"],
                    only_main_content=True,
                )

                markdown = (
                    response.markdown
                    if hasattr(response, "markdown")
                    else ""
                )

                if markdown:
                    scraped_pages.append({
                        "store": store_name,
                        "url": url,
                        "title": item.get("title", ""),
                        "source_description": item.get("description", ""),
                        "evidence": extract_product_evidence(
                            markdown[:max_markdown_chars]
                        ),
                    })

            except WebsiteNotSupportedError:
                print(f"Website not supported: {url}")

            except Exception as error:
                print(f"Scrape failed for {url}: {error}")

    return scraped_pages