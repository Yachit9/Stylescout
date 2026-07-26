# StyleScout: from MCP tool to web app

## What you now have

`server.py` is still your Claude Desktop MCP server. `app/main.py` is a browser-facing FastAPI application. They both call `app/services/catalog.py`; this prevents duplicated scraping logic.

## Setup

1. Revoke the Firecrawl API key that was previously inside `server.py` and create a replacement.
2. Copy `.env.example` to `.env`, then add the replacement key.
3. Activate your virtual environment: `venv\Scripts\Activate.ps1`.
4. Install web dependencies: `python -m pip install -r requirements.txt`.
5. Start the web app: `python -m uvicorn app.main:app --reload`.
6. Open `http://127.0.0.1:8000`.

To use the MCP server in Claude Desktop, keep its command pointing at `venv\Scripts\python.exe` and pass `server.py` as the argument. Do not put the key in the Claude Desktop configuration; the server reads it from `.env` when configured to do so.

## How to think about the layers

| Layer | Responsibility |
| --- | --- |
| MCP (`server.py`) | Lets Claude Desktop call your shopping capability. |
| Service (`catalog.py`) | Fetches data from approved stores. This is reusable business logic. |
| API (`main.py`) | Validates browser requests and exposes safe endpoints. |
| UI (`static/`) | Collects preferences and presents results. |

## Build the real recommendation engine next

Do not ask an LLM to rank raw scraped markdown directly. First transform every listing into a shared `Product` schema: title, brand, price, currency, URL, image, material, rating, review count, sizes, availability, delivery, return policy, and source.

Then use code to enforce hard constraints (in stock, size L, <= Rs 2300), deduplicate products, and compute a score. A good initial score is: value 30%, quality signals 30%, style match 25%, size confidence 10%, seller/returns 5%. Use AI afterwards only to explain the top 3-5 choices in natural language.

## Add stores safely

Each merchant needs an official API, affiliate feed, or a confirmed permitted product-page/search route. Add a `Store` configuration only after testing its search URL and checking its terms. Cache results and save a `checked_at` time because price and stock are volatile.

## Production milestones

1. Replace raw markdown with structured product extraction and persistence in PostgreSQL.
2. Add a background worker for refreshes, retries, and rate limiting.
3. Add user accounts, favourites, price alerts, and location-aware delivery.
4. Deploy the UI/API, worker, database, and secrets separately. Use environment variables managed by the host, not `.env` in production.
5. Add observability, error handling, consent/privacy policy, and affiliate disclosure.
