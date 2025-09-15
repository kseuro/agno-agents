# Arxiv Q&A

⚠️ Under Construction

An agent that can retrieve information from [arxiv](https://arxiv.org/) and answer user questions via local RAG.

## Usage

### Vector Database

Install [Docker](https://docs.docker.com/get-started/get-docker/) on you system, then start an instance of the required vector database by running:

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

### Queries

TODO
