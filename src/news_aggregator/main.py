# from agno.agent import Agent
# from agno.models.google import Gemini
# from agno.tools.duckduckgo import DuckDuckGoTools
# from agno.storage.sqlite import SqliteStorage
# from pydantic import BaseModel, Field

import os
import sys
from dotenv import dotenv_values
from typing import List
from src.news_aggregator.database import DataBase
from src.news_aggregator.news import NewsAPI

# TODO: Build off of this framework:
# https://github.com/agno-agi/agno/blob/main/cookbook/workflows/hackernews_reporter.py


if __name__ == "__main__":
    which: str = "everything"  # TODO: headlines, both
    keywords: List[str] | str = "nvidia"
    language: str = "en"
    sort_by: str = "relevancy"
    n_articles: int | None = 10

    environment_config = dotenv_values(".env")
    GEMINI_API_KEY = environment_config.get("GEMINI_API_KEY", None)
    NEWS_API_KEY = environment_config.get("NEWS_API_KEY", None)

    if not NEWS_API_KEY:
        NEWS_API_KEY = os.getenv("NEWS_API_KEY")
        sys.exit("Please set the `NEWS_API_KEY`.")

    # TODO: Implement gemini checks (provider, model, etc)
    # if not GEMINI_API_KEY:
    #     sys.exit("Please set the `GEMINI_API_KEY`.")
    # GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    # model_id = "gemini-2.0-flash-lite"

    database = DataBase()
    cached = database.get_cached_articles(which, keywords)
    if cached is not None:
        articles = cached
        print(f"Retrieved {len(articles)} articles from cache for ({which},{keywords}) combination")
    else:
        newsapi = NewsAPI(api_key=NEWS_API_KEY, language=language)
        if which == "everything" and keywords:  # take a look at just the news for these keywords
            articles = newsapi.get_everything_by_keyword(keywords=keywords)
            articles = articles[:n_articles]
            database.set_cached_articles(which, keywords, articles)
        elif which == "headlines":
            # TODO: aggregate the top headlines and generate a report
            print("`headlines` not yet implemented.")
        elif which == "all":
            print("`all` aggregation not yet implemented.")
            # TODO: Generate a report about the top stories related to the provided keywords.
            # TODO: Generate a report about the top news stories happening right now.

    # TODO: Agent workflow here
