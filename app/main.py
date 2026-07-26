"""FastAPI web backend. Run with: uvicorn app.main:app --reload"""

import json
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app.services.AIrecommender import recommend_from_scraped_pages
from app.services.catalog import search_catalog_markdown
from app.services.scraper import search_and_scrape_store_products


# Important: this must be __file__, with two underscores on both sides.
ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT.parent / ".env")

app = FastAPI(title="StyleScout API", version="0.2.0")
app.mount("/static", StaticFiles(directory=ROOT / "static"), name="static")


class SearchRequest(BaseModel):
    query: str = Field(min_length=2, max_length=200)
    size: str | None = Field(default=None, max_length=20)
    budget: int | None = Field(default=None, ge=100, le=1_000_000)


@app.get("/")
def home() -> FileResponse:
    return FileResponse(ROOT / "static" / "index.html")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/search")
def search(request: SearchRequest) -> dict[str, object]:
    # Search query sent to Firecrawl.
    search_query = request.query

    if request.size:
        search_query += f", size {request.size}"

    if request.budget:
        search_query += f", under Rs {request.budget}"

    try:
        # 1. Firecrawl Search: query -> result URLs
        scraped_pages=search_and_scrape_store_products(
            query=search_query,
            per_store_limit=3,
        )

        if not scraped_pages:
            return {
                "query": request.query,
                "answer": "I found product links, but could not retrieve their product details.",
                "sources": [],
            }

        # 3. Groq: scraped markdown -> natural-language comparison
        answer = recommend_from_scraped_pages(
            scraped_pages=scraped_pages,
            query=request.query,
            size=request.size,
            budget=request.budget,
        )

        # Do not send complete markdown pages to the frontend.
        sources = [
            {
                "title": page["title"],
                "url": page["url"],
            }
            for page in scraped_pages
        ]

        return {
            "query": request.query,
            "answer": answer,
            "sources": sources,
        }

    except json.JSONDecodeError as error:
        raise HTTPException(
            status_code=502,
            detail="Firecrawl returned an invalid search response.",
        ) from error

    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error)) from error