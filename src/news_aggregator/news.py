from newsapi import NewsApiClient
from typing import List, Dict


class NewsAPI:
    """Wrapper class for the NewsApiClient."""

    def __init__(self, api_key: str, language: str = "en"):
        self.api = NewsApiClient(api_key=api_key)
        self.language = language

    def get_everything_by_keyword(self, keywords: List[str] | str, sort_by: str = "relevancy") -> List[Dict]:
        if isinstance(keywords, list):
            keywords = ",".join(keywords)
        print(f"Sourcing everything related to `{keywords}` sorted by `{sort_by}`.")
        params = dict(
            q=keywords,
            language=self.language,
            sort_by=sort_by,
            page=2,
        )
        articles = self.api.get_everything(**params)
        print(f"Sourced {articles['totalResults']} articles.")
        return articles["articles"]

    def get_top_headlines(self, keywords: List[str] | str, country: str, sources: List[str] | str | None) -> List[Dict]:
        if isinstance(keywords, list):
            keywords = ",".join(keywords)
        print(f"Sourcing headlines for `{country}` using {sources if sources else 'all sources'}")
        params = dict(
            q=keywords,
            language=self.language,
            country=country,
        )
        if isinstance(sources, list):
            sources = ",".join(sources)
        if sources is not None:
            params["sources"] = sources
        return self.api.get_top_headlines(**params)
