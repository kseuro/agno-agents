import os
import json
from typing import List
from agno.tools.arxiv import ArxivTools
from dotenv import dotenv_values
from response_models import ArxivSearchResponse


environment_config = dotenv_values(".env")

GEMINI_API_KEY = environment_config.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY"))
if not GEMINI_API_KEY:
    raise ValueError("Set the `GEMINI_API_KEY`")
MODEL_ID: str = "gemini-2.0-flash-lite"
FALLBACK_MODELS: List[str] = ["gemini-2.0-flash"]


def search_arxiv(query: str, num_articles: int = 5) -> ArxivSearchResponse:
    raw = ArxivTools().search_arxiv_and_return_articles(query=query, num_articles=num_articles)
    items = json.loads(raw)
    result = ArxivSearchResponse.from_agno_items(query=query, items=items)
    return result


def main():
    query = "machine learning antibody design"
    search_result = search_arxiv(query=query)
    print(f"Found {search_result.total_found} articles related to `{search_result.query}`")
    print("PDF URLs:")
    for url in search_result.pdf_urls:
        print(f"- {url}")


if __name__ == "__main__":
    main()
