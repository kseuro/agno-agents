# AI Code Contributor

This agent's high-level goal is to act like a junior developer by autonomously analyzing a `git`, identifying useful next steps, implementing them, and submitting atomic commits for human review.

This kind of task can be broken down using the core concepts of the `agno` agent framework like [Instructions](https://docs.agno.com/examples/concepts/others/instructions), [Tools](https://docs.agno.com/examples/concepts/tools/search/arxiv), and [Reasoning Loops](https://docs.agno.com/examples/concepts/reasoning/agents/basic-cot).

## Tooling

`GitManager`

`GitHubManager`

## Roadmap

This agent will be developed in three stages of increasing complexity:

[ ] V1: An agent that only analyzes code and provides high level summaries thereof.

[ ] V2: An agent that suggests next steps but doesn't implement them.

[ ] V3: An agent that analyzes code, generates code, and produces a PR for human review.
