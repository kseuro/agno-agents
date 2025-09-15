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
