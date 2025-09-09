from textwrap import dedent
from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools.duckduckgo import DuckDuckGoTools
from pydantic import BaseModel, Field
from dotenv import dotenv_values
from typing import List


class NewsStory(BaseModel):
    author_name: str = Field(..., description="The name of a story's author or authors.")
    publication_outlet: str = Field(..., description="Which outlet published the news story.")
    story_url: str = Field(..., description="The URL of the story.")
    summary: str = Field(..., description="A summary of the story along with key points.")


class NewsStories(BaseModel):
    stories: List[NewsStory] = Field(..., description="A collection of news stories.")


class Analysis(BaseModel):
    analysis: str = Field(..., description="Analysis of a collection of news stories.")


if __name__ == "__main__":
    n_articles: int | None = 2

    environment_config = dotenv_values(".env")
    GEMINI_API_KEY = environment_config.get("GEMINI_API_KEY", None)
    if not GEMINI_API_KEY:
        raise ValueError("Set the `GEMINI_API_KEY`")
    keywords: List[str] = ["nvidia", "artificial intelligence", "business"]
    model_id: str = "gemini-2.0-flash-lite"

    # --- Gather the news ---
    print(f"Gathering news related to: {' '.join(keywords)}")
    news_gathering = Agent(
        name="news_gathering",
        model=Gemini(id=model_id, api_key=GEMINI_API_KEY),
        tools=[DuckDuckGoTools(search=True, news=True)],
        role="You are an experienced news gathering agent who scours the internet looking for the best stories.",
        instructions=[
            "Gather the following information:",
            "Author Name",
            "Publication Outlet",
            "Story URL",
            "A summary of the story along with key points",
        ],
        response_model=NewsStories,
    )
    n_stories = "the top story" if n_articles == 1 else f"{n_articles} stories"
    prompt = dedent(
        f"""
    Search the web for {n_stories} related to the following keywords:
    {', '.join(keywords)}
    """
    )
    news_stories = news_gathering.run(prompt)

    # --- Analyze the news ---
    print("Analyzing the news.")
    news_analyst = Agent(
        name="news_analyst",
        model=Gemini(id=model_id, api_key=GEMINI_API_KEY),
        role=dedent(
            """
        You are a seasoned information analyst who is deft at the task of synthesizing information
        from multiple sources into a coherent narrative. A junior news gathering agent will provide you with summaries
        of current news stories from which you'll generate the meta-analysis. Feel free to search the web for any
        additional context or information that might enrich your analysis.
        """
        ),
        tools=[DuckDuckGoTools(search=True)],
        response_model=Analysis,
    )
    news_stories = "\n\n".join([story.summary for story in news_stories.content.stories])
    news_prompt = dedent(
        f"""
    Review the information from the following news stories provided by the junior analyst and provide a
    two paragraph analysis of the impact, implications, opportunities, drawbacks or downsides, and any future research
    directions that might be spurred by what has been occurring in the news recently. If any of the preceeding analysis
    topics are not relevant to the subject matter, then omit them from your analysis.

    News Stories:
    {news_stories}
    """
    )
    analysis = news_analyst.run(news_prompt)
    print(analysis.content)
