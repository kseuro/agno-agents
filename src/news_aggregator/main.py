import os
import argparse
from pathlib import Path
from textwrap import dedent
from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.workflow.v2.types import WorkflowExecutionInput
from agno.workflow.v2.workflow import Workflow
from pydantic import BaseModel, Field
from dotenv import dotenv_values
from typing import List, Dict, Any

environment_config = dotenv_values(".env")
GEMINI_API_KEY = environment_config.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY"))
if not GEMINI_API_KEY:
    raise ValueError("Set the `GEMINI_API_KEY`")
MODEL_ID: str = "gemini-2.0-flash-lite"


class NewsRequest(BaseModel):
    keywords: List[str]
    n_articles: int | None = 2


class NewsStory(BaseModel):
    author_name: str = Field(..., description="The name of a story's author or authors.")
    publication_outlet: str = Field(..., description="Which outlet published the news story.")
    story_url: str = Field(..., description="The URL of the story.")
    summary: str = Field(..., description="A one paragraph summary of the story along with key points.")


class NewsStories(BaseModel):
    stories: List[NewsStory] = Field(..., description="A collection of news stories.")


class Analysis(BaseModel):
    analysis: str = Field(..., description="Analysis of a collection of news stories.")


def get_command_line_args() -> Dict[str, Any]:
    parser = argparse.ArgumentParser(description="News analysis workflow")
    parser.add_argument(
        "-k",
        "--keyword",
        "--keywords",
        action="append",
        help="Keyword to search for. Repeat the flag to add multiple (e.g., -k nvidia -k 'artificial intelligence'). "
        "Alternatively, pass a comma-separated list in a single flag.",
    )
    parser.add_argument(
        "-n",
        "--n-articles",
        type=int,
        default=None,
        help="Number of articles to gather.",
    )
    args = parser.parse_args()

    # Resolve keywords
    keywords: List[str]
    if args.keyword:
        parts: List[str] = []
        for item in args.keyword:
            parts.extend([p.strip() for p in item.split(",") if p.strip()])
        keywords = parts
    else:
        raw = input("Enter keywords (comma-separated): ").strip()
        keywords = [k.strip() for k in raw.split(",") if k.strip()]

    if not args.n_articles:
        raw = input("Enter the number of articles to search for: ").strip()
        n_articles = int(raw)
        if n_articles <= 0:
            print("The number of articles must be greater than zero, defaulting to 2.")
            n_articles = 2
        return {"keywords": keywords, "n_articles": n_articles}

    return {"keywords": keywords, "n_articles": args.n_articles}


def news_workflow_execution_function(workflow: Workflow, *, execution_input: WorkflowExecutionInput):

    assert isinstance(execution_input.message, NewsRequest), "`execution_input.message` must be a `NewsRequest`"

    # -- Extract required inputs --
    required = execution_input.message
    keywords = " ".join(required.keywords)
    n_articles = required.n_articles

    assert n_articles and n_articles > 0, "Number of articles `n_articles` must be positive."

    print(f"Running workflow: {workflow.name}")

    # --- Gather the news ---
    print(f"Gathering {n_articles} news related to: {', '.join(required.keywords)}")
    news_gathering = Agent(
        name="news_gathering",
        model=Gemini(id=MODEL_ID, api_key=GEMINI_API_KEY),
        tools=[DuckDuckGoTools(search=True, news=True)],
        role="You are an experienced news gathering agent who scours the internet looking for the best stories.",
        instructions=[
            "Gather the following information:",
            "Author Name",
            "Publication Outlet",
            "Story URL",
            "A concise one parapgraph summary of the story along with key points",
        ],
        response_model=NewsStories,
    )
    n_stories = "the top story" if n_articles == 1 else f"{n_articles} stories"
    prompt = dedent(
        f"""
        Search the web for {n_stories} related to the following keywords:
        {keywords}
        """
    )
    news_stories = news_gathering.run(prompt)

    # --- Analyze the news ---
    print("Analyzing the news.")
    news_analyst = Agent(
        name="news_analyst",
        model=Gemini(id=MODEL_ID, api_key=GEMINI_API_KEY),
        role="You are a seasoned information analyst who is deft at synthesizing information",
        instructions=[
            "A junior news gathering agent will provide you with summaries of current news stories",
            "Use these news stories to generate a meta-analysis that provides a brief overview of the salient details.",
            "Feel free to search the web for any additonal context or information that might enrich the analysis",
            "Write the analysis in markdown format to the local file system.",
        ],
        tools=[
            DuckDuckGoTools(search=True),
        ],
        response_model=Analysis,
    )
    news_stories = "\n\n".join([story.summary for story in news_stories.content.stories])
    news_prompt = dedent(
        f"""
    Review the information from the following news stories provided by the junior analyst and provide a
    two paragraph analysis of the impact, implications, opportunities, drawbacks or downsides, and any future research
    directions that might be spurred by what has been occurring in the news recently. If any of the preceeding analysis
    topics are not relevant to the subject matter, then omit them from your analysis.

    IMPORTANT: Format your response as markdown with a main heading "# Analysis: {keywords}" and include the analysis below it.

    News Stories:
    {news_stories}
    """  # noqa
    )
    response = news_analyst.run(news_prompt)

    # # -- Write the output file --
    analysis: str = response.content.analysis
    outfile_path = Path(__file__).absolute().parent
    outfile_name = f"{'-'.join(keywords.split(', '))}_analysis.md".replace(" ", "-")
    outfile = outfile_path / outfile_name
    print(f"Writing analysis to: {outfile.name}")
    outfile.write_text(analysis + "\n")

    return response


if __name__ == "__main__":
    args = get_command_line_args()
    print("News Aggregation".center(80, "-"))
    news_analysis_workflow = Workflow(
        name="news_analysis_workflow",
        description="Automated analysis of news related to keywords of the user's interest.",
        steps=news_workflow_execution_function,
    )
    analysis = news_analysis_workflow.run(NewsRequest(**args))
    [print("-" * 80) for _ in range(2)]
