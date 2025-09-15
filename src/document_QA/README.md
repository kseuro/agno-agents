# Document Q&A

⚠️ Under Construction 🛠️

An agent that can answer questions about a specific document, such as a research paper, a legal document, or a product manual.

This projects showcases an agent's ability to work with unstructured data by leveraging `agno` knowledge and retieval features to load a document into a vector store and allow the agent to search for necessary documentation.

## Usage

### Vector Database

Start an instance of the required vector database by running:

```shell
docker run -d \
  -e POSTGRES_DB=ai \
  -e POSTGRES_USER=ai \
  -e POSTGRES_PASSWORD=ai \
  -e PGDATA=/var/lib/postgresql/data/pgdata \
  -v pgvolume:/var/lib/postgresql/data \
  -p 5532:5432 \
  --name pgvector \
  agnohq/pgvector:16
```
