import os
from agno.agent import Agent
from agno.models.google import Gemini
from agno.knowledge.arxiv import ArxivKnowledgeBase
from agno.vectordb.pgvector import PgVector
from agno.embedder.google import GeminiEmbedder
from dotenv import dotenv_values

os.environ["AGNO_LOG_LEVEL"] = "DEBUG"

environment_config = dotenv_values(".env")

db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"

GEMINI_API_KEY = environment_config.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY"))
if not GEMINI_API_KEY:
    raise ValueError("Set the `GEMINI_API_KEY`")
MODEL_ID: str = "gemini-2.0-flash-lite"

# Setup the vector database
vector_db = PgVector(table_name="arxiv_db", db_url=db_url, embedder=GeminiEmbedder(api_key=GEMINI_API_KEY))

# Provide queries and vector_db to the knowledge base
knowledge = ArxivKnowledgeBase(
    queries=["machine learning protein design", "machine learning antibody design"],
    vector_db=vector_db,
    num_documents=10,
)
try:
    knowledge.load(recreate=False, upsert=True)
    print("Knowledge load completed.")
except Exception as e:
    import traceback

    print(f"Knowledge load failed: {e}")
    traceback.print_exc()
    raise

test = knowledge.search("computational protein design", num_documents=5)
print(f"KB search returned {len(test)} docs.")

agent = Agent(
    name="arxiv_agent",
    model=Gemini(id=MODEL_ID, api_key=GEMINI_API_KEY),
    knowledge=knowledge,
    search_knowledge=True,
    add_references=True,
    retries=3,  # total attempts = retries + 1
    delay_between_retries=2,  # seconds
    exponential_backoff=True,
)
response = agent.print_response(
    "What are some of the state of the art methods in computational protein design?",
    markdown=True,
)

# TODO: Provide a research objective (e.g. I want to find the best methods for protein docking)
# TODO: Use an agent to generate a list of queries that are relevant to this objective
# TODO: Search the arxiv for information related to the objective. Five articles per
# TODO: For each article, distill an actionable summary.
#       - Can the method / result in the paper be replicated from publicly available data?
#       - Can the method / model be run without the use of high-end hardware (e.g. GPUs,TPUs)?
# TODO: Use the summary information to rank the articles based on their relevance to the objective.
# TODO: Using the most relevant articles, generate three quick prototype ideas for which we'll build an MVP
#       - For each prototype, provide information on how we would sanity check or benchmark the method.
# TODO: For each prototype, create a brief presentation outline that could be used to present each MVP to a journal club
