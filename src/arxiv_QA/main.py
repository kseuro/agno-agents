import os
import json
from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools.arxiv import ArxivTools
from agno.media import File
from dotenv import dotenv_values
from typing import List, Any

from response_models import ArxivSearchResponse, ArticleSummary


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


def summarize_pdf(pdf_url: str) -> ArticleSummary | Any | None:
    if not pdf_url.startswith("https"):
        pdf_url = pdf_url.replace("http", "https")

    agent = Agent(
        name="pdf_summarizer",
        model=Gemini(id=MODEL_ID, api_key=GEMINI_API_KEY),
        retries=2,
        delay_between_retries=2,
        exponential_backoff=True,
        role="You are a scientist with extensive peer review experience.",
        instructions=[
            "Return a concise summary and bullet points of key contributions.",
            "If any limitations or assumptions are clear, include them.",
        ],
        response_model=ArticleSummary,
    )
    prompt = "Read the contents of the attached arXiv paper."
    response = agent.run(message=prompt, files=[File(url=pdf_url)])
    return response.content


def main():
    query = "machine learning antibody design"
    search_result = search_arxiv(query=query)
    print(f"Found {search_result.total_found} articles related to `{search_result.query}`")
    print("PDF Titles and URLs:")
    titles = [item.title for item in search_result.items]
    for title, url in zip(titles, search_result.pdf_urls):
        print(f"- {title} -- {url}")

    first_pdf = next((u for u in search_result.pdf_urls if u), None)
    if first_pdf:
        print("\nSummarizing first PDF...")
        summary = summarize_pdf(first_pdf)
        if summary:
            print("Title:", summary.title)
            print("Summary:", summary.summary)
            if summary.key_points:
                print("Key points:")
                for kp in summary.key_points:
                    print(f"- {kp}")
            else:
                print("No key points extracted.")
            if summary.limitations:
                print("Limitations:")
                for lim in summary.limitations:
                    print(f"- {lim}")
            else:
                print("No limitations listed or inferred.")


if __name__ == "__main__":
    main()
