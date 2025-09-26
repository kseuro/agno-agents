# Arxiv Q&A

⚠️ Under Construction

An agent that can utilize information retrieved from [arXiv](https://arxiv.org/) and construct an action plan.

The MO is to find a common theme among the N most recently posted articles, under the assumption that
current research methods and directions will be captured to varying degrees by each of the publications.
We then want to synthesize that information in a cohesive whole that a researcher could use to quickly
get up to speed on the state-of-the-art, find a new or complimentary research direction, or both.

For example: A search of arXiv shows that methods A and B are currently the dominant trend in a certain area of research. We'll take the N associated articles and do the following:

1. Synthesize a high-level overview of the publications that explains common research objectives and how methods A and B are being applied towards each goal.
   1. Example: publication 1 uses A to achieve X and B to achieve Y, while publication 2 also uses A to achieve X but modifed B slightly to achieve Z.

2. Synthesize information about research and method commonalities
   1. Example: publications 1, 2, and 4 all use method A in the same manner to achieve/prove/explore ...
   2. Example: all of the publications utilize method B in the same manner in order to ...

3. Synthesize information about research and method differences
   1. Example: publication 3 uses method A in a manner that is distinct form the others in that ...
   2. Example: publications 1, 2, and 4 use method A to achieve (objective), while publication 3 attempts to achieve ...

TODO: For each key idea, using the associated documents, create a single summarized document.

TODO: Search the arxiv for information related to the objective. Five articles per

TODO: For each article, distill an actionable summary.

- Can the method / result in the paper be replicated from publicly available data?
- Can the method / model be run without the use of high-end hardware (e.g. GPUs,TPUs)?

TODO: Use the summary information to rank the articles based on their relevance to the objective.

TODO: Using the most relevant articles, generate three quick prototype ideas for which we'll build an MVP

- For each prototype, provide information on how we would sanity check or benchmark the method.

TODO: For each prototype, create a brief presentation outline that could be used to present each MVP to a journal club

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
